from models.models import Prateleira, Caixa
from repository.BaseRepository import BaseRepository
from sqlalchemy.orm import aliased


class PrateleiraRepository(BaseRepository):
    def __init__(self):
        super().__init__(Prateleira)


    def get_prateleiras(self):
        return self.find_all()

    def get_prateleira_by_id(self, prateleira_id):
        return self.get_by_id(prateleira_id)

    def add_prateleira(self, prateleira):
        return self.save(prateleira)

    def update_prateleira(self, prateleira):
        return self.update(prateleira)

    def delete_prateleira(self, prateleira_id):
        return self.delete(prateleira_id)



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