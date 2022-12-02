from sqlalchemy import DateTime, func
from sqlalchemy.orm import aliased
from models.user import User
from models.role import Role
from app import db


class UserRoleHistory(db.Model):
    __tablename__ = 'user_role_history'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer)
    action = db.Column(db.String())
    old_role = db.Column(db.Integer())
    new_role = db.Column(db.Integer())
    
    def get_user_history(organization_id):
        
        user_table_1 = aliased(User)
        user_table_2 = aliased(User)
        role_table_1 = aliased(Role)
        role_table_2 = aliased(Role)
        
        return (UserRoleHistory.query.with_entities(UserRoleHistory.timestamp.label('timestamp'),
                                                    user_table_1.name.label('created_by'),
                                                    UserRoleHistory.action.label('action'),
                                                    user_table_2.name.label('user'),
                                                    role_table_1.name.label('old_role'),
                                                    role_table_2.name.label('new_role'))
                                                    .join(user_table_1, user_table_1.id == UserRoleHistory.created_by)
                                                    .join(user_table_2, user_table_2.id == UserRoleHistory.user_id)
                                                    .join(role_table_1, role_table_1.id == UserRoleHistory.old_role, isouter=True)
                                                    .join(role_table_2, role_table_2.id == UserRoleHistory.new_role, isouter=True)
                                                    .filter(UserRoleHistory.organization_id == organization_id)
                                                    .order_by(UserRoleHistory.timestamp.desc())
                                                    .all())
    
    def add_history_entry(organization_id, created_by, user_id, action, old_role, new_role):
        
        userRoleHistory = UserRoleHistory(
                organization_id = organization_id,
                created_by = created_by,
                user_id = user_id,
                action = action,
                old_role = old_role,
                new_role = new_role
            )

        db.session.add(userRoleHistory)
        db.session.commit()