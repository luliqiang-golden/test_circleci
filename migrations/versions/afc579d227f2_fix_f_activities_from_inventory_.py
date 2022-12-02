"""fix f_activities_from_inventory function to handle same columns always

Revision ID: afc579d227f2
Revises: fb216d3fe2a5
Create Date: 2022-02-03 18:58:35.334785

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afc579d227f2'
down_revision = 'fb216d3fe2a5'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
        DROP FUNCTION f_activities_from_inventory(bigint);
        
        CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
        RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, inventory_id bigint)
        LANGUAGE plpgsql
        AS $function$
        begin
        return QUERY
            select act.id,
                act.organization_id,
                act.created_by,
                act."timestamp",
                act."name",
                act."data",
            CASE 
                WHEN 
                cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                THEN 
                cast(act.data->>'inventory_id' as bigint)
                ELSE 
                inv_id 
            END
            as inventory_id from activities as act 
            where
                (concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
                concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
                concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
                inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
                inv_id = cast(act.data->>'to_inventory_id' as integer) or
                inv_id = cast(act.data->>'inventory_id'as integer) or
                inv_id = cast(act.data->>'related_inventory_id' as integer) or
                inv_id = cast(act.data->>'linked_inventory_id' as integer));

        END;
        $function$
        ;
            
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
        DROP FUNCTION f_activities_from_inventory(bigint);
        
        CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
        RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, inventory_id bigint)
        LANGUAGE plpgsql
        AS $function$
        begin
        return QUERY
            select *, 
            CASE 
                WHEN 
                cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                THEN 
                cast(act.data->>'inventory_id' as bigint)
                ELSE 
                inv_id 
            END
            as inventory_id from activities as act 
            where
                (concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
                concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
                concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
                inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
                inv_id = cast(act.data->>'to_inventory_id' as integer) or
                inv_id = cast(act.data->>'inventory_id'as integer) or
                inv_id = cast(act.data->>'related_inventory_id' as integer) or
                inv_id = cast(act.data->>'linked_inventory_id' as integer));

        END;
        $function$
        ;

        """)
