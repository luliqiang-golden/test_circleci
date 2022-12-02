"""add permissions to api_server

Revision ID: f70f2d81f125
Revises: 65fee58b8b70
Create Date: 2022-03-21 15:06:38.468335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f70f2d81f125'
down_revision = '65fee58b8b70'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        '''
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO api_server;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO api_server;
        '''
        )



def downgrade():
    pass
