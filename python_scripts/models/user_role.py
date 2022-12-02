from models.user import User
from models.role import Role
from sqlalchemy import func
from app import db

class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_id = db.Column(db.Integer)


    def get_all_user_role(organization_id):
        return (User.query.with_entities(User.id.label('user_id'),
                                         User.name.label('user_name'),
                                         User.email.label('user_email'),
                                         User.enabled.label('user_enabled'),
                                         User.job_title.label('job_title'),
                                         Role.id.label('role_id'),
                                         Role.name.label('role_name'),
                                         Role.role_description.label('role_description'),
                                         Role.organization_id.label('organization_id'))
                                        .join(UserRole, User.id == UserRole.user_id)
                                        .join(Role, Role.id == UserRole.role_id)
                                        .filter(Role.organization_id == organization_id)
                                        .all())


    def get_user_role_by_user_id(organization_id, user_id):
        return (User.query.with_entities(User.id.label('user_id'),
                                         User.name.label('user_name'),
                                         User.email.label('user_email'),
                                         User.enabled.label('user_enabled'),
                                         User.job_title.label('job_title'),
                                         Role.id.label('role_id'),
                                         Role.name.label('role_name'),
                                         Role.role_description.label('role_description'),
                                         Role.organization_id.label('organization_id'))
                                        .join(UserRole, User.id == UserRole.user_id)
                                        .join(Role, Role.id == UserRole.role_id)
                                        .filter(User.id == user_id)
                                        .filter(User.organization_id == organization_id)
                                        .one_or_none())


    def get_user_role_by_role_id(organization_id, role_id):
        return (User.query.with_entities(User.id.label('user_id'),
                                         User.name.label('user_name'),
                                         User.email.label('user_email'),
                                         User.enabled.label('user_enabled'),
                                         Role.id.label('role_id'),
                                         Role.name.label('role_name'),
                                         Role.role_description.label('role_description'),
                                         Role.organization_id.label('organization_id'))
                                        .join(UserRole, User.id == UserRole.user_id)
                                        .join(Role, Role.id == UserRole.role_id)
                                        .filter(Role.id == role_id)
                                        .filter(Role.organization_id == organization_id)
                                        .all())

    def get_user_count_by_role_id(role_id):
        return (UserRole.query.with_entities(func.count()).filter(UserRole.role_id == role_id).scalar())

    def add_user_role(organization_id, user_id, role_id):
        
        userRole = UserRole(
                user_id = user_id,
                role_id = role_id
            )

        db.session.add(userRole)
        db.session.commit()
        
        return UserRole.get_user_role_by_user_id(organization_id, user_id)


    def update_user_role(organization_id, role_id, user_id):


        db.session.query(UserRole).filter(UserRole.user_id == user_id).update({
            'role_id': role_id
        })


        db.session.commit()

        return UserRole.get_user_role_by_user_id(organization_id, user_id)


    def delete_user_role(user_id):
        db.session.query(UserRole).filter(UserRole.user_id == user_id).delete()
        db.session.commit()
