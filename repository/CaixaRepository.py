from database.db import session
from models.models import Caixa

class CaixaRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, caixa_id: int) -> Caixa | None:
        return self.session.query(Caixa).filter(Caixa.id == caixa_id).first()

    def get_all(self) -> list[Caixa]:
        return self.session.query(Caixa).all()

    def get_by_prateleira(self, prateleira_id: int) -> list[Caixa]:
        return self.session.query(Caixa).filter(Caixa.prateleira_id == prateleira_id).all()

    def get_by_unidade(self, unidade_id: int) -> list[Caixa]:
        return self.session.query(Caixa).filter(Caixa.unidade_id == unidade_id).all()

    def add(self, caixa: Caixa) -> None:
        self.session.add(caixa)
        self.session.flush()
        self.session.commit()

    def update(self, caixa: Caixa) -> None:
        self.session.merge(caixa)
        self.session.commit()

    def delete(self, caixa_id: int) -> None:
        obj = self.get_by_id(caixa_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()