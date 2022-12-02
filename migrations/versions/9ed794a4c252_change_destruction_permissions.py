"""change destruction permissions

Revision ID: 9ed794a4c252
Revises: 7bee62dc1a14
Create Date: 2022-07-14 17:03:38.748804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ed794a4c252'
down_revision = '7bee62dc1a14'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        '''
            UPDATE public."permission"
            SET name = 'qa_destruction_access', component_friendly_name='Destruction'
            WHERE name = 'qa_destruction_queue_access';

            DELETE FROM public."permission" WHERE name IN ('qa_destruction_reports_access', 'qa_destruction_history_access');
        '''
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        '''
            UPDATE public."permission"
            SET name = 'qa_destruction_queue_access', component_friendly_name='Destruction Queue'
            WHERE name = 'qa_destruction_access';

            INSERT INTO public."permission"
            (id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
            VALUES(21, '2022-04-29 12:07:37.099', 'qa_destruction_reports_access', 'subgroup'::public.resource_types, 'Destruction Reports', 4);
            INSERT INTO public."permission"
            (id, "timestamp", "name", resource_type, component_friendly_name,  parent_id)
            VALUES(22, '2022-04-29 12:07:37.099', 'qa_destruction_history_access', 'subgroup'::public.resource_types, 'Destruction History', 4);
        '''
    )
