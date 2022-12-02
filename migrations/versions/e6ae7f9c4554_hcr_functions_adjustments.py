"""HCR functions adjustments

Revision ID: e6ae7f9c4554
Revises: 1668ea6d6344
Create Date: 2022-02-21 17:54:21.300154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6ae7f9c4554'
down_revision = '1668ea6d6344'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0),
                    unpackaged_vegetative_plants_packaged_label = COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0),
                    unpackaged_whole_cannabis_plants_packaged_label = COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0),
                    unpackaged_fresh_cannabis_packaged_label = COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000,
                    unpackaged_dried_cannabis_packaged_label = COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000,
                    --unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                    packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                    packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                    packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                    packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                    --packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0),
                    
                    unpackaged_edibles_solid_packaged_label = COALESCE(T2.unpackaged_edibles_solid_packaged_label,0)/1000,
                    unpackaged_edibles_nonsolid_packaged_label = COALESCE(T2.unpackaged_edibles_nonsolid_packaged_label,0)/1000,
                    unpackaged_extracts_inhaled_packaged_label = COALESCE(T2.unpackaged_extracts_inhaled_packaged_label,0)/1000,
                    unpackaged_extracts_ingested_packaged_label = COALESCE(T2.unpackaged_extracts_ingested_packaged_label,0)/1000,
                    unpackaged_extracts_other_packaged_label = COALESCE(T2.unpackaged_extracts_other_packaged_label,0)/1000,
                    unpackaged_topicals_packaged_label = COALESCE(T2.unpackaged_topicals_packaged_label,0)/1000,
                    
                    packaged_edibles_solid_quantity_packaged = COALESCE(T2.packaged_edibles_solid_quantity_packaged,0),
                    packaged_edibles_nonsolid_quantity_packaged = COALESCE(T2.packaged_edibles_nonsolid_quantity_packaged,0),
                    packaged_extracts_inhaled_quantity_packaged = COALESCE(T2.packaged_extracts_inhaled_quantity_packaged,0),
                    packaged_extracts_ingested_quantity_packaged = COALESCE(T2.packaged_extracts_ingested_quantity_packaged,0),
                    packaged_extracts_other_quantity_packaged = COALESCE(T2.packaged_extracts_other_quantity_packaged,0),
                    packaged_topicals_quantity_packaged = COALESCE(T2.packaged_topicals_quantity_packaged,0)
                    
                FROM (
                    SELECT 
                         -- unpackaged packaged label
                        0 AS unpackaged_seed_packaged_label,		
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_packaged_label,
                        0 AS unpackaged_whole_cannabis_plants_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_packaged_label,
                        --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
                        
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_packaged_label,
                        
                        -- quantity packaged label
                        0 AS packaged_seed_quantity_packaged,		
                        COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_quantity_packaged,		 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_quantity_packaged,
                        --COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_quantity_packaged
                    
                    FROM (
                        SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
                        WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
                        (orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') OR (orders.shipping_address->>'country' IS NULL AND orders.shipping_status IS NULL)) AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
;

















CREATE OR REPLACE FUNCTION public.f_inventories_latest_stats_stage(final_date character varying, org_id integer)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, type character varying, variety character varying, data jsonb, stats jsonb, attributes jsonb, latest_quantity numeric, latest_unit character varying, latest_stage character varying, from_qty_unit character varying, package_type character varying, shipping_status character varying)
 LANGUAGE plpgsql
AS $function$
    BEGIN
    /* this function gets the latest stats and stage of every inventory, returns the inventory properties + latest_quantity + latest_unit + latest_stage
    we mainly need this to know what was the values in a certain period
    say that we have an inventory that has 10 plants in august, but in september 10 plants is detroyed and its stats become 0, so if we want the report of aug
    it will be not accurate based on its stats, so that's why we rely on the inventory_adjustment and update_stage activities to get the latest stats and stage in the period required. */
    RETURN QUERY
        SELECT 
            inv.*,
            CAST(act_stats.data->>'quantity' AS DECIMAL) AS latest_quantity,
            CAST(act_stats.data->>'unit' AS VARCHAR) AS latest_unit,
            CAST(act_stage.data->>'to_stage' AS VARCHAR) AS latest_stage,
            CAST(act_samples.data->>'from_qty_unit' AS VARCHAR) AS from_qty_unit,
            s.package_type as package_type,
            orders.shipping_status 
        FROM inventories AS inv 
        INNER JOIN (	  
            SELECT 
                CAST(a_stats.data->>'inventory_id' AS bigint) AS inventory_id,
                MAX(a_stats.id) AS id
            FROM activities AS a_stats
            WHERE 
                a_stats.name = 'inventory_adjustment' AND
                CAST(a_stats.data->>'quantity' AS DECIMAL) >= 0	AND
                TO_CHAR(a_stats.timestamp,'YYYY-MM-DD') <= final_date AND
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
            TO_CHAR(a_stage.timestamp,'YYYY-MM-DD') <= final_date AND
            a_stage.organization_id = org_id
            GROUP BY a_stage.data->>'inventory_id'
            
        ) AS t1 ON t1.inventory_id = inv.id
        LEFT JOIN activities AS act_stage ON act_stage.id = t1.id
    	LEFT JOIN skus as s ON s.id = cast(inv.data->>'sku_id' AS bigint)
    	LEFT JOIN order_items as order_items ON order_items.id = cast(inv.data->>'order_item_id' as bigint)
    	LEFT JOIN orders as orders ON orders.id = order_items.order_id
    	LEFT JOIN activities AS act_samples ON inv.id = cast(act_samples.data->>'to_inventory_id' AS BIGINT) AND act_samples.name IN ('batch_create_sample');
    END;
    $function$
;


        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0),
                    unpackaged_vegetative_plants_packaged_label = COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0),
                    unpackaged_whole_cannabis_plants_packaged_label = COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0),
                    unpackaged_fresh_cannabis_packaged_label = COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000,
                    unpackaged_dried_cannabis_packaged_label = COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000,
                    --unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                    packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                    packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                    packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                    packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                    --packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0),
                    
                    unpackaged_edibles_solid_packaged_label = COALESCE(T2.unpackaged_edibles_solid_packaged_label,0)/1000,
                    unpackaged_edibles_nonsolid_packaged_label = COALESCE(T2.unpackaged_edibles_nonsolid_packaged_label,0)/1000,
                    unpackaged_extracts_inhaled_packaged_label = COALESCE(T2.unpackaged_extracts_inhaled_packaged_label,0)/1000,
                    unpackaged_extracts_ingested_packaged_label = COALESCE(T2.unpackaged_extracts_ingested_packaged_label,0)/1000,
                    unpackaged_extracts_other_packaged_label = COALESCE(T2.unpackaged_extracts_other_packaged_label,0)/1000,
                    unpackaged_topicals_packaged_label = COALESCE(T2.unpackaged_topicals_packaged_label,0)/1000,
                    
                    packaged_edibles_solid_quantity_packaged = COALESCE(T2.packaged_edibles_solid_quantity_packaged,0),
                    packaged_edibles_nonsolid_quantity_packaged = COALESCE(T2.packaged_edibles_nonsolid_quantity_packaged,0),
                    packaged_extracts_inhaled_quantity_packaged = COALESCE(T2.packaged_extracts_inhaled_quantity_packaged,0),
                    packaged_extracts_ingested_quantity_packaged = COALESCE(T2.packaged_extracts_ingested_quantity_packaged,0),
                    packaged_extracts_other_quantity_packaged = COALESCE(T2.packaged_extracts_other_quantity_packaged,0),
                    packaged_topicals_quantity_packaged = COALESCE(T2.packaged_topicals_quantity_packaged,0)
                    
                FROM (
                    SELECT 
                         -- unpackaged packaged label
                        0 AS unpackaged_seed_packaged_label,		
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_packaged_label,
                        0 AS unpackaged_whole_cannabis_plants_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_packaged_label,
                        --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
                        
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_packaged_label,
                        
                        -- quantity packaged label
                        0 AS packaged_seed_quantity_packaged,		
                        COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_quantity_packaged,		 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_quantity_packaged,
                        --COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_quantity_packaged
                    
                    FROM (
                        SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
                        WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
                        (orders.shipping_address->>'country' = 'ca' OR (orders.shipping_address->>'country' IS NULL AND orders.shipping_status IS NULL)) AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
;





















CREATE OR REPLACE FUNCTION public.f_inventories_latest_stats_stage(final_date character varying, org_id integer)
 RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, type character varying, variety character varying, data jsonb, stats jsonb, attributes jsonb, latest_quantity numeric, latest_unit character varying, latest_stage character varying, from_qty_unit character varying, package_type character varying, shipping_status character varying)
 LANGUAGE plpgsql
AS $function$
                        BEGIN
                        /* this function gets the latest stats and stage of every inventory, returns the inventory properties + latest_quantity + latest_unit + latest_stage
                        we mainly need this to know what was the values in a certain period
                        say that we have an inventory that has 10 plants in august, but in september 10 plants is detroyed and its stats become 0, so if we want the report of aug
                        it will be not accurate based on its stats, so that's why we rely on the inventory_adjustment and update_stage activities to get the latest stats and stage in the period required. */
                        RETURN QUERY
                            SELECT 
                                inv.*,
                                ROUND(CAST(act_stats.data->>'quantity' AS DECIMAL)) AS latest_quantity,
                                CAST(act_stats.data->>'unit' AS VARCHAR) AS latest_unit,
                                CAST(act_stage.data->>'to_stage' AS VARCHAR) AS latest_stage,
                                CAST(act_samples.data->>'from_qty_unit' AS VARCHAR) AS from_qty_unit,
                                s.package_type as package_type,
                                orders.shipping_status 
                            FROM inventories AS inv 
                            INNER JOIN (	  
                                SELECT 
                                    CAST(a_stats.data->>'inventory_id' AS bigint) AS inventory_id,
                                    MAX(a_stats.id) AS id
                                FROM activities AS a_stats
                                WHERE 
                                    a_stats.name = 'inventory_adjustment' AND
                                    CAST(a_stats.data->>'quantity' AS DECIMAL) >= 0	AND
                                    TO_CHAR(a_stats.timestamp,'YYYY-MM-DD') <= final_date AND
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
                                TO_CHAR(a_stage.timestamp,'YYYY-MM-DD') <= final_date AND
                                a_stage.organization_id = org_id
                                GROUP BY a_stage.data->>'inventory_id'
                                
                            ) AS t1 ON t1.inventory_id = inv.id
                            LEFT JOIN activities AS act_stage ON act_stage.id = t1.id
                        	LEFT JOIN skus as s ON s.id = cast(inv.data->>'sku_id' AS bigint)
                        	LEFT JOIN order_items as order_items ON order_items.id = cast(inv.data->>'order_item_id' as bigint)
                        	LEFT JOIN orders as orders ON orders.id = order_items.order_id
                        	LEFT JOIN activities AS act_samples ON inv.id = cast(act_samples.data->>'to_inventory_id' AS BIGINT) AND act_samples.name IN ('batch_create_sample');
                        END;
                        $function$
;

        """
    )
