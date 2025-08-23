from database.db import session
from models.models import Unidade

class UnidadeRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, unidade_id: int) -> Unidade | None:
        return self.session.query(Unidade).filter(Unidade.id == unidade_id).first()

    def get_all(self) -> list[Unidade]:
        return self.session.query(Unidade).order_by(Unidade.nome).all()

    def get_by_nome(self, nome: str) -> list[Unidade]:
        return self.session.query(Unidade).filter(Unidade.nome.ilike(f"%{nome}%")).all()

    def add(self, unidade: Unidade) -> None:
        self.session.add(unidade)
        self.session.commit()

    def update(self, unidade: Unidade) -> None:
        self.session.merge(unidade)
        self.session.commit()

    def delete(self, unidade_id: int) -> None:
        unidade = self.get_by_id(unidade_id)