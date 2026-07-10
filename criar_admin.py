"""
Script para criar o primeiro administrador e gerar o link de configuracao do TOTP.
Execute uma vez:  python criar_admin.py
"""
import sys
from app.database import engine, SessionLocal, Base
from app.models import Admin
from app import auth as auth_service

Base.metadata.create_all(bind=engine)

email = input("E-mail do administrador: ").strip()
senha = input("Senha: ").strip()

if not email or not senha:
    print("E-mail e senha sao obrigatorios.")
    sys.exit(1)

db = SessionLocal()

existente = db.query(Admin).filter(Admin.email == email).first()
if existente:
    print(f"Administrador com e-mail '{email}' ja existe.")
    db.close()
    sys.exit(1)

admin = Admin(
    email=email,
    senha_hash=auth_service.hash_senha(senha),
    totp_secret=auth_service.gerar_totp_secret(),
    totp_ativo=False,
)
db.add(admin)
db.commit()
db.refresh(admin)

token = auth_service.criar_token({"sub": admin.id})

print()
print("=" * 60)
print("Administrador criado com sucesso!")
print()
print("Acesse o link abaixo para configurar o Google Authenticator:")
print(f"  http://localhost:8000/admin/setup-totp?token={token}")
print()
print("Apos escanear o QR Code e confirmar, faca login normalmente em:")
print("  http://localhost:8000/admin/login")
print("=" * 60)

db.close()
