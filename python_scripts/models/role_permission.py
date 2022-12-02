from sqlalchemy import and_, case, asc
from models.permission import Permission
from models.user_role import UserRole
from models.role import Role
from app import db

class RolePermission(db.Model):
    __tablename__ = 'role_permission'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer)
    permission_id = db.Column(db.Integer)

    def get_full_permission_tree(permission_list):
        for permission_id in permission_list:
            permission = Permission.get_permission_by_id(permission_id)
            if(permission.resource_type != 'group' and permission.parent_id not in permission_list):
                permission_list.append(permission.parent_id)
                RolePermission.get_full_permission_tree(permission_list)
        return permission_list

    def get_all_role_permission(organization_id):
        return (Role.query.with_entities(Role.id.label('role_id'),
                                        Role.name.label('role_name'),
                                        Role.role_description.label('role_description'),
                                        Role.organization_id.label('organization_id'))
                                        .join(RolePermission, Role.id == RolePermission.role_id)
                                        .filter(Role.organization_id == organization_id)
                                        .order_by(Role.id.asc())
                                        .distinct().all())


    def get_role_permission_by_id(organization_id, role_id):

        role_info = Role.get_role_by_id(organization_id, role_id)

        return (Permission.query.with_entities(Permission.id.label('id'),
                                              Permission.name.label('name'),
                                              Permission.parent_id.label('parent_id'),
                                              Permission.resource_type.label('resource_type'),
                                              Permission.component_friendly_name.label('component_friendly_name'),
                                              case(
                                                    (RolePermission.id == None, False),
                                                    else_=True
                                              ).label('has_access'),
                                              case(
                                                    (Role.id == role_id, Role.id),
                                                    else_=role_info.id
                                              ).label('role_id'),
                                              case(
                                                    (Role.id == role_id, Role.name),
                                                    else_=role_info.name
                                              ).label('role_name'),
                                              case(
                                                    (Role.id == role_id, Role.role_description),
                                                    else_=role_info.role_description
                                              ).label('role_description'),
                                              case(
                                                    (Role.id == role_id, Role.organization_id),
                                                    else_=role_info.organization_id
                                              ).label('organization_id'),)
                                              .join(RolePermission, and_(Permission.id == RolePermission.permission_id, RolePermission.role_id == role_id), isouter=True)
                                              .join(Role, Role.id == RolePermission.role_id, isouter=True)
                                              .order_by(asc(Permission.id))
                                              .all())

    def get_count_of_groups_by_role_id(role_id):
        return len(Permission.query
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .filter(Permission.resource_type == 'group')
                .filter(RolePermission.role_id == role_id).all())

    def add_role_permission(role_id, permission_list):
        
        rolePermission = []
        
        permission_list = RolePermission.get_full_permission_tree(permission_list)
        
        for permission_id in permission_list:
            rolePermission.append(RolePermission(
                role_id = role_id,
                permission_id = permission_id
            ))

        db.session.bulk_save_objects(rolePermission)
        db.session.commit()
        
        return rolePermission


    def delete_role(role_id):
        db.session.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        db.session.commit()

