'''This module contains database schema model for currencies table'''
from app import db
from sqlalchemy import DateTime, func
from class_errors import ClientBadRequest

class Currency(db.Model):
    '''Definition of currencies table'''
    __tablename__ = 'currencies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    alphabetic_code = db.Column(db.String, unique=True)
    minor_unit = db.Column(db.Integer)
    sign = db.Column(db.String)
    entity = db.Column(db.ARRAY(db.String()))
    created_at = db.Column(DateTime(timezone=True), default=func.now())

    def __init__(self, obj: dict):
        '''Constructor of this class'''
        for k, v in obj.items():
            setattr(self, k, v)
    
    def insert_object(self):
        '''Saves object into db'''
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception as e:
            raise ClientBadRequest({"message": f"Error while inserting data - {e}"}, 500) 

    def __repr__(self):
        return f"<{self.name}>"
