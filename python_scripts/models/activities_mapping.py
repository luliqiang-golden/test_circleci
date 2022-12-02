from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func
from app import db


class ActivitiesMapping(db.Model):
    __tablename__ = 'activities_mapping'

    id = db.Column(db.Integer, primary_key=True)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String())
    friendly_name = db.Column(db.String())
    is_editable = db.Column(db.Boolean)
    is_deletable = db.Column(db.Boolean)
    is_visible = db.Column(db.Boolean)
    creates_inventory = db.Column(db.Boolean)
    weight_adjustment = db.Column(db.Boolean)

    def get_activities_mapping():
        
        return (ActivitiesMapping.query.all())
    
    def get_activities_create_inventory():
        return (ActivitiesMapping.query
                .filter(ActivitiesMapping.creates_inventory == True)
                .all())
    
    def get_activities_weight_adjustment():
        return (ActivitiesMapping.query
                .filter(ActivitiesMapping.weight_adjustment == True)
                .all())