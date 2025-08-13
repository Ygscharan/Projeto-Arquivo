from database import session
from models.models import Base

class BaseRepository:
    def __init__(self, model):
        self.model = model
        self.session = session

    def find_all(self):
        return self.session.query(self.model).all()

    def get_by_id(self, entity_id):
        return self.session.query(self.model).filter(self.model.id == entity_id).first()

    def save(self, entity):
        self.session.add(entity)
        self.session.commit()
        return entity

    def update(self, entity):
        self.session.merge(entity)
        self.session.commit()
        return entity

    def delete(self, entity_id):
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False