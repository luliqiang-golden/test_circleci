"""create admin_users user

Revision ID: 65fee58b8b70
Revises: a71fd2ed1129
Create Date: 2022-03-18 13:55:27.418534

"""
import os
import sys
sys.path.append(
    os.path.join(os.path.dirname(__file__), os.pardir, "python_scripts"))

from alembic import op
from sqlalchemy import orm

from models.admin_users import AdminUser


# revision identifiers, used by Alembic.
revision = '65fee58b8b70'
down_revision = 'a71fd2ed1129'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    user = AdminUser(username='maintenance', password='pbkdf2:sha256:260000$9uvUcbYcPWAG2EKE$7a530e500b7bb035ab1d6c4dcb4f137cdab4ef5e3af0dadf64cf2706bc26f9f4')
    session.add(user)
    session.commit()


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.query(AdminUser).filter_by(username='maintenance').delete()
    session.commit()
