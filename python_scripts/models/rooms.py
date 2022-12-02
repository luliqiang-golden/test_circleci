
from sqlalchemy import func
from app import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func

class Rooms(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    name = db.Column(db.String())
    data = db.Column(JSONB)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    
    def get_all_rooms(organization_id):
        return Rooms.query.with_entities(Rooms.id.label('id'),
                                        Rooms.name.label('name'),
                                        Rooms.data['zone'].label('zone')).filter(Rooms.organization_id == organization_id).all()