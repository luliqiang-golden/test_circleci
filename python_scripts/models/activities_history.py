from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func
from models.user import User
from app import db
from utils.decimal_encoder import DecimalEncoder
import json


class ActivitiesHistory(db.Model):
    __tablename__ = 'activities_history'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    changed_by = db.Column(db.Integer)
    changed_at  = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String())
    action = db.Column(db.String())
    old_data = db.Column(JSONB)
    new_data = db.Column(JSONB)
    old_timestamp = db.Column(DateTime(timezone=True))
    new_timestamp = db.Column(DateTime(timezone=True))
    reason_for_modification = db.Column(db.String())
    activity_id = db.Column(db.Integer)
    
    def get_all_activity_history(organization_id):

        return (ActivitiesHistory.
                query.with_entities(ActivitiesHistory.id.label('id'),
                                    ActivitiesHistory.organization_id.label('organization_id'),
                                    User.name.label('changed_by'),
                                    ActivitiesHistory.changed_at.label('changed_at'),
                                    ActivitiesHistory.name.label('name'),
                                    ActivitiesHistory.action.label('action'),
                                    ActivitiesHistory.old_data.label('old_data'),
                                    ActivitiesHistory.new_data.label('new_data'),
                                    ActivitiesHistory.old_timestamp.label('old_timestamp'),
                                    ActivitiesHistory.new_timestamp.label('new_timestamp'),
                                    ActivitiesHistory.reason_for_modification.label('reason_for_modification'),
                                    ActivitiesHistory.activity_id.label('activity_id'))
                .join(User, User.id == ActivitiesHistory.changed_by)
                .filter(ActivitiesHistory.organization_id == organization_id)
                .order_by(ActivitiesHistory.changed_at.desc())
                .all())

    def get_activity_history_by_id(organization_id, activity_id):

        return (ActivitiesHistory.
                query.with_entities(ActivitiesHistory.id.label('id'),
                                    ActivitiesHistory.organization_id.label('organization_id'),
                                    User.name.label('changed_by'),
                                    ActivitiesHistory.changed_at.label('changed_at'),
                                    ActivitiesHistory.name.label('name'),
                                    ActivitiesHistory.action.label('action'),
                                    ActivitiesHistory.old_data.label('old_data'),
                                    ActivitiesHistory.new_data.label('new_data'),
                                    ActivitiesHistory.old_timestamp.label('old_timestamp'),
                                    ActivitiesHistory.new_timestamp.label('new_timestamp'),
                                    ActivitiesHistory.reason_for_modification.label('reason_for_modification'),
                                    ActivitiesHistory.activity_id.label('activity_id'))
                .join(User, User.id == ActivitiesHistory.changed_by)
                .filter(ActivitiesHistory.organization_id == organization_id)
                .filter(ActivitiesHistory.activity_id == activity_id)
                .order_by(ActivitiesHistory.changed_at.desc())
                .all())

    def add_history_entry(organization_id, changed_by, name, action, old_data, new_data, old_timestamp, new_timestamp, reason_for_modification, activity_id):
        
        activitiesHistory = ActivitiesHistory(
                organization_id = organization_id,
                changed_by = changed_by,
                name = name,
                action = action,
                old_data = json.loads(json.dumps(old_data, cls=DecimalEncoder)),
                new_data = json.loads(json.dumps(new_data, cls=DecimalEncoder)),
                old_timestamp = old_timestamp,
                new_timestamp = new_timestamp,
                reason_for_modification = reason_for_modification,
                activity_id = activity_id
            )

        db.session.add(activitiesHistory)
        db.session.commit()
