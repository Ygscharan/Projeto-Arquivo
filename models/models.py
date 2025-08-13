from typing import List, Optional
from sqlalchemy import (
    DateTime, ForeignKeyConstraint, Identity, Integer,
    PrimaryKeyConstraint, VARCHAR, Table, Column, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime



class Base(DeclarativeBase):
    pass


usuario_movimentacao_table = Table(
    'usuario_movimentacao',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuario.id'), primary_key=True),
    Column('movimentacao_id', Integer, ForeignKey('movimentacao.id'), primary_key=True)
)


class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    nome: Mapped[str] = mapped_column(VARCHAR(125))
    email: Mapped[str] = mapped_column(VARCHAR(125))
    senha: Mapped[str] = mapped_column(VARCHAR(50))
    tipo: Mapped[str] = mapped_column(VARCHAR(50))


    movimentacoes: Mapped[List['Movimentacao']] = relationship(
        "Movimentacao",
        secondary=usuario_movimentacao_table,
        back_populates="usuarios"
    )


class Movimentacao(Base):
    __tablename__ = 'movimentacao'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    tipo: Mapped[str] = mapped_column(VARCHAR(50))
    data: Mapped[datetime.datetime] = mapped_column(DateTime)
    caixa_id: Mapped[int] = mapped_column(ForeignKey('caixa.id'))
    documento_id: Mapped[Optional[int]] = mapped_column(ForeignKey('documento.id'))


    usuarios: Mapped[List['Usuario']] = relationship(
        "Usuario",
        secondary=usuario_movimentacao_table,
        back_populates="movimentacoes"
    )

    caixa: Mapped['Caixa'] = relationship(back_populates='movimentacoes')
    documento: Mapped[Optional['Documento']] = relationship(back_populates='movimentacoes')


class Caixa(Base):
    __tablename__ = 'caixa'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    numero_caixa: Mapped[int] = mapped_column(Integer)
    data_criacao: Mapped[datetime.datetime] = mapped_column(DateTime)
    unidade_id: Mapped[Optional[int]] = mapped_column(ForeignKey('unidade.id'))
    prateleira_id: Mapped[Optional[int]] = mapped_column(ForeignKey('prateleira.id'))

    prateleira: Mapped[Optional['Prateleira']] = relationship(back_populates='caixas')
    unidade: Mapped[Optional['Unidade']] = relationship(back_populates='caixas')
    documentos: Mapped[List['Documento']] = relationship(back_populates='caixa')
    movimentacoes: Mapped[List['Movimentacao']] = relationship(back_populates='caixa')


class Documento(Base):
    __tablename__ = 'documento'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    titulo: Mapped[Optional[str]] = mapped_column(VARCHAR(125))
    tipo: Mapped[str] = mapped_column(VARCHAR(50))
    data_arquivo: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    caixa_id: Mapped[int] = mapped_column(ForeignKey('caixa.id'))

    caixa: Mapped['Caixa'] = relationship(back_populates='documentos')
    movimentacoes: Mapped[List['Movimentacao']] = relationship(back_populates='documento')


class Prateleira(Base):
    __tablename__ = 'prateleira'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    setor: Mapped[str] = mapped_column(VARCHAR(100))
    corredor: Mapped[str] = mapped_column(VARCHAR(10))
    coluna: Mapped[int] = mapped_column(Integer)
    nivel: Mapped[int] = mapped_column(Integer)

    caixas: Mapped[List['Caixa']] = relationship(back_populates='prateleira')


class Unidade(Base):
    __tablename__ = 'unidade'

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    nome: Mapped[str] = mapped_column(VARCHAR(100))
    codigo: Mapped[int] = mapped_column(Integer)

    caixas: Mapped[List['Caixa']] = relationship(back_populates='unidade')
