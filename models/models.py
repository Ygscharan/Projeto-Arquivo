from sqlalchemy import Column, DateTime, Integer, PrimaryKeyConstraint, Table, VARCHAR, ForeignKeyConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship
from typing import List, Optional
import datetime

class Base(MappedAsDataclass, DeclarativeBase):
    pass


class Documento(Base):
    __tablename__ = 'documento'
    __table_args__ = (PrimaryKeyConstraint('id', name='documento_pk'),)

    titulo: Mapped[str] = mapped_column(VARCHAR(250))
    tipo: Mapped[str] = mapped_column(VARCHAR(50))

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    caixas: Mapped[List['Caixa']] = relationship(
        'Caixa',
        secondary='caixa_documento',
        back_populates='documentos',
        default_factory=list
    )


class Prateleira(Base):
    __tablename__ = 'prateleira'
    __table_args__ = (PrimaryKeyConstraint('id', name='prateleira_pk'),)

    setor: Mapped[str] = mapped_column(VARCHAR(100))
    corredor: Mapped[str] = mapped_column(VARCHAR(50))    # aceita 'A', '1', etc.
    coluna: Mapped[str] = mapped_column(VARCHAR(50))
    nivel: Mapped[str] = mapped_column(VARCHAR(50))

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    caixas: Mapped[List['Caixa']] = relationship('Caixa', back_populates='prateleira', default_factory=list)


class Unidade(Base):
    __tablename__ = 'unidade'
    __table_args__ = (PrimaryKeyConstraint('id', name='unidade_pk'),)

    nome: Mapped[str] = mapped_column(VARCHAR(125))
    codigo: Mapped[int] = mapped_column(Integer)

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    caixas: Mapped[List['Caixa']] = relationship('Caixa', back_populates='unidade', default_factory=list)


class Usuario(Base):
    __tablename__ = 'usuario'
    __table_args__ = (PrimaryKeyConstraint('id', name='usuario_pk'),)

    nome: Mapped[str] = mapped_column(VARCHAR(125))
    email: Mapped[str] = mapped_column(VARCHAR(125))
    senha: Mapped[str] = mapped_column(VARCHAR(100))
    tipo: Mapped[str] = mapped_column(VARCHAR(50))

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    movimentacoes: Mapped[List['Movimentacao']] = relationship('Movimentacao', back_populates='usuario', default_factory=list)


class Caixa(Base):
    __tablename__ = 'caixa'
    __table_args__ = (PrimaryKeyConstraint('id', name='caixa_pk'),)

    # required (no default) fields first
    numero_caixa: Mapped[int] = mapped_column(Integer)
    data_criacao: Mapped[datetime.datetime] = mapped_column(DateTime)
    unidade_id: Mapped[int] = mapped_column(Integer, ForeignKey('unidade.id'))
    prateleira_id: Mapped[int] = mapped_column(Integer, ForeignKey('prateleira.id'))

    # optional / defaults after
    data_eliminacao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=None)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    prateleira: Mapped[Optional[Prateleira]] = relationship('Prateleira', back_populates='caixas', default=None)
    unidade: Mapped[Optional[Unidade]] = relationship('Unidade', back_populates='caixas', default=None)
    documentos: Mapped[List[Documento]] = relationship('Documento', secondary='caixa_documento', back_populates='caixas', default_factory=list)
    movimentacoes: Mapped[List['Movimentacao']] = relationship('Movimentacao', back_populates='caixa', default_factory=list)


t_caixa_documento = Table(
    'caixa_documento', Base.metadata,
    Column('caixa_id', Integer, nullable=False),
    Column('documento_id', Integer, nullable=False),
    ForeignKeyConstraint(['caixa_id'], ['caixa.id'], name='caixa_documento_fk'),
    ForeignKeyConstraint(['documento_id'], ['documento.id'], name='caixa_documento_fkv2'),
    PrimaryKeyConstraint('caixa_id', 'documento_id', name='caixa_documento_pk')
)


class Movimentacao(Base):
    __tablename__ = 'movimentacao'
    __table_args__ = (PrimaryKeyConstraint('id', name='movimentacao_pk'),)

    tipo: Mapped[str] = mapped_column(VARCHAR(50))
    data: Mapped[datetime.datetime] = mapped_column(DateTime)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey('usuario.id'))
    caixa_id: Mapped[int] = mapped_column(Integer, ForeignKey('caixa.id'))

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True, autoincrement=True, default=None)

    usuario: Mapped[Optional[Usuario]] = relationship('Usuario', back_populates='movimentacoes', default=None)
    caixa: Mapped[Optional[Caixa]] = relationship('Caixa', back_populates='movimentacoes', default=None)