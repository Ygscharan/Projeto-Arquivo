from models.models import Documento, Caixa
from repository.BaseRepository import BaseRepository


class DocumentoRepository(BaseRepository):
    def __init__(self):
        super().__init__(Documento)


    def get_documentos(self):
        return self.find_all()

    def get_documento_by_id(self, documento_id):
        return self.get_by_id(documento_id)

    def add_documento(self, documento):
        return self.save(documento)

    def update_documento(self, documento):
        return self.update(documento)

    def delete_documento(self, documento_id):
        return self.delete(documento_id)


    def find_by_titulo(self, termo_busca):
        return self.session.query(self.model).filter(self.model.titulo.ilike(f'%{termo_busca}%')).all()

    def find_by_tipo(self, tipo_documento):
        return self.session.query(self.model).filter(self.model.tipo == tipo_documento).all()

    def find_by_caixa_id(self, caixa_id):
        return self.session.query(self.model).filter(self.model.caixa_id == caixa_id).all()

    def count_documentos_na_caixa(self, caixa_id):
        return self.session.query(self.model).filter(self.model.caixa_id == caixa_id).count()