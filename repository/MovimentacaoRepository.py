from models.models import Movimentacao, Usuario, Caixa
from repository.BaseRepository import BaseRepository
import datetime


class MovimentacaoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Movimentacao)


    def get_movimentacoes(self):
        return self.find_all()

    def get_movimentacao_by_id(self, movimentacao_id):
        return self.get_by_id(movimentacao_id)

    def add_movimentacao(self, movimentacao):
        return self.save(movimentacao)

    def update_movimentacao(self, movimentacao):
        return self.update(movimentacao)

    def delete_movimentacao(self, movimentacao_id):
        return self.delete(movimentacao_id)



    def find_by_caixa_id(self, caixa_id):
        return self.session.query(self.model).filter(self.model.caixa_id == caixa_id).order_by(
            self.model.data.desc()).all()

    def find_by_usuario_id(self, usuario_id):
        return self.session.query(Movimentacao).filter(Movimentacao.usuarios.any(id=usuario_id)).all()

    def find_by_tipo(self, tipo_movimentacao):
        return self.session.query(self.model).filter(self.model.tipo == tipo_movimentacao).all()

    def find_by_date_range(self, data_inicio, data_fim):
        return self.session.query(self.model).filter(
            self.model.data.between(data_inicio, data_fim)
        ).all()

    def find_latest_movimentacao_for_caixa(self, caixa_id):
        return self.session.query(self.model).filter(
            self.model.caixa_id == caixa_id
        ).order_by(self.model.data.desc()).first()