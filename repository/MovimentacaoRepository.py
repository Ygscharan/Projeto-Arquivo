from database.db import session
from models.models import Movimentacao
from sqlalchemy import desc
from database.db import session
from models.models import Movimentacao

class MovimentacaoRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, movimentacao_id: int) -> Movimentacao | None:
        return self.session.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()

    def get_all(self) -> list[Movimentacao]:
        return self.session.query(Movimentacao).order_by(desc(Movimentacao.tipo)).all()

    def get_by_caixa(self, caixa_id: int) -> list[Movimentacao]:
        return self.session.query(Movimentacao).filter(Movimentacao.caixa_id == caixa_id).all()

    def get_by_usuario(self, usuario_id: int) -> list[Movimentacao]:
        return self.session.query(Movimentacao).filter(Movimentacao.usuario_id == usuario_id).all()

    def get_by_data(self, data) -> list[Movimentacao]:
        return self.session.query(Movimentacao).filter(Movimentacao.data == data).all()

    def add(self, movimentacao: Movimentacao) -> None:
        self.session.add(movimentacao)
        self.session.commit()

    def update(self, movimentacao: Movimentacao) -> None:
        self.session.merge(movimentacao)
        self.session.commit()

    def delete(self, movimentacao_id: int) -> None:
        movimentacao = self.get_by_id(movimentacao_id)