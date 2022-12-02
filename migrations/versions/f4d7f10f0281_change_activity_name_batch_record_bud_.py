"""change activity name batch_record_bud_weight to  batch_record_harvest_weight

Revision ID: f4d7f10f0281
Revises: 739daca8387f
Create Date: 2022-02-21 15:14:00.168991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4d7f10f0281'
down_revision = 'd1b02172157c'
branch_labels = None
depends_on = None


def upgrade():

    connection = op.get_bind()
    connection.execute(
        """
            UPDATE activities
            SET name = 'batch_record_harvest_weight'
            WHERE name = 'batch_record_bud_harvest_weight';
        """
    )


def downgrade():
    
    connection = op.get_bind()
    connection.execute(
        """
            UPDATE activities
            SET name = 'batch_record_bud_harvest_weight'
            WHERE name = 'batch_record_harvest_weight';
        """
    )
