from models import Usuario
from repository.BaseRepository import BaseRepository



class UsuarioRepository(BaseRepository):
    def __init__(self):
        super().__init__(Usuario)