from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, Boolean, Enum
from sqlalchemy.sql import func
import enum
from app.database import Base


class TipoLancamento(str, enum.Enum):
    receita = "receita"
    despesa = "despesa"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    totp_secret = Column(String(64), nullable=True)
    totp_ativo = Column(Boolean, default=False)
    criado_em = Column(DateTime, server_default=func.now())


class Membro(Base):
    __tablename__ = "membros"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    sobrenome = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=True)
    data_batismo = Column(Date, nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    endereco = Column(String(255), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    observacoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Lancamento(Base):
    __tablename__ = "lancamentos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoLancamento), nullable=False)
    categoria = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data = Column(Date, nullable=False)
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now())
