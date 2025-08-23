from database.db import session
from models.models import Usuario

class UsuarioRepository:
    def __init__(self, session=session):
        self.session = session

    def get_by_id(self, usuario_id: int) -> Usuario | None:
        return self.session.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_all(self) -> list[Usuario]:
        return self.session.query(Usuario).order_by(Usuario.nome).all()

    def get_by_nome(self, nome: str) -> list[Usuario]:
        return self.session.query(Usuario).filter(Usuario.nome.ilike(f"%{nome}%")).all()

    def get_by_email(self, email: str) -> Usuario | None:
        return self.session.query(Usuario).filter(Usuario.email == email).first()

    def add(self, usuario: Usuario) -> None:
        self.session.add(usuario)
        self.session.commit()

    def update(self, usuario: Usuario) -> None:
        self.session.merge(usuario)
        self.session.commit()

    def delete(self, usuario_id: int) -> None:
        usuario = self.get_by_id(usuario_id)
        if usuario:
            self.session.delete(usuario)