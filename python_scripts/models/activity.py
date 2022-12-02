import json
from sqlalchemy.sql.sqltypes import Integer
from operator import or_
from activities import ACTIVITIES
from class_errors import ClientBadRequest
from class_external_webhooks import firing_webhooks

from models.activities_history import ActivitiesHistory
from models.notification import Notification

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func

import json
from utils.decimal_encoder import DecimalEncoder

from app import db
from utils.decimal_encoder import DecimalEncoder

class Activity(db.Model):
    __tablename__ = 'activities'
    __table_args__ = {'extend_existing': True} 


    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    name  = db.Column(db.String())
    data = db.Column(JSONB)
    parent_id = db.Column(db.Integer)
    edited = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

    def __init__(self, organization_id, created_by, timestamp, name, data, parent_id = None, edited = False, deleted = False):
        self.organization_id = organization_id
        self.created_by = created_by
        self.timestamp = timestamp
        self.name = name
        self.data = data
        self.parent_id = parent_id
        self.edited = edited
        self.deleted = deleted
        
    @property
    def serialize(self):
       return {
        'id' : self.id,
        'organization_id' : self.organization_id,
        'created_by' : self.created_by,
        'timestamp'  : self.timestamp,
        'name'  : self.name,
        'data' : self.data,
        'parent_id': self.parent_id,
        'edited': self.edited,
        'deleted': self.deleted,
       }

    def save_activities(organization_id, data, created_by, name, parent_id = None, edited = False, deleted = False, timestamp = None):
        activity = Activity(organization_id = organization_id, 
                             created_by = created_by, 
                             timestamp = timestamp or func.now(), 
                             name = name, 
                             data = json.loads(json.dumps(data, cls=DecimalEncoder)),
                             parent_id = parent_id,
                             edited = edited,
                             deleted = deleted)

        db.session.add(activity)
        db.session.commit()

        return activity

    def update_activities(activity_id, organization_id, data, created_by, name, reason_for_modification, timestamp = None, parent_id = None):
        
        activity = db.session.query(Activity).filter(Activity.id == activity_id).filter(Activity.organization_id == organization_id).one_or_none()
        
        if timestamp:
            ActivitiesHistory.add_history_entry(organization_id, created_by, name, 'UPDATE', activity.data, data, activity.timestamp, timestamp, reason_for_modification, activity_id)
            setattr(activity, 'timestamp', timestamp)

        else:
            ActivitiesHistory.add_history_entry(organization_id, created_by, name, 'UPDATE', activity.data, data, activity.timestamp, activity.timestamp, reason_for_modification, activity_id)

        setattr(activity, 'data', json.loads(json.dumps(data, cls=DecimalEncoder)))
        setattr(activity, 'edited', True)

        db.session.commit()

        return activity

    def delete_activities(activity_id, organization_id, created_by, name, reason_for_modification):
        
        
        activity = db.session.query(Activity).filter(Activity.id == activity_id).filter(Activity.organization_id == organization_id).one_or_none()
        
        setattr(activity, 'deleted', True)

        ActivitiesHistory.add_history_entry(organization_id, created_by, name, 'DELETE', activity.data, {}, activity.timestamp, None, reason_for_modification, activity_id)
        
        db.session.commit()

        return {}

    def get_complete_destruction_activity_by_id(organization_id, destruction_inventory_id):
        return db.session.query(Activity).filter(Activity.organization_id == organization_id).filter(Activity.name=='complete_destruction').filter(Activity.data["from_inventory_id"].astext == destruction_inventory_id).filter(Activity.deleted == False).all()

    def get_inventory_adjustment_activity_by_id(organization_id, destruction_inventory_id):
        return db.session.query(Activity).filter(Activity.organization_id == organization_id).filter(Activity.name=='inventory_adjustment').filter(Activity.data["inventory_id"].astext == destruction_inventory_id).filter(Activity.data["activity_name"].astext == "complete_destruction").filter(Activity.deleted == False).all()

    def get_inventory_adjustment_activity_by_parent_activity(organization_id, parent_activity_id):
        return (db.session.query(Activity)
                .filter(Activity.organization_id == organization_id)
                .filter(Activity.name=='inventory_adjustment')
                .filter(or_(Activity.data["activity_id"].astext.cast(Integer) == parent_activity_id, Activity.parent_id == parent_activity_id))
                .all())

    def backdate_activity(organization_id, created_by, activity_ids, timestamp, reason_for_modification):

        result = []

        for activity_id in activity_ids:
            
            activity = db.session.query(Activity).filter(Activity.id == activity_id).filter(Activity.organization_id == organization_id).one_or_none()
            
            activities = Activity.get_inventory_adjustment_activity_by_parent_activity(organization_id, activity_id)
            
            activities.append(activity)

            for act in activities:

                result.append(act.id)

                ActivitiesHistory.add_history_entry(organization_id, created_by, act.name, 'UPDATE', act.data, act.data, act.timestamp, timestamp, reason_for_modification, activity_id)
                setattr(act, 'timestamp', timestamp)
                setattr(act, 'edited', True)

        db.session.commit()

        return result

    def bulk_activity_handle(organization_id, current_user, batch_list, activity):
        
        batch_list = list(set(batch_list))
        
        allowed_activities = ['consumable_lot_use_items',
                              'batch_add_links',
                              'update_stage',
                              'create_activity_log',
                              'plants_defoliate',
                              'plants_flush',
                              'plants_add_fertilizer',
                              'update_room']
        
        if(activity['name'] not in allowed_activities):
            raise ClientBadRequest({
                    "code": "invalid_activity",
                    "message": f"The for bulk activities please use one of the following: {allowed_activities}"
                }, 400)

        for batch in batch_list:
            try:
                module = ACTIVITIES[activity['name']]
                
                if(activity['name'] == 'consumable_lot_use_items'):
                    activity['linked_inventory_id'] = str(batch)
                    activity['organization_id'] = organization_id
                    activity['created_by'] = current_user['user_id']

                else:
                    activity['inventory_id'] = str(batch)
                    activity['organization_id'] = organization_id
                    activity['created_by'] = current_user['user_id']
                
                module.do_activity(activity, current_user)
    
            except Exception:
                Notification.push_notification(organization_id, current_user['user_id'], f'Rooms activities failed!', 'error')
                raise Exception

        Notification.push_notification(organization_id, current_user['user_id'], 'Rooms activities completed!', 'success')
