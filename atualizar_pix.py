from app.database import SessionLocal
from app.models import ConfiguracaoSite

db = SessionLocal()

valores = {
    "pix_chave": "21093882000157",
    "pix_tipo": "CNPJ",
    "banco_nome": "CRESOL",
    "banco_agencia": "5617",
    "banco_conta": "22213-5",
    "banco_tipo_conta": "Conta Corrente",
    "banco_titular": "Igreja Batista Independente Nova Vida",
}

for chave, valor in valores.items():
    cfg = db.query(ConfiguracaoSite).filter_by(chave=chave).first()
    if cfg:
        cfg.valor = valor
    else:
        db.add(ConfiguracaoSite(chave=chave, valor=valor))
    print(f"{chave}: {valor}")

db.commit()
db.close()
print("Configurações salvas.")
