"""new-end-types-hcr-shipped-domestic

Revision ID: 726050a7f1c9
Revises: bdd8b2345e34
Create Date: 2021-06-15 09:29:58.944695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '726050a7f1c9'
down_revision = 'bdd8b2345e34'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
                    packaged_extracts_shipped_domestic = COALESCE(T2.packaged_extracts_shipped_domestic ,0),
                    
                    packaged_edibles_solid_shipped_domestic = COALESCE(T2.packaged_edibles_solid_shipped_domestic ,0),
                    packaged_edibles_nonsolid_shipped_domestic = COALESCE(T2.packaged_edibles_nonsolid_shipped_domestic ,0),
                    packaged_extracts_inhaled_shipped_domestic = COALESCE(T2.packaged_extracts_inhaled_shipped_domestic ,0),
                    packaged_extracts_ingested_shipped_domestic = COALESCE(T2.packaged_extracts_ingested_shipped_domestic ,0),
                    packaged_extracts_other_shipped_domestic = COALESCE(T2.packaged_extracts_other_shipped_domestic ,0),
                    packaged_topicals_shipped_domestic = COALESCE(T2.packaged_topicals_shipped_domestic ,0)
                FROM (
                    SELECT 
                        COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_shipped_domestic, 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_shipped_domestic, 
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_shipped_domestic, 
                        COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_shipped_domestic,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_shipped_domestic
                    FROM (
                        SELECT act_map.data->>'inventory_id' AS inventory_id, inv.latest_unit AS unit, st.data->>'subtype' AS subtype
                            FROM activities AS act
                            INNER JOIN order_items AS oi ON act.data->>'shipment_id' = CAST(oi.shipment_id AS varchar)
                            INNER JOIN activities AS act_map ON CAST(oi.id AS varchar) = act_map.data->>'order_item_id' AND act_map.name = 'order_item_map_to_lot_item'
                            INNER JOIN f_inventories_latest_stats_stage(final_date) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                            INNER JOIN stats_taxonomies st ON st.name = inv.latest_unit
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
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
        """
    )
