from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ConfiguracaoSite, Culto, Admin
from app.auth import get_admin_atual

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Lista de configurações organizadas por seção
SECOES = {
    "Geral": {
        "icon": "⚙️",
        "campos": [
            ("nome_igreja", "Nome da Igreja", "text", "Igreja Batista Independente Nova Vida", "Nome completo da igreja. Aparece no topo do site e no rodapé."),
            ("sigla_igreja", "Sigla", "text", "IBINOVI", "Sigla ou nome curto da igreja. Ex: IBINOVI."),
            ("cidade_estado", "Cidade/Estado", "text", "Rio Pardo – RS", "Cidade e estado onde a igreja está localizada."),
            ("ano_fundacao", "Ano de Fundação", "text", "", "Ano em que a igreja foi fundada. Opcional."),
        ],
    },
    "Home": {
        "icon": "🏠",
        "campos": [
            ("hero_subtitulo", "Subtítulo do Hero", "text", "Bem-vindo à", "Texto pequeno que aparece acima do título principal na página inicial."),
            ("hero_titulo", "Título do Hero", "text", "Igreja Batista Independente Nova Vida", "Título grande em destaque no topo da página inicial."),
            ("hero_sigla", "Sigla no Hero", "text", "IBINOVI", "Sigla exibida abaixo do título principal."),
            ("hero_cidade", "Cidade no Hero", "text", "RIO PARDO – RIO GRANDE DO SUL", "Localização exibida abaixo da sigla, em letras maiúsculas."),
            ("hero_mensagem", "Mensagem de boas-vindas", "textarea", "Um lugar de fé, comunhão e esperança. Você é muito bem-vindo!", "Mensagem de boas-vindas que aparece abaixo do título. Seja acolhedor!"),
            ("card1_titulo", "Card 1 - Título", "text", "Cultos Semanais", "Título do primeiro card de destaque (abaixo do hero)."),
            ("card1_texto", "Card 1 - Texto", "textarea", "Pregação da Palavra de Deus todos os domingos e durante a semana.", "Descrição do primeiro card. Texto curto e direto."),
            ("card1_link", "Card 1 - Link", "text", "/cultos", "Página para onde o link do card 1 aponta. Use: /cultos, /sobre, /eventos, /contato"),
            ("card1_link_texto", "Card 1 - Texto do Link", "text", "Ver horários →", "Texto clicável do link do card 1."),
            ("card2_titulo", "Card 2 - Título", "text", "Comunidade", "Título do segundo card de destaque."),
            ("card2_texto", "Card 2 - Texto", "textarea", "Uma família unida em amor, fé e serviço ao próximo.", "Descrição do segundo card."),
            ("card2_link", "Card 2 - Link", "text", "/sobre", "Página para onde o link do card 2 aponta."),
            ("card2_link_texto", "Card 2 - Texto do Link", "text", "Saiba mais →", "Texto clicável do link do card 2."),
            ("card3_titulo", "Card 3 - Título", "text", "Eventos", "Título do terceiro card de destaque."),
            ("card3_texto", "Card 3 - Texto", "textarea", "Confraternizações, conferências e eventos especiais ao longo do ano.", "Descrição do terceiro card."),
            ("card3_link", "Card 3 - Link", "text", "/eventos", "Página para onde o link do card 3 aponta."),
            ("card3_link_texto", "Card 3 - Texto do Link", "text", "Ver eventos →", "Texto clicável do link do card 3."),
            ("versiculo_texto", "Versículo - Texto", "textarea", "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.", "Texto do versículo exibido na seção escura da página inicial. Pode incluir aspas."),
            ("versiculo_ref", "Versículo - Referência", "text", "João 3:16", "Referência bíblica do versículo. Ex: João 3:16, Salmos 23:1."),
        ],
    },
    "Sobre": {
        "icon": "📖",
        "campos": [
            ("sobre_titulo", "Título da Página", "text", "Sobre a Igreja", "Título que aparece no topo da página Sobre."),
            ("sobre_subtitulo", "Subtítulo", "text", "Conheça nossa história e missão", "Subtítulo da página Sobre, logo abaixo do título."),
            ("sobre_historia_titulo", "Título - Nossa História", "text", "Nossa História", "Título da seção de história da igreja."),
            ("sobre_historia_texto", "Texto - Nossa História", "textarea", "A Igreja Batista Independente Nova Vida (IBINOVI) de Rio Pardo foi fundada com o propósito de proclamar o evangelho de Jesus Cristo e edificar uma comunidade de fé sólida no município de Rio Pardo – RS. Ao longo dos anos, Deus tem abençoado nossa congregação com crescimento, comunhão e serviço ao próximo.", "Texto contando a história da igreja. Pode ser longo."),
            ("sobre_missao_titulo", "Título - Nossa Missão", "text", "Nossa Missão", "Título da seção de missão."),
            ("sobre_missao_texto", "Texto - Nossa Missão", "textarea", "Proclamar o Evangelho de Jesus Cristo, discipular crentes, servir a comunidade e plantar igrejas, tudo para a glória de Deus.", "Texto descrevendo a missão da igreja."),
            ("sobre_visao_titulo", "Título - Nossa Visão", "text", "Nossa Visão", "Título da seção de visão."),
            ("sobre_visao_texto", "Texto - Nossa Visão", "textarea", "Ser uma igreja relevante, comprometida com a Palavra de Deus, que transforma vidas e impacta a cidade de Rio Pardo e região.", "Texto descrevendo a visão da igreja."),
            ("sobre_cremos_titulo", "Título - O que Cremos", "text", "O que Cremos", "Título da seção de crenças."),
            ("sobre_cremos_lista", "Crenças (uma por linha)", "textarea", "Na inspiração e autoridade da Bíblia Sagrada\nNa Trindade: Pai, Filho e Espírito Santo\nNa salvação pela graça, mediante a fé em Jesus Cristo\nNo batismo de crentes por imersão\nNa segunda vinda de Cristo", "Escreva cada crença em uma linha separada. Cada linha vira um item na lista."),
        ],
    },
    "Contato": {
        "icon": "📞",
        "campos": [
            ("contato_titulo", "Título da Página", "text", "Entre em Contato", "Título que aparece no topo da página de Contato."),
            ("contato_subtitulo", "Subtítulo", "text", "Estamos aqui para recebê-lo", "Subtítulo da página de Contato."),
            ("endereco_rua", "Endereço - Rua", "text", "Rua Nicolau Matte Pessoa de Brum, 158", "Rua e número da igreja."),
            ("endereco_bairro", "Endereço - Bairro", "text", "Bairro Higino Leitão – Rio Pardo/RS", "Bairro, cidade e estado da igreja."),
            ("telefone", "Telefone", "text", "(51) 99726-7850", "Telefone de contato da igreja. Ex: (51) 99726-7850"),
            ("whatsapp_link", "Link do WhatsApp", "text", "https://wa.me/5551997267850", "Link completo do WhatsApp. Formato: https://wa.me/55 + número (só dígitos, sem espaços ou parênteses)."),
            ("email", "E-mail", "text", "ibnvriopardo@gmail.com", "Endereço de e-mail de contato da igreja."),
            ("facebook_link", "Link do Facebook", "text", "https://www.facebook.com/ibnvrp", "URL completa da página do Facebook."),
            ("facebook_texto", "Texto do Facebook", "text", "Facebook: /ibnvrp", "Texto exibido no link do Facebook. Ex: Facebook: /ibnvrp"),
            ("instagram_link", "Link do Instagram", "text", "https://www.instagram.com/ibinovi_rp/", "URL completa do perfil do Instagram."),
            ("instagram_texto", "Texto do Instagram", "text", "Instagram: @ibinovi_rp", "Texto exibido no link do Instagram. Ex: Instagram: @ibinovi_rp"),
            ("maps_embed", "Google Maps - URL do embed (src do iframe)", "textarea", "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3473.2!2d-52.3864082!3d-29.983285!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x951b5d32bfce9c5b%3A0xcf1e16321d0d8a49!2sIgreja%20Batista%20Nova%20Vida!5e0!3m2!1spt!2sbr!4v1", "Cole aqui a URL do embed do Google Maps. Para obter: vá no Google Maps > Compartilhar > Incorporar mapa > copie o conteúdo do src do iframe."),
        ],
    },
}


def get_config(db: Session, chave: str, default: str = "") -> str:
    cfg = db.query(ConfiguracaoSite).filter(ConfiguracaoSite.chave == chave).first()
    return cfg.valor if cfg else default


def set_config(db: Session, chave: str, valor: str):
    cfg = db.query(ConfiguracaoSite).filter(ConfiguracaoSite.chave == chave).first()
    if cfg:
        cfg.valor = valor
    else:
        db.add(ConfiguracaoSite(chave=chave, valor=valor))


def get_all_configs(db: Session) -> dict:
    configs = {}
    for cfg in db.query(ConfiguracaoSite).all():
        configs[cfg.chave] = cfg.valor or ""
    # Preencher defaults
    for secao_data in SECOES.values():
        for campo in secao_data["campos"]:
            chave = campo[0]
            default = campo[3]
            if chave not in configs:
                configs[chave] = default
    return configs


@router.get("/admin/site", response_class=HTMLResponse)
def editar_site(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    configs = get_all_configs(db)
    cultos = db.query(Culto).order_by(Culto.ordem).all()
    return templates.TemplateResponse("admin/site/editar.html", {
        "request": request,
        "secoes": SECOES,
        "configs": configs,
        "cultos": cultos,
    })


@router.post("/admin/site/salvar-configs")
async def salvar_configs(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    form_data = await request.form()
    for chave, valor in form_data.items():
        if chave.startswith("cfg_"):
            real_chave = chave[4:]
            set_config(db, real_chave, valor)
    db.commit()
    return RedirectResponse(url="/admin/site?ok=1", status_code=302)


# CRUD Cultos
@router.post("/admin/site/culto/novo")
async def novo_culto(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    form = await request.form()
    culto = Culto(
        dia_semana=form.get("dia_semana", ""),
        horario=form.get("horario", ""),
        nome=form.get("nome", ""),
        descricao=form.get("descricao", "") or None,
        destaque=form.get("destaque") == "on",
        ordem=int(form.get("ordem", 0)),
        ativo=form.get("ativo") != "off",
    )
    db.add(culto)
    db.commit()
    return RedirectResponse(url="/admin/site#cultos", status_code=302)


@router.post("/admin/site/culto/{id}/editar")
async def editar_culto(
    id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    culto = db.query(Culto).filter(Culto.id == id).first()
    if not culto:
        raise HTTPException(status_code=404)
    form = await request.form()
    culto.dia_semana = form.get("dia_semana", "")
    culto.horario = form.get("horario", "")
    culto.nome = form.get("nome", "")
    culto.descricao = form.get("descricao", "") or None
    culto.destaque = form.get("destaque") == "on"
    culto.ordem = int(form.get("ordem", 0))
    culto.ativo = form.get("ativo") != "off"
    db.commit()
    return RedirectResponse(url="/admin/site#cultos", status_code=302)


@router.post("/admin/site/culto/{id}/excluir")
def excluir_culto(
    id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_admin_atual)
):
    culto = db.query(Culto).filter(Culto.id == id).first()
    if not culto:
        raise HTTPException(status_code=404)
    db.delete(culto)
    db.commit()
    return RedirectResponse(url="/admin/site#cultos", status_code=302)
