from models.models import Caixa, Prateleira, Unidade
from repository.BaseRepository import BaseRepository
import datetime


class CaixaRepository(BaseRepository):
    def __init__(self):
        super().__init__(Caixa)

    def get_caixas(self):
        return self.session.query(self.model).order_by(self.model.numero_caixa.asc()).all()

    def get_caixa_by_id(self, caixa_id):
        return self.get_by_id(caixa_id)

    def add_caixa(self, caixa):
        return self.save(caixa)

    def update_caixa(self, caixa):
        return self.update(caixa)

    def delete_caixa(self, caixa_id):
        return self.delete(caixa_id)



    def find_by_numero_caixa(self, numero):

        return self.session.query(self.model).filter(self.model.numero_caixa == numero).first()

    def find_by_prateleira_id(self, prateleira_id):
        return self.session.query(self.model).filter(self.model.prateleira_id == prateleira_id).all()

    def find_by_unidade_id(self, unidade_id):
        return self.session.query(Caixa).join(Unidade).filter(Unidade.id == unidade_id).all()

    def find_caixas_para_eliminar(self):
        data_hoje = datetime.datetime.now()
        return self.session.query(self.model).filter(self.model.data_eliminacao <= data_hoje).all()