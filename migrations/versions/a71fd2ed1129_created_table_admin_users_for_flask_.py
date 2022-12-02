"""Created table admin_users for Flask admin access.

Revision ID: a71fd2ed1129
Revises: 1668ea6d6344
Create Date: 2022-03-08 00:05:56.285327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a71fd2ed1129'
down_revision = '1e0d21d81da7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'admin_users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
    )


def downgrade():
    op.drop_table(
        'admin_users',
    )
