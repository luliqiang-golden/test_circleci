"""add db permission to api_server user

Revision ID: 9fda3a5d3b99
Revises: 84894dd33ed8
Create Date: 2021-11-10 13:39:45.900463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fda3a5d3b99'
down_revision = '84894dd33ed8'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        '''
        CREATE OR REPLACE FUNCTION create_role_if_not_exists(rolename NAME) RETURNS TEXT AS
        $$
        BEGIN
            IF NOT EXISTS (SELECT * FROM pg_roles WHERE rolname = rolename) THEN
                EXECUTE format('CREATE ROLE %%I', rolename);
                RETURN 'CREATE ROLE';
            ELSE
                RETURN format('ROLE ''%%I'' ALREADY EXISTS', rolename);
            END IF;
        END;
        $$
        LANGUAGE plpgsql;

        SELECT create_role_if_not_exists('api_server');
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO api_server;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO api_server;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO api_server;
        '''
        )


def downgrade():
    pass
