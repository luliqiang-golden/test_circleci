"""add created_at and updated_at to inventories table

Revision ID: 7056adecf391
Revises: afc579d227f2
Create Date: 2022-02-03 03:33:48.590960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7056adecf391'
down_revision = 'afc579d227f2'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
        ALTER TABLE activities 
        ADD COLUMN created_at timestamptz;

        ALTER TABLE activities 
        ADD COLUMN updated_at timestamptz;

        CREATE OR REPLACE FUNCTION public.trigger_created_at_activities()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
        NEW.created_at = NOW();
        NEW.updated_at = NOW();
        RETURN NEW;
        END;
        $function$
        ;

        CREATE OR REPLACE FUNCTION public.trigger_updated_at_activities()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
        END;
        $function$
        ;

        CREATE TRIGGER set_created_at_activities BEFORE
        INSERT
            ON
            public.activities FOR EACH ROW EXECUTE PROCEDURE trigger_created_at_activities();

        CREATE TRIGGER set_updated_at_activities BEFORE
        UPDATE
            ON
            public.activities FOR EACH ROW EXECUTE PROCEDURE trigger_updated_at_activities();
        
   
   
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
    """
        ALTER TABLE activities 
        DROP COLUMN created_at;

        ALTER TABLE activities 
        DROP COLUMN updated_at;

        DROP TRIGGER set_created_at_activities ON public.activities;
        DROP TRIGGER set_updated_at_activities ON public.activities;

        DROP FUNCTION public.trigger_created_at_activities();
        DROP FUNCTION public.trigger_updated_at_activities();
    """)

