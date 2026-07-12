from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
import pandas as pd
import io
from app.database import get_db
from app.models import Membro, Lancamento, TipoLancamento, Admin
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/importar", response_class=HTMLResponse)
def pagina_importar(request: Request, admin: Admin = Depends(get_admin_atual)):
    return templates.TemplateResponse("admin/importar.html", {
        "request": request
    })


@router.post("/admin/importar")
async def importar_dados(
    request: Request,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    if not arquivo.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Arquivo deve ser Excel (.xlsx, .xls) ou CSV")
    
    try:
        # Ler o arquivo
        content = await arquivo.read()
        
        if arquivo.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Processar os dados
        resultado = processar_planilha(df, db)
        
        return templates.TemplateResponse("admin/importar.html", {
            "request": request,
            "sucesso": True,
            "resultado": resultado
        })
        
    except Exception as e:
        return templates.TemplateResponse("admin/importar.html", {
            "request": request,
            "erro": str(e)
        })


def processar_planilha(df, db):
    resultado = {
        "membros_importados": 0,
        "lancamentos_importados": 0,
        "erros": [],
        "warnings": [],
        "colunas_encontradas": df.columns.tolist(),
        "total_linhas": len(df)
    }
    
    # Detectar colunas
    colunas = df.columns.tolist()
    colunas_lower = [col.lower().strip() for col in colunas]
    
    # Mostrar informações sobre a planilha
    print(f"Colunas encontradas: {colunas}")
    print(f"Total de linhas: {len(df)}")
    
    # Verificar se é uma planilha de membros
    membros_keywords = ['nome', 'nome completo', 'name', 'membro', 'membros']
    if any(keyword in ' '.join(colunas_lower) for keyword in membros_keywords):
        resultado.update(importar_membros(df, db))
    
    # Verificar se é uma planilha de lançamentos financeiros
    elif any(keyword in ' '.join(colunas_lower) for keyword in ['data', 'date', 'valor', 'value', 'lançamento', 'lancamento', 'caixa']):
        resultado.update(importar_lancamentos(df, db))
    
    else:
        resultado["erros"].append(f"Formato de planilha não reconhecido. Colunas encontradas: {', '.join(colunas)}")
    
    return resultado


def importar_membros(df, db):
    resultado = {"membros_importados": 0, "erros": [], "warnings": []}
    
    # Mapeamento de colunas
    col_map = {
        'nome': 'nome',
        'nome completo': 'nome',
        'name': 'nome',
        'sobrenome': 'sobrenome',
        'telefone': 'telefone',
        'phone': 'telefone',
        'email': 'email',
        'data nascimento': 'data_nascimento',
        'nascimento': 'data_nascimento',
        'data batismo': 'data_batismo',
        'batismo': 'data_batismo',
        'endereco': 'endereco',
        'bairro': 'bairro',
        'cidade': 'cidade',
        'estado': 'estado',
        'cep': 'cep',
        'observacoes': 'observacoes'
    }
    
    for index, row in df.iterrows():
        try:
            # Criar dicionário de dados do membro
            membro_data = {}
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in col_map and pd.notna(row[col]):
                    campo = col_map[col_lower]
                    valor = row[col]
                    
                    # Tratar datas
                    if campo in ['data_nascimento', 'data_batismo']:
                        if isinstance(valor, str):
                            try:
                                valor = datetime.strptime(valor, '%d/%m/%Y').date()
                            except:
                                try:
                                    valor = datetime.strptime(valor, '%Y-%m-%d').date()
                                except:
                                    valor = None
                        elif pd.notna(valor):
                            valor = pd.to_datetime(valor).date()
                    
                    membro_data[campo] = valor
            
            # Separar nome e sobrenome se não houver sobrenome
            if 'nome' in membro_data and 'sobrenome' not in membro_data:
                partes = membro_data['nome'].split()
                if len(partes) > 1:
                    membro_data['nome'] = partes[0]
                    membro_data['sobrenome'] = ' '.join(partes[1:])
            
            # Verificar se membro já existe
            if 'nome' in membro_data:
                existente = db.query(Membro).filter(
                    Membro.nome == membro_data['nome'],
                    Membro.sobrenome == membro_data.get('sobrenome', '')
                ).first()
                
                if existente:
                    resultado["warnings"].append(f"Membro {membro_data['nome']} {membro_data.get('sobrenome', '')} já existe")
                    continue
            
            # Criar membro
            membro = Membro(**membro_data)
            membro.ativo = True
            db.add(membro)
            resultado["membros_importados"] += 1
            
        except Exception as e:
            resultado["erros"].append(f"Erro na linha {index + 2}: {str(e)}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        resultado["erros"].append(f"Erro ao salvar: {str(e)}")
    
    return resultado


def importar_lancamentos(df, db):
    resultado = {"lancamentos_importados": 0, "erros": [], "warnings": []}
    
    # Mapeamento de colunas expandido
    col_map = {
        'data': 'data',
        'date': 'data',
        'dt': 'data',
        'data lancamento': 'data',
        'data do lançamento': 'data',
        'valor': 'valor',
        'value': 'valor',
        'vlr': 'valor',
        'valor (r$)': 'valor',
        'valor rs': 'valor',
        'descrição': 'descricao',
        'descricao': 'descricao',
        'description': 'descricao',
        'historico': 'descricao',
        'histórico': 'descricao',
        'categoria': 'categoria',
        'type': 'categoria',
        'tipo': 'categoria',
        'classificação': 'categoria',
        'classificacao': 'categoria',
        'membro': 'membro_nome',
        'dizimista': 'membro_nome',
        'nome do membro': 'membro_nome',
        'nome dizimista': 'membro_nome',
        'responsavel': 'membro_nome',
        'responsável': 'membro_nome'
    }
    
    # Obter todos os membros para busca
    membros = db.query(Membro).all()
    membro_map = {f"{m.nome} {m.sobrenome}".lower(): m for m in membros}
    
    for index, row in df.iterrows():
        try:
            # Criar dicionário de dados do lançamento
            lancamento_data = {}
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in col_map and pd.notna(row[col]):
                    campo = col_map[col_lower]
                    valor = row[col]
                    
                    # Tratar data
                    if campo == 'data':
                        if isinstance(valor, str):
                            try:
                                valor = datetime.strptime(valor, '%d/%m/%Y').date()
                            except:
                                try:
                                    valor = datetime.strptime(valor, '%Y-%m-%d').date()
                                except:
                                    valor = date.today()
                        elif pd.notna(valor):
                            valor = pd.to_datetime(valor).date()
                    
                    # Tratar valor
                    elif campo == 'valor':
                        if isinstance(valor, str):
                            # Remove espaços e símbolos monetários
                            valor_str = valor.strip().replace('R$', '').replace('$', '').replace(' ', '')
                            # Substitui vírgula por ponto para casas decimais, mas primeiro remove pontos de milhar
                            if ',' in valor_str and '.' in valor_str:
                                # Formato brasileiro: 1.234,56
                                valor_str = valor_str.replace('.', '').replace(',', '.')
                            elif ',' in valor_str:
                                # Formato simples: 123,56
                                valor_str = valor_str.replace(',', '.')
                            try:
                                valor = float(valor_str)
                            except ValueError:
                                valor = 0.0
                        else:
                            valor = float(valor) if pd.notna(valor) else 0.0
                    
                    # Tratar tipo
                    elif campo == 'tipo':
                        if isinstance(valor, str):
                            valor = valor.lower()
                            if valor in ['receita', 'despesa']:
                                lancamento_data['tipo'] = TipoLancamento(valor)
                            else:
                                # Se não for receita/despesa, inferir pela categoria
                                pass
                    
                    lancamento_data[campo] = valor
            
            # Inferir tipo pela categoria se não definido
            if 'tipo' not in lancamento_data and 'categoria' in lancamento_data:
                cat = lancamento_data['categoria'].lower()
                receitas = ['dízimo', 'oferta', 'doação', 'especial']
                if any(r in cat for r in receitas):
                    lancamento_data['tipo'] = TipoLancamento.receita
                else:
                    lancamento_data['tipo'] = TipoLancamento.despesa
            
            # Encontrar membro
            if 'membro_nome' in lancamento_data:
                nome_membro = lancamento_data.pop('membro_nome').lower()
                if nome_membro in membro_map:
                    lancamento_data['membro_id'] = membro_map[nome_membro].id
                else:
                    resultado["warnings"].append(f"Membro '{lancamento_data.get('membro_nome')}' não encontrado")
            
            # Criar lançamento
            lancamento = Lancamento(**lancamento_data)
            db.add(lancamento)
            resultado["lancamentos_importados"] += 1
            
        except Exception as e:
            resultado["erros"].append(f"Erro na linha {index + 2}: {str(e)}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        resultado["erros"].append(f"Erro ao salvar: {str(e)}")
    
    return resultado
