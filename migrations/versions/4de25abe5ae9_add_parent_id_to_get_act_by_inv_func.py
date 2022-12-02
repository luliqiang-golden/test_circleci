"""add parent id to get act by inv func

Revision ID: 4de25abe5ae9
Revises: 5c2f133b391e
Create Date: 2022-11-03 13:10:38.772991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4de25abe5ae9'
down_revision = '5c2f133b391e'
branch_labels = None
depends_on = None


def upgrade():
     connection = op.get_bind()
     connection.execute(
        """
        DROP FUNCTION public.f_activities_from_inventory(bigint);
CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, edited boolean, deleted boolean, parent_id bigint, changed_at timestamp with time zone, changed_by integer, reason_for_modification text, inventory_id bigint)
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
                    act."parent_id",
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

        
        """
    )


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

        
        """
    )
