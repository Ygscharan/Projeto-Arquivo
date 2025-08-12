from models import Caixa
from repository.BaseRepository import BaseRepository

class CaixaRepository(BaseRepository):
    def __init__(self):
        super().__init__(Caixa)
