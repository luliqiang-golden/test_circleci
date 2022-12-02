
import copy
from app import db
from sqlalchemy import DateTime, func

class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True))
    content  = db.Column(db.String())
    type  = db.Column(db.String())
    
    def push_notification(organization_id, created_by, content, type):
        
        notification = Notification(
                organization_id = organization_id,
                created_by = created_by,
                timestamp = func.now(),
                content = content,
                type = type
        )

        db.session.add(notification)
        db.session.commit()
    
    def has_notification(organization_id, created_by):
        
        notification = (Notification.query
                        .filter(Notification.organization_id == organization_id)
                        .filter(Notification.created_by == created_by)
                        .order_by(Notification.timestamp.asc()).first())
        
        if(notification):
            return True
        else:
            return False
    
    def pop_notification(organization_id, created_by):
        
        notification = (Notification.query
                        .filter(Notification.organization_id == organization_id)
                        .filter(Notification.created_by == created_by)
                        .order_by(Notification.timestamp.asc()).first())
        
        
        notification_ = copy.deepcopy(notification)
        
        db.session.query(Notification).filter(Notification.id == notification.id).delete()
        db.session.commit()
        
        return notification_
