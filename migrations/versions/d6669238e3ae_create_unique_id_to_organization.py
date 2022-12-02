"""create unique id to organization

Revision ID: d6669238e3ae
Revises: c04de60ebc11
Create Date: 2022-07-14 19:22:34.924541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6669238e3ae'
down_revision = 'c04de60ebc11'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE organizations 
        ADD COLUMN IF NOT EXISTS unique_id BIGINT NULL;
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE organizations 
        DROP COLUMN IF EXISTS unique_id;
        """)
