"""creates notification table

Revision ID: 8c444af29be4
Revises: 1322ab9d5794
Create Date: 2022-10-11 19:54:54.502819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c444af29be4'
down_revision = '7c17cedaca79'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        '''
            CREATE TYPE notification_types AS ENUM ('info', 'success', 'warning', 'error');

            CREATE TABLE notification (
                id bigserial NOT NULL,
                organization_id int4 NOT NULL,
                created_by int4 NOT NULL,
                "timestamp" timestamptz NOT NULL DEFAULT now(),
                "content" varchar NOT NULL,
                type notification_types NOT NULL
            );
        '''
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        '''
            DROP TYPE notification_types;

            DROP TABLE notification;
        '''
    )
