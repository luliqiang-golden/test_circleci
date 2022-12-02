from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import DateTime, func
from sqlalchemy.orm import aliased
from models.user import User 
from models.role import Role
from app import db


class RolePermissionHistory(db.Model):
    __tablename__ = 'permission_role_history'

    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    role_id = db.Column(db.Integer)
    action = db.Column(db.String())
    old_permissions = db.Column(JSONB)
    new_permissions = db.Column(JSONB)
    
    
    
    def get_permission_role_history(organization_id):
        
        user_table_1 = aliased(User)
        role_table_1 = aliased(Role)
        
        return (RolePermissionHistory.query.with_entities(RolePermissionHistory.timestamp.label('timestamp'),
                                                    user_table_1.name.label('created_by'),
                                                    RolePermissionHistory.action.label('action'),
                                                    role_table_1.name.label('name'),
                                                    RolePermissionHistory.old_permissions.label('old_permission'),
                                                    RolePermissionHistory.new_permissions.label('new_permission'),)
                                                    .join(user_table_1, user_table_1.id == RolePermissionHistory.created_by)
                                                    .join(role_table_1, role_table_1.id == RolePermissionHistory.role_id, isouter=True)
                                                    .filter(RolePermissionHistory.organization_id == organization_id)
                                                    .order_by(RolePermissionHistory.timestamp.desc())
                                                    .all())


    def add_history_entry(organization_id, created_by, role_id, action, old_permissions, new_permissions):
        
        permissionRoleHistory = RolePermissionHistory(
                organization_id = organization_id,
                created_by = created_by,
                role_id = role_id,
                action = action,
                old_permissions = old_permissions,
                new_permissions = new_permissions
            )

        db.session.add(permissionRoleHistory)
        db.session.commit()