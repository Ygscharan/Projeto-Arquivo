from models.models import Unidade
from repository.BaseRepository import BaseRepository

class UnidadeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Unidade)


    def get_unidades(self):
        return self.find_all()

    def get_unidade_by_id(self, unidade_id):
        return self.get_by_id(unidade_id)

    def add_unidade(self, unidade):
        return self.save(unidade)

    def update_unidade(self, unidade):
        return self.update(unidade)

    def delete_unidade(self, unidade_id):
        return self.delete(unidade_id)


    def find_by_codigo(self, codigo_unidade):
        return self.session.query(self.model).filter(self.model.codigo == codigo_unidade).first()

    def find_by_nome(self, nome_unidade):
        return self.session.query(self.model).filter(self.model.nome.ilike(f'%{nome_unidade}%')).all()