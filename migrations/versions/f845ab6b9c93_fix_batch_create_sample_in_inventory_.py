"""fix batch-create-sample in inventory attributes to create-sample

Revision ID: f845ab6b9c93
Revises: 5e707e47852e
Create Date: 2022-07-28 18:05:35.650367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f845ab6b9c93'
down_revision = '5e707e47852e'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            UPDATE inventories SET "attributes" = jsonb_set("attributes", '{test_status}', '"create-sample"') WHERE "attributes"->>'test_status' = 'batch-create-sample'
        
        """)

def downgrade():
    pass
