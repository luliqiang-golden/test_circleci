"""fix activity log function for edited activities

Revision ID: 5e707e47852e
Revises: 9ed794a4c252
Create Date: 2022-07-21 18:26:37.829565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e707e47852e'
down_revision = '9ed794a4c252'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, edited boolean, deleted boolean, changed_at timestamp with time zone, changed_by integer, reason_for_modification text, inventory_id bigint)
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
                    act."edited",
                    act."deleted",
                    ah.changed_at,
                    ah.changed_by,
                    CAST(ah.reason_for_modification AS TEXT),
                    CASE 
                        WHEN 
                        cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                        THEN 
                        cast(act.data->>'inventory_id' as bigint)
                        ELSE 
                        inv_id 
                    END
                    as inventory_id from activities as act
                    LEFT JOIN (SELECT DISTINCT ON(h.activity_id) h.activity_id, h.changed_at, h.changed_by, h.reason_for_modification FROM activities_history h ORDER BY h.activity_id, h.changed_at DESC) AS ah 
                    ON act.id = ah.activity_id
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
        CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, edited boolean, deleted boolean, changed_at timestamp with time zone, changed_by integer, reason_for_modification text, inventory_id bigint)
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
                    act."edited",
                    act."deleted",
                    MAX(ah.changed_at),
                    MAX(ah.changed_by),
                    MAX(ah.reason_for_modification),
                    CASE 
                        WHEN 
                        cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                        THEN 
                        cast(act.data->>'inventory_id' as bigint)
                        ELSE 
                        inv_id 
                    END
                    as inventory_id from activities as act
                    LEFT JOIN activities_history ah 
                    ON act.id = ah.activity_id
                    where
                        (concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
                        inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
                        inv_id = cast(act.data->>'to_inventory_id' as integer) or
                        inv_id = cast(act.data->>'inventory_id'as integer) or
                        inv_id = cast(act.data->>'related_inventory_id' as integer) or
                        inv_id = cast(act.data->>'linked_inventory_id' as integer))
                        GROUP BY act.id, act.organization_id, act.created_by, act."timestamp", act."name", act."data", act."edited", act."deleted";

                END;
                $function$
;

        """)
