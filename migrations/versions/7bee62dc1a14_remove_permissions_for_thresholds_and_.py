"""remove permissions for thresholds and data changes

Revision ID: 7bee62dc1a14
Revises: 75d479581162
Create Date: 2022-07-08 16:46:47.404617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bee62dc1a14'
down_revision = '75d479581162'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        '''
            DELETE FROM permission WHERE name IN ('administration_thresholds_access', 'administration_data_changes_access', 'qa_data_changes_access');
        '''
    )


def downgrade():
    pass
