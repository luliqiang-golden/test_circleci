"""adds new column creates_inventory to activity mapping table

Revision ID: fa6b5940cc56
Revises: 23496a860c3a
Create Date: 2022-08-17 13:11:16.595424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa6b5940cc56'
down_revision = '23496a860c3a'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
            ALTER TABLE activities_mapping 
            ADD COLUMN creates_inventory bool NOT NULL DEFAULT FALSE;


            UPDATE activities_mapping SET creates_inventory = TRUE
            WHERE name IN ('receive_inventory', 'queue_for_destruction', 'create_mother', 'create_batch',
            'create_mother_batch', 'create_sample', 'create_lot', 'create_lot_item');

        """)

def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            ALTER TABLE activities_mapping 
            DROP COLUMN creates_inventory;
        """)