from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, Text, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
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
    is_superadmin = Column(Boolean, default=False)
    criado_em = Column(DateTime, server_default=func.now())


class PermissaoAdmin(Base):
    __tablename__ = "permissoes_admin"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    area = Column(String(50), nullable=False)
    admin = relationship("Admin", backref="permissoes")


class AcessoLog(Base):
    __tablename__ = "acesso_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    email = Column(String(255), nullable=True)
    acao = Column(String(50), nullable=False)
    path = Column(String(255), nullable=True)
    ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    detalhes = Column(Text, nullable=True)
    criado_em = Column(DateTime, server_default=func.now())


class DispositivoOtpExento(Base):
    __tablename__ = "dispositivos_otp_exentos"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    fingerprint = Column(String(128), nullable=False)
    nome = Column(String(100), nullable=True)
    ip = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())

    admin = relationship("Admin", backref="dispositivos_otp_exentos")


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
    membro_id = Column(Integer, ForeignKey("membros.id"), nullable=True)
    membro = relationship("Membro", backref="lancamentos")
    criado_em = Column(DateTime, server_default=func.now())


class ConfiguracaoSite(Base):
    __tablename__ = "configuracoes_site"

    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=True)
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Culto(Base):
    __tablename__ = "cultos"

    id = Column(Integer, primary_key=True, index=True)
    dia_semana = Column(String(50), nullable=False)
    horario = Column(String(20), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(255), nullable=True)
    destaque = Column(Boolean, default=False)
    ordem = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    data = Column(Date, nullable=False)
    horario = Column(String(20), nullable=True)
    local = Column(String(255), nullable=True)
    imagem_url = Column(String(500), nullable=True)
    destaque = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    youtube_url = Column(String(500), nullable=False)
    youtube_id = Column(String(50), nullable=True)
    destaque = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())
    atualizado_em = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PedidoOracao(Base):
    __tablename__ = "pedidos_oracao"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    pedido = Column(Text, nullable=False)
    publico = Column(Boolean, default=False)
    status = Column(String(20), default="novo")
    criado_em = Column(DateTime, server_default=func.now())


class InscricaoEvento(Base):
    __tablename__ = "inscricoes_evento"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    criado_em = Column(DateTime, server_default=func.now())
    evento = relationship("Evento", backref="inscricoes")


class Foto(Base):
    __tablename__ = "fotos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    imagem_url = Column(String(500), nullable=False)
    album = Column(String(100), nullable=True)
    destaque = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, server_default=func.now())


class Contribuicao(Base):
    __tablename__ = "contribuicoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    telefone = Column(String(20), nullable=True)
    valor = Column(Numeric(10, 2), nullable=True)
    mensagem = Column(Text, nullable=True)
    status = Column(String(20), default="pendente")
    criado_em = Column(DateTime, server_default=func.now())
