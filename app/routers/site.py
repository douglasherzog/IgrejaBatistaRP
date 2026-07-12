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
            ("nome_igreja", "Nome da Igreja", "text", "Igreja Batista Independente Nova Vida"),
            ("sigla_igreja", "Sigla", "text", "IBINOVI"),
            ("cidade_estado", "Cidade/Estado", "text", "Rio Pardo – RS"),
            ("ano_fundacao", "Ano de Fundação", "text", ""),
        ],
    },
    "Home": {
        "icon": "🏠",
        "campos": [
            ("hero_subtitulo", "Subtítulo do Hero", "text", "Bem-vindo à"),
            ("hero_titulo", "Título do Hero", "text", "Igreja Batista Independente Nova Vida"),
            ("hero_sigla", "Sigla no Hero", "text", "IBINOVI"),
            ("hero_cidade", "Cidade no Hero", "text", "RIO PARDO – RIO GRANDE DO SUL"),
            ("hero_mensagem", "Mensagem de boas-vindas", "textarea", "Um lugar de fé, comunhão e esperança. Você é muito bem-vindo!"),
            ("card1_titulo", "Card 1 - Título", "text", "Cultos Semanais"),
            ("card1_texto", "Card 1 - Texto", "textarea", "Pregação da Palavra de Deus todos os domingos e durante a semana."),
            ("card1_link", "Card 1 - Link", "text", "/cultos"),
            ("card1_link_texto", "Card 1 - Texto do Link", "text", "Ver horários →"),
            ("card2_titulo", "Card 2 - Título", "text", "Comunidade"),
            ("card2_texto", "Card 2 - Texto", "textarea", "Uma família unida em amor, fé e serviço ao próximo."),
            ("card2_link", "Card 2 - Link", "text", "/sobre"),
            ("card2_link_texto", "Card 2 - Texto do Link", "text", "Saiba mais →"),
            ("card3_titulo", "Card 3 - Título", "text", "Eventos"),
            ("card3_texto", "Card 3 - Texto", "textarea", "Confraternizações, conferências e eventos especiais ao longo do ano."),
            ("card3_link", "Card 3 - Link", "text", "/eventos"),
            ("card3_link_texto", "Card 3 - Texto do Link", "text", "Ver eventos →"),
            ("versiculo_texto", "Versículo - Texto", "textarea", "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna."),
            ("versiculo_ref", "Versículo - Referência", "text", "João 3:16"),
        ],
    },
    "Sobre": {
        "icon": "📖",
        "campos": [
            ("sobre_titulo", "Título da Página", "text", "Sobre a Igreja"),
            ("sobre_subtitulo", "Subtítulo", "text", "Conheça nossa história e missão"),
            ("sobre_historia_titulo", "Título - Nossa História", "text", "Nossa História"),
            ("sobre_historia_texto", "Texto - Nossa História", "textarea", "A Igreja Batista Independente Nova Vida (IBINOVI) de Rio Pardo foi fundada com o propósito de proclamar o evangelho de Jesus Cristo e edificar uma comunidade de fé sólida no município de Rio Pardo – RS. Ao longo dos anos, Deus tem abençoado nossa congregação com crescimento, comunhão e serviço ao próximo."),
            ("sobre_missao_titulo", "Título - Nossa Missão", "text", "Nossa Missão"),
            ("sobre_missao_texto", "Texto - Nossa Missão", "textarea", "Proclamar o Evangelho de Jesus Cristo, discipular crentes, servir a comunidade e plantar igrejas, tudo para a glória de Deus."),
            ("sobre_visao_titulo", "Título - Nossa Visão", "text", "Nossa Visão"),
            ("sobre_visao_texto", "Texto - Nossa Visão", "textarea", "Ser uma igreja relevante, comprometida com a Palavra de Deus, que transforma vidas e impacta a cidade de Rio Pardo e região."),
            ("sobre_cremos_titulo", "Título - O que Cremos", "text", "O que Cremos"),
            ("sobre_cremos_lista", "Crenças (uma por linha)", "textarea", "Na inspiração e autoridade da Bíblia Sagrada\nNa Trindade: Pai, Filho e Espírito Santo\nNa salvação pela graça, mediante a fé em Jesus Cristo\nNo batismo de crentes por imersão\nNa segunda vinda de Cristo"),
        ],
    },
    "Contato": {
        "icon": "📞",
        "campos": [
            ("contato_titulo", "Título da Página", "text", "Entre em Contato"),
            ("contato_subtitulo", "Subtítulo", "text", "Estamos aqui para recebê-lo"),
            ("endereco_rua", "Endereço - Rua", "text", "Rua Nicolau Matte Pessoa de Brum, 158"),
            ("endereco_bairro", "Endereço - Bairro", "text", "Bairro Higino Leitão – Rio Pardo/RS"),
            ("telefone", "Telefone", "text", "(51) 99726-7850"),
            ("whatsapp_link", "Link do WhatsApp", "text", "https://wa.me/5551997267850"),
            ("email", "E-mail", "text", "ibnvriopardo@gmail.com"),
            ("facebook_link", "Link do Facebook", "text", "https://www.facebook.com/ibnvrp"),
            ("facebook_texto", "Texto do Facebook", "text", "Facebook: /ibnvrp"),
            ("instagram_link", "Link do Instagram", "text", "https://www.instagram.com/ibinovi_rp/"),
            ("instagram_texto", "Texto do Instagram", "text", "Instagram: @ibinovi_rp"),
            ("maps_embed", "Google Maps - URL do embed (src do iframe)", "textarea", "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3473.2!2d-52.3864082!3d-29.983285!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x951b5d32bfce9c5b%3A0xcf1e16321d0d8a49!2sIgreja%20Batista%20Nova%20Vida!5e0!3m2!1spt!2sbr!4v1"),
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
        for chave, _, _, default in secao_data["campos"]:
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
