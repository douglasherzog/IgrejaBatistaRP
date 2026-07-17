from app.database import SessionLocal
from app.models import Culto

db = SessionLocal()
db.query(Culto).delete()
db.commit()

cultos = [
    Culto(dia_semana="Terça-feira", horario="19h30", nome="Terça do Despertar", descricao=None, destaque=False, ordem=1, ativo=True),
    Culto(dia_semana="Quarta-feira", horario="15h", nome="Reunião de Oração", descricao=None, destaque=False, ordem=2, ativo=True),
    Culto(dia_semana="Quinta-feira", horario="19h30", nome="Jovens New Life", descricao="Na casa do irmão Tiago Glashorester", destaque=False, ordem=3, ativo=True),
    Culto(dia_semana="Sexta-feira", horario="19h30", nome="Reunião de Oração", descricao=None, destaque=False, ordem=4, ativo=True),
    Culto(dia_semana="Domingo", horario="19h", nome="Culto de Celebração", descricao=None, destaque=True, ordem=5, ativo=True),
]
db.add_all(cultos)
db.commit()
print(f"{len(cultos)} cultos atualizados")
for c in cultos:
    print(f"  {c.id} | {c.dia_semana} | {c.horario} | {c.nome} | {c.descricao or '-'}")
db.close()
