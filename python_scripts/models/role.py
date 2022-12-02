
from sqlalchemy import DateTime, func

from app import db


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String())
    role_description = db.Column(db.String())


    def get_all_roles(organization_id):
        return db.session.query(Role).filter(Role.organization_id==organization_id).all()


    def get_role_by_id(organization_id, role_id):
        return db.session.query(Role).filter(Role.id==role_id).filter(Role.organization_id == organization_id).one_or_none()


    def add_role(organization_id, created_by, name, role_description=None):
        
        role = Role(
                organization_id = organization_id,
                created_by = created_by,
                name = name,
                role_description = role_description
            )

        db.session.add(role)
        db.session.commit()

        return role


    def update_role(organization_id, role_id, name, role_description=None):
        
        if(role_description):
        
            db.session.query(Role).filter(Role.id == role_id).filter(Role.organization_id == organization_id).update({
                'name': name,
                'role_description': role_description
            })
        
        else:
            
            db.session.query(Role).filter(Role.id == role_id).filter(Role.organization_id == organization_id).update({
                'name': name
            })
        
        db.session.commit()
        
        return Role.get_role_by_id(organization_id, role_id)


    def delete_role(role_id):
        db.session.query(Role).filter(Role.id == role_id).delete()
        db.session.commit()

