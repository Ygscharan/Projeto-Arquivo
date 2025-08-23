from database.db import session
from models.models import Prateleira, Caixa

class PrateleiraRepository():
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, prateleira_id: int) -> Prateleira | None:
        return self.session.query(Prateleira).filter(Prateleira.id == prateleira_id).first()

    def get_all(self) -> list[Prateleira]:
        return self.session.query(Prateleira).order_by(Prateleira.setor, Prateleira.corredor).all()

    def get_by_setor(self, setor: str) -> list[Prateleira]:
        return self.session.query(Prateleira).filter(Prateleira.setor == setor).all()

    def get_by_corredor(self, corredor: int) -> list[Prateleira]:
        return self.session.query(Prateleira).filter(Prateleira.corredor == corredor).all()

    def get_by_coluna(self, coluna: int) -> list[Prateleira]:
        return self.session.query(Prateleira).filter(Prateleira.coluna == coluna).all()

    def get_by_nivel(self, nivel: int) -> list[Prateleira]:
        return self.session.query(Prateleira).filter(Prateleira.nivel == nivel).all()

    def add(self, prateleira: Prateleira) -> None:
        self.session.add(prateleira)
        self.session.commit()

    def update(self, prateleira: Prateleira) -> None:
        self.session.merge(prateleira)
        self.session.commit()

    def delete(self, prateleira_id: int) -> None:
        prateleira = self.get_by_id(prateleira_id)
        if prateleira:
            self.session.delete(prateleira)
            self.session.commit()

    def find_by_localizacao(self, setor, corredor=None, coluna=None, nivel=None):
        query = self.session.query(self.model).filter(self.model.setor == setor)

        if corredor:
            query = query.filter(self.model.corredor == corredor)
        if coluna:
            query = query.filter(self.model.coluna == coluna)
        if nivel:
            query = query.filter(self.model.nivel == nivel)

        return query.all()

    def find_prateleiras_vazias(self):
        return self.session.query(Prateleira).outerjoin(Caixa).filter(Caixa.id == None).all()

    def count_caixas_na_prateleira(self, prateleira_id):
        return self.session.query(Caixa).filter(Caixa.prateleira_id == prateleira_id).count()