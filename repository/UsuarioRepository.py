from models.models import Usuario
from repository.BaseRepository import BaseRepository

class UsuarioRepository(BaseRepository):
    def __init__(self):
        super().__init__(Usuario)

    def get_usuarios(self):
        return self.find_all()

    def get_usuario_by_id(self, usuario_id):
        return self.get_by_id(usuario_id)

    def add_usuario(self, usuario):
        return self.save(usuario)

    def update_usuario(self, usuario):
        return self.update(usuario)

    def delete_usuario(self, usuario_id):
        return self.delete(usuario_id)

    def find_by_email(self, email):
        return self.session.query(self.model).filter(self.model.email == email).first()

    def find_by_nome(self, nome):
        return self.session.query(self.model).filter(self.model.nome.ilike(f'%{nome}%')).all()

    def find_by_tipo(self, tipo):
        return self.session.query(self.model).filter(self.model.tipo == tipo).all()