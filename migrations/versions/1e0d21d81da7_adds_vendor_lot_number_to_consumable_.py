"""adds vendor lot number to consumable lots table

Revision ID: 1e0d21d81da7
Revises: f4d7f10f0281
Create Date: 2022-03-07 12:31:12.199407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e0d21d81da7'
down_revision = 'f4d7f10f0281'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE consumable_lots 
        ADD COLUMN IF NOT EXISTS vendor_lot_number varchar NULL;
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE consumable_lots 
        DROP COLUMN IF EXISTS vendor_lot_number;
        """)
