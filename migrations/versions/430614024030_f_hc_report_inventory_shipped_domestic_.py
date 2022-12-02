"""f_hc_report_inventory_shipped_domestic_performancing_query

Revision ID: 430614024030
Revises: 9fda3a5d3b99
Create Date: 2021-12-01 21:07:38.866231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '430614024030'
down_revision = '9fda3a5d3b99'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_domestic(report_id integer, initial_date character varying, final_date character varying, org_id integer)
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
        BEGIN		
            -- packaged shipped domestic
            UPDATE health_canada_report
            SET 
                packaged_seed_shipped_domestic = 0, -- we don't sell seeds
                packaged_vegetative_plants_shipped_domestic = COALESCE(T2.packaged_vegetative_plants_shipped_domestic ,0),
                packaged_fresh_cannabis_shipped_domestic = COALESCE(T2.packaged_fresh_cannabis_shipped_domestic ,0),
                packaged_dried_cannabis_shipped_domestic = COALESCE(T2.packaged_dried_cannabis_shipped_domestic ,0),
                packaged_extracts_shipped_domestic = COALESCE(T2.packaged_extracts_shipped_domestic ,0)
            FROM (
                SELECT 
                    COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_shipped_domestic, 
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_shipped_domestic, 
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_shipped_domestic, 
                    COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_shipped_domestic
                FROM (
                    SELECT act_map.data->>'inventory_id' AS inventory_id, inv.latest_unit AS unit FROM activities AS act
                        INNER JOIN order_items AS oi ON act.data->>'shipment_id' = CAST(oi.shipment_id AS varchar)
                        INNER JOIN activities AS act_map ON CAST(oi.id AS varchar) = act_map.data->>'order_item_id' AND act_map.name = 'order_item_map_to_lot_item'
                        INNER JOIN f_inventories_latest_stats_stage(final_date) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                        --INNER JOIN f_inventories_latest_stats_stage('2020-05-31') AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                    WHERE act.name = 'shipment_shipped' AND
                        --inv.organization_id = 1 AND
                        --inv.timestamp >= cast('2021-11-01' as date)
                        inv.organization_id = org_id AND
                        inv.timestamp >= cast(initial_date as date)
                ) AS T1   
            ) AS T2
            WHERE id = report_id;	
        END;$function$
    ;
    """)
    pass


def downgrade():
    connection = op.get_bind()
    connection.execute("""
    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_domestic(report_id integer, initial_date character varying, final_date character varying, org_id integer)
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
        BEGIN		
            -- packaged shipped domestic
            UPDATE health_canada_report
            SET 
                packaged_seed_shipped_domestic = 0, -- we don't sell seeds
                packaged_vegetative_plants_shipped_domestic = COALESCE(T2.packaged_vegetative_plants_shipped_domestic ,0),
                packaged_fresh_cannabis_shipped_domestic = COALESCE(T2.packaged_fresh_cannabis_shipped_domestic ,0),
                packaged_dried_cannabis_shipped_domestic = COALESCE(T2.packaged_dried_cannabis_shipped_domestic ,0),
                packaged_extracts_shipped_domestic = COALESCE(T2.packaged_extracts_shipped_domestic ,0)
            FROM (
                SELECT 
                    COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_shipped_domestic, 
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_shipped_domestic, 
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_shipped_domestic, 
                    COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_shipped_domestic
                FROM (
                    SELECT act_map.data->>'inventory_id' AS inventory_id, inv.latest_unit AS unit FROM activities AS act
                        INNER JOIN order_items AS oi ON act.data->>'shipment_id' = CAST(oi.shipment_id AS varchar)
                        INNER JOIN activities AS act_map ON CAST(oi.id AS varchar) = act_map.data->>'order_item_id' AND act_map.name = 'order_item_map_to_lot_item'
                        INNER JOIN f_inventories_latest_stats_stage(final_date) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                        --INNER JOIN f_inventories_latest_stats_stage('2020-05-31') AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                    WHERE act.name = 'shipment_shipped' AND
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                        inv.organization_id = org_id AND
                        TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                ) AS T1   
            ) AS T2
            WHERE id = report_id;	
        END;$function$
    ;

    """)
    pass
