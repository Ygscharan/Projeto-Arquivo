from database import session
from models import Base

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def findall(self):
        return session.query(self.model).all()

    def save(self, entity):
        session.add(entity)
        session.commit()
