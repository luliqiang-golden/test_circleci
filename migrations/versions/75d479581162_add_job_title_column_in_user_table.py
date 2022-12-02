"""Add Job title column in user table

Revision ID: 75d479581162
Revises: e71f00f07c66
Create Date: 2022-06-27 11:30:55.846716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75d479581162'
down_revision = 'e71f00f07c66'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS job_title varchar NULL;
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE users 
        DROP COLUMN IF EXISTS job_title;
        """)