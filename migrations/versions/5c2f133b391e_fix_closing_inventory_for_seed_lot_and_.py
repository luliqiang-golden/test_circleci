"""fix closing inventory for seed lot and lot item

Revision ID: 5c2f133b391e
Revises: 1322ab9d5794
Create Date: 2022-10-10 20:46:17.394331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c2f133b391e'
down_revision = '61a7792a04ed'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT purchased_hemp_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT purchased_hemp_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT shipping_status character varying, OUT other_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    plants DECIMAL;
    dry DECIMAL;
    cured DECIMAL;
    distilled DECIMAL;
    crude DECIMAL;
    cannabinoid DECIMAL;
    sift DECIMAL;
    terpene DECIMAL;
    biomass DECIMAL;
BEGIN
	
	shipping_status = p_shipping_status;
	
	package_type := 'unpackage';
	
    seeds_qty := 0;
    IF (unit = 'seeds') THEN
        seeds_qty := GREATEST(0,quantity);
    END IF;

    IF (seeds_qty > 0) THEN
        IF (type = 'received inventory') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(data->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
        ELSIF (type = 'batch') THEN
            IF (attributes->>'seed_weight' IS NOT NULL) THEN
                seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
            ELSE
                seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seeds_weight' AS DECIMAL), 0));
            END IF;
        ELSIF (type = 'sample') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL), 0));
        ELSIF (type = 'lot') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
        ELSIF (type = 'lot item') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
        ELSE
            seeds_weight := 0;
        END IF;
    END IF;

    plants := 0;
    IF (unit = 'plants') THEN
        plants := GREATEST(0,quantity);
    END IF;

    IF (plants > 0) THEN
            IF ((stage in ('planning', 'propagation', 'germinating', 'vegetation') OR type IN ('received inventory', 'mother', 'mother batch', 'lot', 'lot item'))) OR (data->'plan'->>'end_type'='plants') THEN
                vegetative_plants := plants;
            ELSE
                whole_plants := plants;
            END IF;
    END IF;

    fresh_cannabis_weight := 0;
    IF (unit = 'g-wet' AND (from_qty_unit != 'plants' OR from_qty_unit IS NULL)) THEN
        fresh_cannabis_weight := GREATEST(0,quantity);
    END IF;
   
   	purchased_hemp_weight := 0;
  	IF (unit = 'purchasedHemp') THEN
        purchased_hemp_weight := GREATEST(0,quantity);
    END IF;

    dry := 0;
    IF (unit = 'dry') THEN
        dry := GREATEST(0,quantity);
    END IF;

    cured := 0;
    IF (unit = 'cured') THEN
        cured := GREATEST(0,quantity);
    END IF;

    dried_cannabis_weight := dry + cured;


    distilled := 0;
    IF (unit = 'distilled') THEN
        distilled := GREATEST(0,quantity);
    END IF;

    crude := 0;
    IF (unit = 'crude') THEN
        crude := GREATEST(0,quantity);
    END IF;
	
	cannabinoid := 0;
    IF (unit = 'cannabinoid') THEN
        cannabinoid := GREATEST(0,quantity);
    END IF;
	
	sift := 0;
    IF (unit = 'sift') THEN
        sift := GREATEST(0,quantity);
    END IF;
	
	terpene := 0;
    IF (unit = 'terpene') THEN
        terpene := GREATEST(0,quantity);
    END IF;
	
	biomass := 0;
    IF (unit = 'biomass') THEN
        biomass := GREATEST(0,quantity);
    END IF;

    extracts_weight := distilled + crude; --+ cannabinoid + sift + terpene + biomass;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested' AND (unit NOT IN ('crude', 'distilled') OR (unit IN ('crude', 'distilled') AND type = 'lot item' AND p_package_type != 'unpackaged'))) THEN
        extracts_ingested_weight := GREATEST(0,quantity);
    END IF;

    extracts_other_weight := 0;
    IF (taxonomy_subtype = 'other') THEN
        extracts_other_weight := GREATEST(0,quantity);
    END IF;

    edibles_solid_weight := 0;
    IF (taxonomy_subtype = 'solid') THEN
        edibles_solid_weight := GREATEST(0,quantity);
    END IF;

    edibles_non_solid_weight := 0;
    IF (taxonomy_subtype = 'nonsolid') THEN
        edibles_non_solid_weight := GREATEST(0,quantity);
    END IF;

    topicals_weight := 0;
    IF (taxonomy_subtype = 'topicals') THEN
        topicals_weight := GREATEST(0,quantity);
    END IF;

   	other_weight := 0;
   	IF(type = 'sample' AND unit = 'g-wet' AND from_qty_unit = 'plants') THEN 
   		other_weight := GREATEST(0,quantity);
   	END IF;


    IF (type = 'lot item') then
    	
    	if(p_package_type = 'packaged') then
    		package_type = 'package';
    	else
    		package_type = 'unpackage';
    	end if;
    
    	IF (seeds_qty > 0) THEN
            packaged_seeds_qty := 1;
        ELSIF (fresh_cannabis_weight > 0) THEN
            fresh_cannabis_qty := 1;
        ELSIF (dried_cannabis_weight > 0) THEN
            dried_cannabis_qty := 1;
        --ELSIF (extracts_weight > 0) THEN
        --    extracts_qty := 1;
        ELSIF (plants > 0) THEN
            packaged_vegetative_plants_qty := 1;
        ELSIF (extracts_inhaled_weight > 0) THEN
            extracts_inhaled_qty := 1;
        ELSIF (extracts_ingested_weight > 0) THEN
            extracts_ingested_qty := 1;
        ELSIF (extracts_other_weight > 0  AND (unit NOT IN ('cannabinoid', 'sift', 'terpene', 'biomass'))) THEN
            extracts_other_qty := 1;
        ELSIF (edibles_solid_weight > 0) THEN
            edibles_solid_qty := 1;
        ELSIF (edibles_non_solid_weight > 0) THEN
            edibles_non_solid_qty := 1;
        ELSIF (topicals_weight > 0) THEN
            topicals_qty := 1;
        END if;
    END IF;

END;
$function$
;









CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
	            SET enable_nestloop = off;
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0)/1000,
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
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'seeds') AS unpackaged_seed_packaged_label,		
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
                        COUNT(*) FILTER (WHERE T1.unit = 'seeds') AS packaged_seed_quantity_packaged,		
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
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
;










CREATE OR REPLACE FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
               BEGIN		
               --closing inventory
               UPDATE health_canada_report
               SET 
                   -- unpackage (kg)
                   unpackaged_seed_closing_inventory = COALESCE(T1.unpackaged_seed_inventory,0)/1000,
                   unpackaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_vegetative_plants_inventory,0),
                   unpackaged_whole_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_whole_cannabis_plants_inventory,0),
                   unpackaged_fresh_cannabis_closing_inventory = COALESCE(T1.unpackaged_fresh_cannabis_inventory,0)/1000,
                   unpackaged_purchased_hemp_closing_inventory = COALESCE(T1.unpackaged_purchased_hemp_inventory,0)/1000,
                   unpackaged_dried_cannabis_closing_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
                   unpackaged_extracts_closing_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
                   unpackaged_extracts_inhaled_closing_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
                   unpackaged_extracts_ingested_closing_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
                   unpackaged_extracts_other_closing_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
                   unpackaged_edibles_solid_closing_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
                   unpackaged_edibles_nonsolid_closing_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
                   unpackaged_topicals_closing_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,
                   unpackaged_other_closing_inventory = COALESCE(T1.unpackaged_other_inventory,0)/1000,
                   
                   -- packaged (#)
                   packaged_seed_closing_inventory = COALESCE(T1.packaged_seed_inventory,0),
                   packaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T1.packaged_vegetative_plants_inventory,0),
                   packaged_fresh_cannabis_closing_inventory = COALESCE(T1.packaged_fresh_cannabis_inventory,0),
                   packaged_dried_cannabis_closing_inventory = COALESCE(T1.packaged_dried_cannabis_inventory,0),
                   packaged_extracts_closing_inventory = COALESCE(T1.packaged_extracts_inventory,0),
                   packaged_edibles_solid_closing_inventory = COALESCE(T1.packaged_edibles_solid_inventory,0),
                   packaged_edibles_nonsolid_closing_inventory = COALESCE(T1.packaged_edibles_nonsolid_inventory,0),
                   packaged_extracts_inhaled_closing_inventory = COALESCE(T1.packaged_extracts_inhaled_inventory,0),
                   packaged_extracts_ingested_closing_inventory = COALESCE(T1.packaged_extracts_ingested_inventory,0),
                   packaged_extracts_other_closing_inventory = COALESCE(T1.packaged_extracts_other_inventory,0),
                   packaged_topicals_closing_inventory = COALESCE(T1.packaged_topicals_inventory,0),
                   
                   -- packaged weight (kg)
                   packaged_seed_closing_inventory_weight = COALESCE(T1.packaged_seed_inventory_weight,0)/1000,-- total number of seeds
                   packaged_fresh_cannabis_closing_inventory_weight = COALESCE(T1.packaged_fresh_cannabis_inventory_weight,0)/1000,
                   packaged_dried_cannabis_closing_inventory_weight = COALESCE(T1.packaged_dried_cannabis_inventory_weight,0)/1000,
                   packaged_extracts_closing_inventory_weight = COALESCE(T1.packaged_extracts_inventory_weight,0)/1000,
                   packaged_edibles_solid_closing_inventory_weight = COALESCE(T1.packaged_edibles_solid_inventory_weight,0)/1000,
                   packaged_edibles_nonsolid_closing_inventory_weight = COALESCE(T1.packaged_edibles_nonsolid_inventory_weight,0)/1000,
                   packaged_extracts_inhaled_closing_inventory_weight = COALESCE(T1.packaged_extracts_inhaled_inventory_weight,0)/1000,
                   packaged_extracts_ingested_closing_inventory_weight = COALESCE(T1.packaged_extracts_ingested_inventory_weight,0)/1000,
                   packaged_extracts_other_closing_inventory_weight = COALESCE(T1.packaged_extracts_other_inventory_weight,0)/1000,
                   packaged_topicals_inventory_closing_weight = COALESCE(T1.packaged_topicals_inventory_weight,0)/1000
               FROM (
                   --SELECT * FROM f_get_current_inventory('2021-05-31', 1)
                   SELECT * FROM f_get_current_inventory(final_date, org_id)
               ) AS T1
               WHERE id = report_id;	
            END;$function$
;










CREATE OR REPLACE FUNCTION public.f_test_report_result(report_id integer)
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
            DECLARE
                return_values TEXT[] := ARRAY[]::TEXT[];
                opening_value DECIMAL;
                adition_value DECIMAL;
                reduction_value DECIMAL;
                closing_value DECIMAL;
                text_value varchar;
                var1 DECIMAL;
                var2 DECIMAL;
                var3 DECIMAL;
            BEGIN
    
                -- unpackage seeds
                SELECT
                    --opening
                    unpackaged_seed_opening_inventory,
                    --adition
                    (unpackaged_seed_produced+
                    unpackaged_seed_received_domestic+
                    unpackaged_seed_received_imported+
                    unpackaged_seed_received_returned),
                    --reduction
                    (unpackaged_seed_destroyed +
                    unpackaged_seed_packaged_label +
                    unpackaged_seed_shipped_analytical_testers +
                    unpackaged_seed_reductions_shipped_returned+
                    unpackaged_seeds_shipped_exported+
                    unpackaged_seed_processed),
                    --closing
                    unpackaged_seed_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
    
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Seeds calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- unpackage vegetative plants
                SELECT
    
                    --opening
                    unpackaged_vegetative_plants_opening_inventory,
                    --adition
                    (unpackaged_vegetative_plants_produced+
                    unpackaged_vegetative_plants_received_domestic+
                    unpackaged_vegetative_plants_received_imported+
                    unpackaged_vegetative_plants_received_returned+
                    unpackaged_vegetative_plants_other_additions),
                    --reduction
                    (unpackaged_vegetative_plants_processed+
                    unpackaged_vegetative_plants_packaged_label+
                    unpackaged_vegetative_plants_shipped_cultivators_processors+
                    unpackaged_vegetative_plants_shipped_researchers+
                    unpackaged_vegetative_cannabis_plants_shipped_exported+
                    unpackaged_vegetative_plants_destroyed+
                    unpackaged_vegetative_plants_reductions_shipped_returned+
                    unpackaged_vegetative_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_vegetative_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Vegetative Cannabis Plants calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- unpackage whole plants
                SELECT
                    --opening
                    unpackaged_whole_cannabis_plants_opening_inventory,
                    --adition
                    (unpackaged_whole_cannabis_plants_produced+
                    unpackaged_whole_cannabis_plants_received_domestic+
                    unpackaged_whole_cannabis_plants_received_imported+
                    unpackaged_whole_cannabis_plants_received_returned),
                    --reduction
                    (unpackaged_whole_cannabis_plants_processed+
                    unpackaged_whole_cannabis_plants_packaged_label+
                    unpackaged_whole_cannabis_plants_destroyed+
                    unpackaged_whole_cannabis_plants_shipped_exported+
                    unpackaged_whole_cannabis_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_whole_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Whole Cannabis Plants calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- unpackaged fresh cannabis
                SELECT
                    --opening
                    unpackaged_fresh_cannabis_opening_inventory,
                    --adition
                    (unpackaged_fresh_cannabis_produced+
                    unpackaged_fresh_cannabis_received_domestic+
                    unpackaged_fresh_cannabis_received_imported+
                    unpackaged_fresh_cannabis_received_returned),
                    --reduction
                    (unpackaged_fresh_cannabis_processed+
                    unpackaged_fresh_cannabis_packaged_label+
                    unpackaged_fresh_cannabis_adjustment_loss+
                    unpackaged_fresh_cannabis_reductions_shipped_returned+
                    unpackaged_fresh_shipped_cultivators_processors+
                    unpackaged_fresh_cannabis_shipped_exported+
                    unpackaged_fresh_shipped_researchers+
                    unpackaged_fresh_cannabis_destroyed+
                    unpackaged_fresh_shipped_analytical_testers),
                    --closing
                    unpackaged_fresh_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Fresh Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
               
               
               
               
               -- unpackaged purchased hemp
                SELECT
                    --opening
                    unpackaged_purchased_hemp_opening_inventory,
                    --adition
                    (
                    unpackaged_purchased_hemp_received_domestic+
                    unpackaged_purchased_hemp_received_imported),
                    --reduction
                    (unpackaged_purchased_hemp_processed+
                    unpackaged_purchased_hemp_adjustment_loss+
                    unpackaged_purchased_hemp_reductions_shipped_returned+
                    unpackaged_purchased_hemp_shipped_cultivators_processors+
                    unpackaged_purchased_hemp_shipped_exported+
                    unpackaged_purchased_hemp_shipped_researchers+
                    unpackaged_purchased_hemp_destroyed+
                    unpackaged_purchased_hemp_shipped_analytical_testers),
                    --closing
                    unpackaged_purchased_hemp_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Fresh Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- unpackaged dried cannabis
                SELECT
                    --opening
                    unpackaged_dried_cannabis_opening_inventory,
                    --adition
                    (unpackaged_dried_cannabis_produced+
                    unpackaged_dried_cannabis_received_domestic+
                    unpackaged_dried_cannabis_received_imported+
                    unpackaged_dried_cannabis_received_returned),
                    --reduction
                    (unpackaged_dried_cannabis_processed+
                    unpackaged_dried_cannabis_packaged_label+
                    unpackaged_dried_cannabis_adjustment_loss+
                    unpackaged_dried_cannabis_destroyed+
                    unpackaged_dried_shipped_cultivators_processors+
                    unpackaged_dried_cannabis_shipped_exported+
                    unpackaged_dried_shipped_researchers+
                    unpackaged_dried_cannabis_reductions_shipped_returned+
                    unpackaged_dried_shipped_analytical_testers),
                    --closing
                    unpackaged_dried_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Dried Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- unpackaged extracts cannabis
                SELECT
                    --opening
                    unpackaged_extracts_opening_inventory,
                    --adition
                    (unpackaged_extracts_produced+
                    unpackaged_extracts_received_domestic+
                    unpackaged_extracts_received_imported+
                    unpackaged_extracts_received_returned),
                    --reduction
                    (
                    unpackaged_edibles_solid_processed+
                    unpackaged_edibles_nonsolid_processed+
                    unpackaged_extracts_ingested_processed+
                    unpackaged_extracts_inhaled_processed+
                    unpackaged_extracts_other_processed+
                    unpackaged_extracts_shipped_cultivators_processors+
                    unpackaged_extracts_shipped_researchers+
                    unpackaged_topicals_processed+
                    unpackaged_extracts_packaged_label+
                    unpackaged_pure_intermediate_reductions_other+
                    unpackaged_extracts_adjustment_loss+
                    unpackaged_extracts_reductions_shipped_returned+
                    unpackaged_extracts_destroyed+
                    unpackaged_extracts_shipped_analytical_testers),
                    --closing
                    unpackaged_extracts_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Pure Intermediate calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- unpackaged extracts inhaled
                SELECT
                    --opening
                    unpackaged_extracts_inhaled_opening_inventory,
                    --adition
                    (unpackaged_extracts_inhaled_produced+
                    unpackaged_extracts_inhaled_received_domestic+
                    unpackaged_extracts_inhaled_received_imported),
                    --reduction
                    (unpackaged_extracts_inhaled_packaged_label+
                    unpackaged_extracts_inhaled_adjustment_loss+
                    unpackaged_extracts_inhaled_shipped_researchers+
                    unpackaged_extracts_inhaled_shipped_cultivators_processors+
                    unpackaged_extracts_inhaled_shipped_exported+
                    unpackaged_extracts_inhaled_destroyed+
                    unpackaged_extracts_inhaled_reductions_shipped_returned+
                    unpackaged_extracts_inhaled_analytical_testers),
                    --closing
                    unpackaged_extracts_inhaled_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Extracts Inhaled calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- unpackaged extracts other
                SELECT
                    --opening
                    unpackaged_extracts_other_opening_inventory,
                    --adition
                    (unpackaged_extracts_other_produced+
                    unpackaged_extracts_other_received_domestic+
                    unpackaged_extracts_other_received_imported),
                    --reduction
                    (unpackaged_extracts_other_packaged_label+
                    unpackaged_extracts_other_adjustment_loss+
                    unpackaged_extracts_other_destroyed+
                    unpackaged_extracts_other_reductions_shipped_returned+
                    unpackaged_extracts_other_analytical_testers),
                    --closing
                    unpackaged_extracts_other_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Extracts Other calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- Packaged seeds
                SELECT
                    --opening
                    packaged_seed_opening_inventory,
                    --adition
                    (packaged_seed_received_domestic+
                    packaged_seed_received_returned+
                    packaged_seed_quantity_packaged),
                    --reduction
                    (packaged_seed_destroyed+
                    packaged_seed_shipped_domestic),
                    --closing
                    packaged_seed_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Pacakged Seeds calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
    
                -- Packaged vegetative plants
                SELECT
                    --opening
                    packaged_vegetative_plants_opening_inventory,
                    --adition
                    (packaged_vegetative_plants_received_domestic+
                    packaged_vegetative_plants_received_returned+
                    packaged_vegetative_plants_quantity_packaged),
                    --reduction
                    (packaged_vegetative_plants_destroyed+
                    packaged_vegetative_plants_shipped_domestic),
                    --closing
                    packaged_vegetative_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Vegetative Cannabis Plants calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- Packaged fresh cannabis
                SELECT
                    --opening
                    packaged_fresh_cannabis_opening_inventory,
                    --adition
                    (packaged_fresh_cannabis_received_domestic+
                    packaged_fresh_cannabis_received_returned+
                    packaged_fresh_cannabis_quantity_packaged),
                    --reduction
                    (packaged_fresh_cannabis_destroyed+
                    packaged_fresh_cannabis_shipped_domestic),
                    --closing
                    packaged_fresh_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Fresh Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- Packaged dried cannabis
                SELECT
                    --opening
                    packaged_dried_cannabis_opening_inventory,
                    --adition
                    (packaged_dried_cannabis_received_domestic+
                    packaged_dried_cannabis_received_returned+
                    packaged_dried_cannabis_quantity_packaged),
                    --reduction
                    (packaged_dried_cannabis_destroyed+
                    packaged_dried_cannabis_shipped_domestic),
                    --closing
                    packaged_dried_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Dried Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- Packaged extracts cannabis
                SELECT
                    --opening
                    packaged_extracts_ingested_opening_inventory,
                    --adition
                    (packaged_extracts_ingested_received_domestic +
                    packaged_extracts_ingested_quantity_packaged),
                    --reduction
                    (packaged_extracts_ingested_destroyed +
                    packaged_extracts_ingested_shipped_domestic),
                    --closing
                    packaged_extracts_ingested_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Ingested (oil) calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
               -- Packaged extracts inhaled
                SELECT
                    --opening
                    packaged_extracts_inhaled_opening_inventory,
                    --adition
                    (packaged_extracts_inhaled_received_domestic+
                    packaged_extracts_inhaled_quantity_packaged),
                    --reduction
                    (packaged_extracts_inhaled_destroyed+
                    packaged_extracts_inhaled_shipped_domestic),
                    --closing
                    packaged_extracts_inhaled_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Inhaled calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
               -- Packaged extracts other
                SELECT
                    --opening
                    packaged_extracts_other_opening_inventory,
                    --adition
                    (packaged_extracts_other_received_domestic+
                    packaged_extracts_other_quantity_packaged),
                    --reduction
                    (packaged_extracts_other_destroyed+
                    packaged_extracts_other_shipped_domestic),
                    --closing
                    packaged_extracts_other_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Other calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                RETURN return_values;
            END ;
    
            $function$
;










CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_destroyed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            --destroyed
	        SET enable_nestloop = off;
	       
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_destroyed = COALESCE(T2.unpackaged_seed_destroyed,0)/1000,
                unpackaged_vegetative_plants_destroyed = COALESCE(T2.unpackaged_vegetative_plants_destroyed,0),
                unpackaged_whole_cannabis_plants_destroyed = COALESCE(T2.unpackaged_whole_cannabis_plants_destroyed,0),
                unpackaged_fresh_cannabis_destroyed = COALESCE(T2.unpackaged_fresh_cannabis_destroyed,0)/1000,
                unpackaged_purchased_hemp_destroyed = COALESCE(T2.unpackaged_purchased_hemp_destroyed,0)/1000,
                unpackaged_dried_cannabis_destroyed = COALESCE(T2.unpackaged_dried_cannabis_destroyed,0)/1000,
                unpackaged_extracts_destroyed = COALESCE(T2.unpackaged_extracts_destroyed,0)/1000,
                
                unpackaged_edibles_solid_destroyed = COALESCE(T2.unpackaged_edibles_solid_destroyed,0)/1000,
                unpackaged_edibles_nonsolid_destroyed = COALESCE(T2.unpackaged_edibles_nonsolid_destroyed,0)/1000,
                unpackaged_extracts_inhaled_destroyed = COALESCE(T2.unpackaged_extracts_inhaled_destroyed,0)/1000,
                unpackaged_extracts_ingested_destroyed = COALESCE(T2.unpackaged_extracts_ingested_destroyed,0)/1000,
                unpackaged_extracts_other_destroyed = COALESCE(T2.unpackaged_extracts_other_destroyed,0)/1000,
                unpackaged_topicals_destroyed = COALESCE(T2.unpackaged_topicals_destroyed,0)/1000,
                
                packaged_seed_destroyed = COALESCE(T2.packaged_seed_destroyed,0),
                packaged_vegetative_plants_destroyed = COALESCE(T2.packaged_vegetative_plants_destroyed,0),
                packaged_fresh_cannabis_destroyed = COALESCE(T2.packaged_fresh_cannabis_destroyed,0),
                packaged_dried_cannabis_destroyed = COALESCE(T2.packaged_dried_cannabis_destroyed,0),
                packaged_extracts_destroyed = COALESCE(T2.packaged_extracts_destroyed,0),
                
                packaged_edibles_solid_destroyed = COALESCE(T2.packaged_edibles_solid_destroyed,0)/1000,
                packaged_edibles_nonsolid_destroyed = COALESCE(T2.packaged_edibles_nonsolid_destroyed,0)/1000,
                packaged_extracts_inhaled_destroyed = COALESCE(T2.packaged_extracts_inhaled_destroyed,0)/1000,
                packaged_extracts_ingested_destroyed = COALESCE(T2.packaged_extracts_ingested_destroyed,0)/1000,
                packaged_extracts_other_destroyed = COALESCE(T2.packaged_extracts_other_destroyed,0)/1000,
                packaged_topicals_destroyed = COALESCE(T2.packaged_topicals_destroyed,0)/1000
            FROM (
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE(T1.weight_destroyed,T1.quantity,0)) FILTER (WHERE T1.unit = 'seeds' AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'g-wet' AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'purchasedHemp' AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_purchased_hemp_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'solid') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null) AND T1.unit NOT IN ('crude', 'distilled')) AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'other') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null) AND T1.unit NOT IN ('sift', 'terpene', 'biomass', 'cannabinoid')) AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND ((T1.type = 'lot item' and T1.package_type = 'unpackaged') or T1.package_type is null)) AS unpackaged_topicals_destroyed,
                    
                    -- packaged (#)
                    COUNT(*) FILTER (WHERE T1.unit = 'seeds' AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_seed_destroyed,			
                    COUNT(*) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_vegetative_plants_destroyed,					 
                    COUNT(*) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_whole_cannabis_plants_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_fresh_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_dried_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_extracts_destroyed,
                    
                    COUNT(*) FILTER (WHERE (T1.subtype = 'solid') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_edibles_solid_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_edibles_nonsolid_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_extracts_inhaled_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_extracts_ingested_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'other') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_extracts_other_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type = 'lot item' and T1.package_type = 'packaged') AS packaged_topicals_destroyed
                    
                FROM (
                    SELECT
                        CASE
                        /* receive inventory, mother and lot are always vegetative plants and do not have a stage associated with it
                         we need to know the stage before it was destroyed to know if it was vegetative or whole plants */
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation', 'qa') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot', 'lot item')))
                            THEN 'vegetative_plants'
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type not in ('received inventory', 'mother', 'mother batch', 'lot')))
                            THEN 'whole_plants'
                        ELSE T0.from_unit
                        END AS unit,
                        T0.*
                    FROM (
                        SELECT
                            CAST(act.data->>'from_qty' AS DECIMAL) AS quantity,
                            CAST(act.data->>'to_qty' AS DECIMAL) AS weight_destroyed,
                            act.data->>'from_qty_unit' AS from_unit,
                            inv.type AS type,
                            inv.data->'plan'->>'end_type' AS end_type,
                            st.data->>'subtype' as subtype,
                             s.package_type,
                            
                            (SELECT act_stage.data->>'to_stage' 
                            FROM activities AS act_stage 
                            WHERE act_stage.name = 'update_stage' AND 
                                    act_stage.data->>'inventory_id' = act.data->>'from_inventory_id' AND
                                    act_stage.timestamp <= act.timestamp
                            ORDER BY timestamp DESC
                            LIMIT 1	 		
                            ) AS last_stage_before_activity
                        FROM activities as act 
                        INNER JOIN inventories AS inv ON CAST(inv.id AS VARCHAR) = act.data->>'from_inventory_id'
                        inner join stats_taxonomies st on st.name = act.data->>'from_qty_unit' AND st.organization_id = org_id
                        left join skus s on CAST(inv."data"->>'sku_id' as numeric) = s.id
                        /* for destruction section we rely on queue_for_destruction activity, and prunning is not included because when we prune a plant, 
                        we don't destroy the entire plant but just small portion which does not count for the destruction section */
                        WHERE act.name ='queue_for_destruction' AND act.deleted = FALSE AND
                            act.data->>'reason_for_destruction' != 'pruning' AND
                            act.organization_id = org_id AND
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
        --					act.organization_id = 1 AND
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                    ) AS T0
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;
    
        """ )


def downgrade():
    pass