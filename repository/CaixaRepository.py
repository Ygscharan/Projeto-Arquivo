from sqlalchemy import func
from database.db import session
from models.models import Caixa
from datetime import date

class CaixaRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, caixa_id: int) -> Caixa | None:
        return self.session.query(Caixa).filter(Caixa.id == caixa_id).first()

    def get_all(self) -> list[Caixa]:
        return self.session.query(Caixa).order_by(Caixa.numero_caixa).all()

    def get_by_prateleira(self, prateleira_id: int) -> list[Caixa]:
        return self.session.query(Caixa).filter(Caixa.prateleira_id == prateleira_id).all()

    def get_by_unidade(self, unidade_id: int) -> list[Caixa]:
        return self.session.query(Caixa).filter(Caixa.unidade_id == unidade_id).all()
    
    def get_caixas_a_eliminar(self) -> list[Caixa]:
        return self.session.query(Caixa).filter(Caixa.data_eliminacao > date.today()).all()

    def get_max_numero_caixa(self) -> int:
        max_num = self.session.query(func.max(Caixa.numero_caixa)).scalar()
        return max_num if max_num is not None else 0

    def numero_exists(self, numero_caixa: int) -> bool:
        return self.session.query(Caixa.id).filter(Caixa.numero_caixa == numero_caixa).first() is not None

    def add(self, caixa: Caixa) -> None:
        self.session.add(caixa)
        self.session.commit()
        self.session.remove()

    def update(self, caixa: Caixa) -> None:
        self.session.merge(caixa)
        self.session.commit()
        self.session.remove() 

    def delete(self, caixa_id: int) -> None:
        obj = self.get_by_id(caixa_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            self.session.remove()