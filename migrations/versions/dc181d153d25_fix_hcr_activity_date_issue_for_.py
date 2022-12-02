"""fix_HCR_activity_date_issue_for_unpackaged_lot_items

Revision ID: dc181d153d25
Revises: aab9ae566158
Create Date: 2022-01-18 21:31:48.978910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc181d153d25'
down_revision = 'aab9ae566158'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
    
    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to cultivators and process
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_cultivators_processors = COALESCE(T2.unpackaged_seed_shipped_cultivators_processors,0),
                unpackaged_vegetative_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_vegetative_plants_shipped_cultivators_processors,0),
                unpackaged_whole_cannabis_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_cultivators_processors,0),
                unpackaged_fresh_shipped_cultivators_processors = COALESCE(T2.unpackaged_fresh_shipped_cultivators_processors,0)/1000,
                unpackaged_dried_shipped_cultivators_processors = COALESCE(T2.unpackaged_dried_shipped_cultivators_processors,0)/1000,
                --unpackaged_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_other_shipped_cultivators_processors,0)/1000,
                
                
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_solids_shipped_cultivators_processors,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_inhaled_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_inhaled_shipped_cultivators_processors,0)/1000,    
	            unpackaged_extracts_ingested_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_ingested_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_other_shipped_cultivators_processors,0)/1000,
	            unpackaged_topicals_shipped_cultivators_processors = COALESCE(T2.unpackaged_topicals_shipped_cultivators_processors,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_shipped_cultivators_processors,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_cultivators_processors,
					0 AS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_cultivators_processors
                
                FROM (
                
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name = 'create_lot_item' AND
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_status = 'shipped' AND 
                        	orders.shipping_address->>'country' = 'ca' AND
                        	accounts.account_type IN ('distributor','license holder','retailer') AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                      
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported = COALESCE(T2.unpackaged_seeds_shipped_exported,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported,0),
                unpackaged_whole_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported,0),
                unpackaged_fresh_cannabis_shipped_exported = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported,0)/1000,
                unpackaged_dried_cannabis_shipped_exported = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported = COALESCE(T2.unpackaged_edibles_solids_shipped_exported,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported,0)/1000,
	            unpackaged_extracts_other_shipped_exported = COALESCE(T2.unpackaged_extracts_other_shipped_exported,0)/1000,
	            unpackaged_topicals_shipped_exported = COALESCE(T2.unpackaged_topicals_shipped_exported,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seeds_shipped_exported,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' != 'ca' AND 
                        	orders.shipping_status = 'shipped' AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_researchers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_researchers = COALESCE(T2.unpackaged_seed_shipped_researchers,0),
                unpackaged_vegetative_plants_shipped_researchers = COALESCE(T2.unpackaged_vegetative_plants_shipped_researchers,0),
                unpackaged_whole_cannabis_plants_shipped_researchers = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_researchers,0),
                unpackaged_fresh_shipped_researchers = COALESCE(T2.unpackaged_fresh_shipped_researchers,0)/1000,
                unpackaged_dried_shipped_researchers = COALESCE(T2.unpackaged_dried_shipped_researchers,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_researchers = COALESCE(T2.unpackaged_edibles_solids_shipped_researchers,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_researchers = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_researchers,0)/1000,
	            unpackaged_extracts_inhaled_shipped_researchers = COALESCE(T2.unpackaged_extracts_inhaled_shipped_researchers,0)/1000,    
	            unpackaged_extracts_ingested_shipped_researchers = COALESCE(T2.unpackaged_extracts_ingested_shipped_researchers,0)/1000,
	            unpackaged_extracts_other_shipped_researchers = COALESCE(T2.unpackaged_extracts_other_shipped_researchers,0)/1000,
	            unpackaged_topicals_shipped_researchers = COALESCE(T2.unpackaged_topicals_shipped_researchers,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seed_shipped_researchers,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_researchers,
					0 AS unpackaged_whole_cannabis_plants_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_researchers,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_researchers
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	accounts.account_type = 'researcher' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' = 'ca' AND 
                        	orders.shipping_status = 'shipped' AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT other_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    plants DECIMAL;
    dry DECIMAL;
    cured DECIMAL;
    distilled DECIMAL;
    crude DECIMAL;
BEGIN
	
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

    --extracts_weight := distilled + crude;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested') THEN
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
    
        IF (fresh_cannabis_weight > 0) THEN
            fresh_cannabis_qty := 1;
        ELSIF (dried_cannabis_weight > 0) THEN
            dried_cannabis_qty := 1;
        ELSIF (extracts_weight > 0) THEN
            extracts_qty := 1;
        ELSIF (plants > 0) THEN
            packaged_vegetative_plants_qty := 1;

        ELSIF (extracts_inhaled_weight > 0) THEN
            extracts_inhaled_qty := 1;
        ELSIF (extracts_ingested_weight > 0) THEN
            extracts_ingested_qty := 1;
        ELSIF (extracts_other_weight > 0) THEN
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


    
                       """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
    
    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to cultivators and process
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_cultivators_processors = COALESCE(T2.unpackaged_seed_shipped_cultivators_processors,0),
                unpackaged_vegetative_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_vegetative_plants_shipped_cultivators_processors,0),
                unpackaged_whole_cannabis_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_cultivators_processors,0),
                unpackaged_fresh_shipped_cultivators_processors = COALESCE(T2.unpackaged_fresh_shipped_cultivators_processors,0)/1000,
                unpackaged_dried_shipped_cultivators_processors = COALESCE(T2.unpackaged_dried_shipped_cultivators_processors,0)/1000,
                --unpackaged_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_other_shipped_cultivators_processors,0)/1000,
                
                
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_solids_shipped_cultivators_processors,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_inhaled_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_inhaled_shipped_cultivators_processors,0)/1000,    
	            unpackaged_extracts_ingested_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_ingested_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_other_shipped_cultivators_processors,0)/1000,
	            unpackaged_topicals_shipped_cultivators_processors = COALESCE(T2.unpackaged_topicals_shipped_cultivators_processors,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_shipped_cultivators_processors,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_cultivators_processors,
					0 AS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_cultivators_processors
                
                FROM (
                
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
                        WHERE act.name = 'create_lot_item' AND
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_status = 'shipped' AND 
                        	orders.shipping_address->>'country' = 'ca' AND
                        	accounts.account_type IN ('distributor','license holder','retailer') AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                      
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported = COALESCE(T2.unpackaged_seeds_shipped_exported,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported,0),
                unpackaged_whole_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported,0),
                unpackaged_fresh_cannabis_shipped_exported = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported,0)/1000,
                unpackaged_dried_cannabis_shipped_exported = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported = COALESCE(T2.unpackaged_edibles_solids_shipped_exported,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported,0)/1000,
	            unpackaged_extracts_other_shipped_exported = COALESCE(T2.unpackaged_extracts_other_shipped_exported,0)/1000,
	            unpackaged_topicals_shipped_exported = COALESCE(T2.unpackaged_topicals_shipped_exported,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seeds_shipped_exported,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' != 'ca' AND 
                        	orders.shipping_status = 'shipped' AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_researchers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_researchers = COALESCE(T2.unpackaged_seed_shipped_researchers,0),
                unpackaged_vegetative_plants_shipped_researchers = COALESCE(T2.unpackaged_vegetative_plants_shipped_researchers,0),
                unpackaged_whole_cannabis_plants_shipped_researchers = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_researchers,0),
                unpackaged_fresh_shipped_researchers = COALESCE(T2.unpackaged_fresh_shipped_researchers,0)/1000,
                unpackaged_dried_shipped_researchers = COALESCE(T2.unpackaged_dried_shipped_researchers,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_researchers = COALESCE(T2.unpackaged_edibles_solids_shipped_researchers,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_researchers = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_researchers,0)/1000,
	            unpackaged_extracts_inhaled_shipped_researchers = COALESCE(T2.unpackaged_extracts_inhaled_shipped_researchers,0)/1000,    
	            unpackaged_extracts_ingested_shipped_researchers = COALESCE(T2.unpackaged_extracts_ingested_shipped_researchers,0)/1000,
	            unpackaged_extracts_other_shipped_researchers = COALESCE(T2.unpackaged_extracts_other_shipped_researchers,0)/1000,
	            unpackaged_topicals_shipped_researchers = COALESCE(T2.unpackaged_topicals_shipped_researchers,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seed_shipped_researchers,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_researchers,
					0 AS unpackaged_whole_cannabis_plants_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_researchers,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_researchers
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
                        WHERE act.name ='create_lot_item' AND 
                        	accounts.account_type = 'researcher' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' = 'ca' AND 
                        	orders.shipping_status = 'shipped' AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;


CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT other_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    plants DECIMAL;
    dry DECIMAL;
    cured DECIMAL;
    distilled DECIMAL;
    crude DECIMAL;
BEGIN
	
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

    --extracts_weight := distilled + crude;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested') THEN
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
    	
    	if((p_package_type = 'unpackaged' and p_shipping_status = 'shipped') or p_package_type = 'packaged') then
    		package_type = 'package';
    	else
    		package_type = 'unpackage';
    	end if;
    
        IF (fresh_cannabis_weight > 0) THEN
            fresh_cannabis_qty := 1;
        ELSIF (dried_cannabis_weight > 0) THEN
            dried_cannabis_qty := 1;
        ELSIF (extracts_weight > 0) THEN
            extracts_qty := 1;
        ELSIF (plants > 0) THEN
            packaged_vegetative_plants_qty := 1;

        ELSIF (extracts_inhaled_weight > 0) THEN
            extracts_inhaled_qty := 1;
        ELSIF (extracts_ingested_weight > 0) THEN
            extracts_ingested_qty := 1;
        ELSIF (extracts_other_weight > 0) THEN
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


    
                       """)
