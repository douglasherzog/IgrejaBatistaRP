# Igreja Batista Nova Vida – Rio Pardo/RS

Site institucional com área administrativa para gestão de membros e controle financeiro.

## Tecnologias

- **Backend:** Python 3.11+ / FastAPI / SQLAlchemy
- **Banco:** SQLite (desenvolvimento) / PostgreSQL (produção no VPS)
- **Autenticação:** JWT + TOTP (Google Authenticator)
- **Frontend:** HTML / Tailwind CSS / Jinja2

## Instalação

```bash
cd IgrejaBatistaRP
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

## Configuração

```bash
cp .env.example .env
# Edite o .env com suas configurações
```

## Primeiro acesso

Crie o administrador e configure o Google Authenticator:

```bash
python criar_admin.py
```

Siga o link gerado para escanear o QR Code com o Google Authenticator.

## Executar

```bash
uvicorn app.main:app --reload
```

Acesse em: http://localhost:8000

## Logo

Coloque o arquivo da logo em: `static/img/logo.png`

## Estrutura

```
IgrejaBatistaRP/
├── app/
│   ├── main.py          # Aplicação FastAPI
│   ├── database.py      # Conexão banco de dados
│   ├── models.py        # Modelos SQLAlchemy
│   ├── auth.py          # Autenticação JWT + TOTP
│   └── routers/
│       ├── publico.py   # Site público
│       ├── auth.py      # Login/logout
│       ├── membros.py   # CRUD de membros
│       ├── caixa.py     # Controle financeiro
│       └── admin_dashboard.py
├── templates/
│   ├── base.html        # Layout site público
│   ├── publico/         # Páginas públicas
│   └── admin/           # Área administrativa
├── static/
│   └── img/             # Coloque logo.png aqui
├── criar_admin.py        # Script de setup inicial
└── requirements.txt
```

## Deploy no VPS (Hetzner)

1. Instale PostgreSQL, Python 3.11, Nginx
2. Configure `DATABASE_URL` no `.env` com a string do PostgreSQL
3. Use `gunicorn` ou `uvicorn` com systemd service
4. Configure Nginx como proxy reverso
```
