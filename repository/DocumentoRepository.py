from database.db import session
from models.models import Documento


class DocumentoRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, documento_id: int) -> Documento | None:
        return self.session.query(Documento).filter(Documento.id == documento_id).first()

    def get_all(self) -> list[Documento]:
        return self.session.query(Documento).order_by(Documento.titulo).all()

    def get_by_tipo(self, tipo: str) -> list[Documento]:
        return self.session.query(Documento).filter(Documento.tipo == tipo).all()

    def get_by_titulo(self, titulo: str) -> list[Documento]:
        return self.session.query(Documento).filter(Documento.titulo.ilike(f"%{titulo}%")).all()

    def get_by_data_emissao(self, data_emissao) -> list[Documento]:
        return self.session.query(Documento).filter(Documento.data_emissao == data_emissao).all()

    def add(self, documento: Documento) -> None:
        self.session.add(documento)
        self.session.commit()

    def update(self, documento: Documento) -> None:
        self.session.merge(documento)
        self.session.commit()

    def delete(self, documento_id: int) -> None:
        documento = self.get_by_id(documento_id)
        if documento:
            self.session.delete(documento)
            self.session.commit()