from typing import List, Optional
from sqlalchemy import (
    DateTime, ForeignKeyConstraint, Identity, Integer,
    PrimaryKeyConstraint, VARCHAR, Table, String, Column, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime



class Base(DeclarativeBase):
    pass


class Caixa(Base):
    __tablename__ = 'caixa'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_caixa: Mapped[int] = mapped_column(Integer, unique=True)
    data_criacao: Mapped[datetime.datetime] = mapped_column(DateTime)
    data_eliminacao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)

    documento_id: Mapped[Optional[int]] = mapped_column(ForeignKey('documento.id'), nullable=True)
    documento: Mapped[Optional["Documento"]] = relationship(back_populates='caixas')

    unidade_id: Mapped[int] = mapped_column(ForeignKey('unidade.id'))
    prateleira_id: Mapped[int] = mapped_column(ForeignKey('prateleira.id'))
    unidade: Mapped["Unidade"] = relationship(back_populates='caixas')
    prateleira: Mapped["Prateleira"] = relationship(back_populates='caixas')
    movimentacoes: Mapped[List["Movimentacao"]] = relationship(back_populates='caixa')


class Documento(Base):
    __tablename__ = 'documento'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(125))
    tipo: Mapped[str] = mapped_column(String(50))

    caixas: Mapped[List["Caixa"]] = relationship(back_populates='documento')
    movimentacoes: Mapped[List["Movimentacao"]] = relationship(back_populates='documento')


class Usuario(Base):
    __tablename__ = 'usuario'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(125))
    email: Mapped[str] = mapped_column(String(125), unique=True)
    senha: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(50))

    movimentacoes: Mapped[List["Movimentacao"]] = relationship(back_populates="usuario")


class Movimentacao(Base):
    __tablename__ = 'movimentacao'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50))
    data: Mapped[datetime.datetime] = mapped_column(DateTime)

    caixa_id: Mapped[int] = mapped_column(ForeignKey('caixa.id'))
    documento_id: Mapped[Optional[int]] = mapped_column(ForeignKey('documento.id'), nullable=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id'))

    usuario: Mapped["Usuario"] = relationship(back_populates="movimentacoes")
    caixa: Mapped["Caixa"] = relationship(back_populates='movimentacoes')
    documento: Mapped[Optional["Documento"]] = relationship(back_populates='movimentacoes')


class Unidade(Base):
    __tablename__ = 'unidade'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    codigo: Mapped[int] = mapped_column(Integer, unique=True)
    caixas: Mapped[List["Caixa"]] = relationship(back_populates='unidade')


class Prateleira(Base):
    __tablename__ = 'prateleira'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    setor: Mapped[str] = mapped_column(String(100))
    corredor: Mapped[str] = mapped_column(String(10))
    coluna: Mapped[int] = mapped_column(Integer)
    nivel: Mapped[int] = mapped_column(Integer)
    caixas: Mapped[List["Caixa"]] = relationship(back_populates='prateleira')