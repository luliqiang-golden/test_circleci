"""fix rounding issues HCR functions and shipment issues HCR

Revision ID: 0974fad7e63d
Revises: 4de25abe5ae9
Create Date: 2022-11-07 17:51:20.505161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0974fad7e63d'
down_revision = '4de25abe5ae9'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
        CREATE INDEX activities_name ON public.activities USING btree (name);
        
        
        
        
        
        
        
        
        
        

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_domestic(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged shipped domestic
	            SET enable_nestloop = off;
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
                        COUNT(*) FILTER (WHERE T1.unit = 'plants' AND T1.package_type = 'packaged') AS packaged_vegetative_plants_shipped_domestic, 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.package_type = 'packaged') AS packaged_fresh_cannabis_shipped_domestic, 
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.package_type = 'packaged') AS packaged_dried_cannabis_shipped_domestic, 
                        COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.package_type = 'packaged') AS packaged_extracts_shipped_domestic,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid') AND T1.package_type = 'packaged') AS packaged_edibles_solid_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.package_type = 'packaged') AS packaged_edibles_nonsolid_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.package_type = 'packaged') AS packaged_extracts_inhaled_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested') AND T1.package_type = 'packaged') AS packaged_extracts_ingested_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other') AND T1.package_type = 'packaged') AS packaged_extracts_other_shipped_domestic,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals') AND T1.package_type = 'packaged') AS packaged_topicals_shipped_domestic
                    FROM (
                        SELECT act_map.data->>'inventory_id' AS inventory_id, inv.latest_unit AS unit, st.data->>'subtype' AS subtype, inv.package_type AS package_type
                            FROM activities AS act
                            INNER JOIN order_items AS oi ON act.data->>'shipment_id' = CAST(oi.shipment_id AS varchar)
                            INNER JOIN activities AS act_map ON CAST(oi.id AS varchar) = act_map.data->>'order_item_id' AND act_map.name = 'order_item_map_to_lot_item'
                            INNER JOIN f_inventories_latest_stats_stage(final_date, org_id) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                            INNER JOIN stats_taxonomies st ON st.name = inv.latest_unit AND st.organization_id = act.organization_id 
                            --INNER JOIN f_inventories_latest_stats_stage('2020-05-31', 1) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                        WHERE act.name = 'shipment_shipped' AND
                            --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            act."timestamp" BETWEEN cast(initial_date as "timestamp") AND cast(final_date as "timestamp")
                    ) AS T1   
                ) AS T2
                WHERE id = report_id;	
                
            END;$function$
;


        
        
        
        
        
        
        
        DROP FUNCTION f_inventories_latest_stats_stage(character varying,integer);
        
        
        
        
        
        
        
        
        
        
        CREATE OR REPLACE FUNCTION public.f_inventories_latest_stats_stage(final_date character varying, org_id integer)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, type character varying, variety character varying, data jsonb, stats jsonb, attributes jsonb, latest_quantity numeric, latest_unit character varying, latest_stage character varying, from_qty_unit character varying, package_type character varying, shipping_status character  VARYING, shipped_date timestamp with time zone)
 LANGUAGE plpgsql
AS $function$
    BEGIN
    /* this function gets the latest stats and stage of every inventory, returns the inventory properties + latest_quantity + latest_unit + latest_stage
    we mainly need this to know what was the values in a certain period
    say that we have an inventory that has 10 plants in august, but in september 10 plants is detroyed and its stats become 0, so if we want the report of aug
    it will be not accurate based on its stats, so that's why we rely on the inventory_adjustment and update_stage activities to get the latest stats and stage in the period required. */
    RETURN QUERY
        SELECT 
            inv.id,
            inv.organization_id,
            inv.created_by,
            inv."timestamp",
            inv."name",
            inv."type",
            inv.variety,
            inv."data",
            inv.stats,
            inv."attributes",
            CAST(act_stats.data->>'quantity' AS DECIMAL) AS latest_quantity,
            CAST(act_stats.data->>'unit' AS VARCHAR) AS latest_unit,
            CAST(act_stage.data->>'to_stage' AS VARCHAR) AS latest_stage,
            CAST(act_samples.data->>'from_qty_unit' AS VARCHAR) AS from_qty_unit,
            s.package_type as package_type,
            orders.shipping_status,
            shipments.shipped_date
        FROM inventories AS inv 
        INNER JOIN (	  
            SELECT 
                CAST(a_stats.data->>'inventory_id' AS bigint) AS inventory_id,
                MAX(a_stats.id) AS id
            FROM activities AS a_stats
            WHERE 
                a_stats.name = 'inventory_adjustment' AND
                CAST(a_stats.data->>'quantity' AS DECIMAL) >= 0	AND
                a_stats.timestamp <= CAST(final_date AS "timestamp") AND
                a_stats.organization_id = org_id
            GROUP BY a_stats.data->>'inventory_id'
        ) AS t2 ON t2.inventory_id = inv.id
        INNER JOIN activities AS act_stats ON act_stats.id = t2.id
        LEFT JOIN (	  
        SELECT 
                CAST(a_stage.data->>'inventory_id' AS bigint) AS inventory_id,
                MAX(a_stage.id) AS id
            FROM activities AS a_stage
            WHERE 
            a_stage.name = 'update_stage' AND
            a_stage.timestamp <= CAST(final_date AS "timestamp") AND
            a_stage.organization_id = org_id
            GROUP BY a_stage.data->>'inventory_id'
            
        ) AS t1 ON t1.inventory_id = inv.id
        LEFT JOIN activities AS act_stage ON act_stage.id = t1.id
    	LEFT JOIN skus as s ON s.id = cast(inv.data->>'sku_id' AS bigint)
    	LEFT JOIN order_items as order_items ON order_items.id = cast(inv.data->>'order_item_id' as bigint)
    	LEFT JOIN orders as orders ON orders.id = order_items.order_id
    	LEFT JOIN activities AS act_samples ON inv.id = cast(act_samples.data->>'to_inventory_id' AS BIGINT) AND act_samples.name IN ('create_sample')
    	LEFT JOIN shipments AS shipments ON order_items.shipment_id = shipments.id;
    END;
    $function$
;










CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_purchased_hemp_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT unpackaged_extracts_inhaled_inventory numeric, OUT unpackaged_extracts_ingested_inventory numeric, OUT unpackaged_extracts_other_inventory numeric, OUT unpackaged_edibles_solid_inventory numeric, OUT unpackaged_edibles_nonsolid_inventory numeric, OUT unpackaged_topicals_inventory numeric, OUT unpackaged_other_inventory numeric, OUT packaged_extracts_inhaled_inventory numeric, OUT packaged_extracts_ingested_inventory numeric, OUT packaged_extracts_other_inventory numeric, OUT packaged_edibles_solid_inventory numeric, OUT packaged_edibles_nonsolid_inventory numeric, OUT packaged_topicals_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric, OUT packaged_extracts_inhaled_inventory_weight numeric, OUT packaged_extracts_ingested_inventory_weight numeric, OUT packaged_extracts_other_inventory_weight numeric, OUT packaged_edibles_solid_inventory_weight numeric, OUT packaged_edibles_nonsolid_inventory_weight numeric, OUT packaged_topicals_inventory_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
            DECLARE
                initial_date character varying;
                final_day numeric;
            BEGIN
	            
	            IF(DATE_PART('day', CAST(final_date AS TIMESTAMP)) = '1') THEN
	            	SELECT to_timestamp(final_date, 'YYYY-MM-DD H:M:S') 
                                - interval '1 month' INTO initial_date;
	            ELSE
	            	SELECT to_timestamp(final_date, 'YYYY-MM-DD H:M:S') 
                                + interval '1 day'
                                - interval '1 month' INTO initial_date;
	            END IF;
                            
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE((f).seeds_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_seed_inventory,
                    SUM(COALESCE((f).vegetative_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_vegetative_plants_inventory,		
                    SUM(COALESCE((f).whole_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_whole_cannabis_plants_inventory,
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).purchased_hemp_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_purchased_hemp_inventory,
                    SUM(COALESCE((f).dried_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_topicals_inventory,
                    SUM(COALESCE((f).other_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_other_inventory,
                    
                    -- packaged (#)
                    SUM(COALESCE((f).packaged_seeds_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_seed_inventory,
                    SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_vegetative_plants_inventory,				
                    SUM(COALESCE((f).fresh_cannabis_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).dried_cannabis_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_topicals_inventory,
                    
                    
                    -- packaged weight(#)
                    SUM(COALESCE((f).seeds_qty,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_seed_inventory_weight, -- total number of seeds
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_fresh_cannabis_inventory_weight,
                    SUM(COALESCE((f).dried_cannabis_weight,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_dried_cannabis_inventory_weight,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_inventory_weight,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_inhaled_inventory_weight,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_ingested_inventory_weight,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_extracts_other_inventory_weight,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_edibles_solid_inventory_weight,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_edibles_nonsolid_inventory_weight,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (((f).shipping_status IS NULL OR (f).shipping_status IN ('cancelled', 'pending')) OR ((f).shipping_status IN ('shipped', 'delivered') AND shipped_date NOT BETWEEN CAST(initial_date AS timestamp) AND CAST(final_date AS timestamp)))) AS packaged_topicals_inventory_weight
            
                FROM (
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data, inv.shipped_date
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv 
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1)  
                    WHERE inv.latest_quantity > 0 and
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            --inv.timestamp >= cast(initial_date as date) AND
                        type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    --samples that have not been sent to the lab and do not come from plants
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data, inv.shipped_date
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1) as inv
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    INNER JOIN (
                        SELECT 
                            CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                            MAX(sample_activity.id) AS act_id
                        FROM activities AS sample_activity
                        WHERE 
                            sample_activity.name in ('create_sample', 'sample_sent_to_lab') 
                            AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= final_date
                            --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                            --AND sample_activity.data->>'from_qty_unit' != 'plants'
                        GROUP BY sample_activity.data->>'inventory_id'
                    ) AS latest_activity ON inv.id = latest_activity.id
                    INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='create_sample' 
                    WHERE inv.latest_quantity > 0 AND
                          inv.type ='sample' AND
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id 
                            --AND inv.timestamp >= cast(initial_date as date) 
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' 
                        
            
                    ) AS T1
                    INTO
                        unpackaged_seed_inventory,
                        unpackaged_vegetative_plants_inventory,		
                        unpackaged_whole_cannabis_plants_inventory,
                        unpackaged_fresh_cannabis_inventory,
                        unpackaged_purchased_hemp_inventory,
                        unpackaged_dried_cannabis_inventory,
                        unpackaged_extracts_inventory,
                        
                        unpackaged_extracts_inhaled_inventory,
                        unpackaged_extracts_ingested_inventory,		
                        unpackaged_extracts_other_inventory,
                        unpackaged_edibles_solid_inventory,
                        unpackaged_edibles_nonsolid_inventory,
                        unpackaged_topicals_inventory,
                        unpackaged_other_inventory,
                        
                        --Packaged (#)
                        packaged_seed_inventory,
                        packaged_vegetative_plants_inventory,				
                        packaged_fresh_cannabis_inventory,
                        packaged_dried_cannabis_inventory,
                        packaged_extracts_inventory,
                        
                        packaged_extracts_inhaled_inventory, 
                        packaged_extracts_ingested_inventory, 
                        packaged_extracts_other_inventory, 
                        packaged_edibles_solid_inventory,
                        packaged_edibles_nonsolid_inventory, 
                        packaged_topicals_inventory,
                        
                        
                        --packaged weight(#)
                        packaged_seed_inventory_weight,
                        packaged_fresh_cannabis_inventory_weight,
                        packaged_dried_cannabis_inventory_weight,
                        packaged_extracts_inventory_weight,
                        
                        packaged_extracts_inhaled_inventory_weight, 
                        packaged_extracts_ingested_inventory_weight, 
                        packaged_extracts_other_inventory_weight, 
                        packaged_edibles_solid_inventory_weight,
                        packaged_edibles_nonsolid_inventory_weight, 
                        packaged_topicals_inventory_weight;
             
            END;$function$
;


















        """
    )


def downgrade():
    pass
