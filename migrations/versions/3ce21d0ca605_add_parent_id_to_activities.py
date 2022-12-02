"""add parent_id to activities

Revision ID: 3ce21d0ca605
Revises: 24e708a74772
Create Date: 2022-02-03 02:15:13.030088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ce21d0ca605'
down_revision = '24e708a74772'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
        ALTER TABLE activities 
        ADD COLUMN parent_id bigint;
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
    """
        ALTER TABLE activities 
        DROP COLUMN parent_id;
    """)
