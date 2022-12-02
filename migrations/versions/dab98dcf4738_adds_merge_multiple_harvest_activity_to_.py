"""adds merge multiple harvest activity to activity mapping table

Revision ID: dab98dcf4738
Revises: d1e1356995f4
Create Date: 2022-09-12 19:40:02.085779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dab98dcf4738'
down_revision = 'd1e1356995f4'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(""" 
                       INSERT INTO activities_mapping (name, friendly_name)
                       VALUES ('merge_multiple_harvest_batches', 'Merge Multiple Harvest Batches');
                       """)


def downgrade():
    connection = op.get_bind()
    connection.execute(""" 
                       
                       DELETE FROM activities_mapping WHERE name = 'merge_multiple_harvest_batches';
                       
                       """)
