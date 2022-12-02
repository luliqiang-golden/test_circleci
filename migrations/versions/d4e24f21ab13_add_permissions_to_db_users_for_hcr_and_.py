"""add permissions to db users for HCR and taxanomies

Revision ID: d4e24f21ab13
Revises: b4f93cd1b707
Create Date: 2021-10-12 11:28:47.095680

"""
from alembic import op
import sqlalchemy as sa
import os

# revision identifiers, used by Alembic.
revision = 'd4e24f21ab13'
down_revision = 'b4f93cd1b707'
branch_labels = None
depends_on = None
db_user = os.environ.get('DB_USERNAME')

def upgrade():
    connection = op.get_bind()
    connection.execute(
        f'''
        GRANT ALL ON TABLE stats_taxonomies TO dev_users;
        GRANT ALL ON TABLE stats_taxonomies TO postgres;
        GRANT ALL ON TABLE stats_taxonomies TO api_server;
        GRANT ALL ON TABLE public.health_canada_report TO dev_users;
        GRANT ALL ON TABLE public.health_canada_report TO postgres;
        GRANT ALL ON TABLE public.health_canada_report TO api_server;
        '''
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        f'''
        REVOKE ALL ON TABLE stats_taxonomies TO dev_users;
        REVOKE ALL ON TABLE stats_taxonomies TO postgres;
        REVOKE ALL ON TABLE stats_taxonomies TO api_server;
        REVOKE ALL ON TABLE public.health_canada_report TO dev_users;
        REVOKE ALL ON TABLE public.health_canada_report TO postgres;
        REVOKE ALL ON TABLE public.health_canada_report TO api_server;
        '''
    )

