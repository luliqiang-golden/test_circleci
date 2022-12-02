"""adjust HCR for send/receive to/from processor activity

Revision ID: d1b02172157c
Revises: 739daca8387f
Create Date: 2022-02-24 02:30:31.540155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1b02172157c'
down_revision = '739daca8387f'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
                unpackaged_extracts_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_shipped_cultivators_processors,0)/1000,
                
                
                
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
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_shipped_cultivators_processors,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested' AND T1.unit NOT IN ('distilled', 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_cultivators_processors
                
                FROM (
                
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
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
                        	orders.shipping_status IN ('shipped', 'delivered') AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND
                        	accounts.account_type IN ('distributor','license holder','retailer') AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                            
                     UNION ALL 
                     
                     SELECT 
                        CAST(act.data->>'from_qty' AS DECIMAL) AS to_qty, 
                        act.data->>'from_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
                        FROM activities AS act
                        INNER JOIN stats_taxonomies AS st ON st.name = act.data->>'from_qty_unit' AND st.organization_id = act.organization_id
                        WHERE act.name = 'send_processor' AND
                              act.organization_id = org_id AND
                              TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                      
            
        END;$function$
;







CREATE OR REPLACE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_domestic = COALESCE(T3.unpackaged_extracts_inhaled_received_domestic ,0)/1000,
                    unpackaged_extracts_ingested_received_domestic = COALESCE(T3.unpackaged_extracts_ingested_received_domestic,0)/1000,
                    unpackaged_extracts_other_received_domestic = COALESCE(T3.unpackaged_extracts_other_received_domestic ,0)/1000,
                    unpackaged_edibles_solid_received_domestic = COALESCE(T3.unpackaged_edibles_solid_received_domestic ,0)/1000,
                    unpackaged_edibles_nonsolid_received_domestic = COALESCE(T3.unpackaged_edibles_nonsolid_received_domestic ,0)/1000,
                    unpackaged_topicals_received_domestic = COALESCE(T3.unpackaged_topicals_received_domestic ,0)/1000,
                    
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_imported = COALESCE(T3.unpackaged_extracts_inhaled_received_imported ,0)/1000,
                    unpackaged_extracts_ingested_received_imported = COALESCE(T3.unpackaged_extracts_ingested_received_imported,0)/1000,
                    unpackaged_extracts_other_received_imported = COALESCE(T3.unpackaged_extracts_other_received_imported ,0)/1000,
                    unpackaged_edibles_solid_received_imported = COALESCE(T3.unpackaged_edibles_solid_received_imported ,0)/1000,
                    unpackaged_edibles_nonsolid_received_imported = COALESCE(T3.unpackaged_edibles_nonsolid_received_imported ,0)/1000,
                    unpackaged_topicals_received_imported = COALESCE(T3.unpackaged_topicals_received_imported ,0)/1000,

                    
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0),	
                    
                    packaged_extracts_inhaled_received_domestic = COALESCE(T3.packaged_extracts_inhaled_received_domestic ,0),
                    packaged_extracts_ingested_received_domestic = COALESCE(T3.packaged_extracts_ingested_received_domestic,0),
                    packaged_extracts_other_received_domestic = COALESCE(T3.packaged_extracts_other_received_domestic ,0),
                    packaged_edibles_solid_received_domestic = COALESCE(T3.packaged_edibles_solid_received_domestic ,0),
                    packaged_edibles_nonsolid_received_domestic = COALESCE(T3.packaged_edibles_nonsolid_received_domestic ,0),
                    packaged_topicals_received_domestic = COALESCE(T3.packaged_topicals_received_domestic ,0)
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
            
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_topicals_received_domestic,
                        
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_inhaled_received_imported,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_ingested_received_imported,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_other_received_imported,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_solid_received_imported,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_nonsolid_received_imported,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_topicals_received_imported,
                        
                        
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic,
                        
                        SUM(COALESCE(T2.extracts_inhaled_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_topicals_received_domestic
                        
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,		
                            
                            SUM(COALESCE((f).extracts_inhaled_weight,0)) AS extracts_inhaled_weight,
                            SUM(COALESCE((f).extracts_inhaled_qty, 0)) AS extracts_inhaled_qty,	
                            SUM(COALESCE((f).extracts_ingested_weight,0)) AS extracts_ingested_weight,
                            SUM(COALESCE((f).extracts_ingested_qty, 0)) AS extracts_ingested_qty,	
                            SUM(COALESCE((f).extracts_other_weight,0)) AS extracts_other_weight,
                            SUM(COALESCE((f).extracts_other_qty, 0)) AS extracts_other_qty,	
                            SUM(COALESCE((f).edibles_solid_weight,0)) AS edibles_solid_weight,
                            SUM(COALESCE((f).edibles_solid_qty, 0)) AS edibles_solid_qty,	
                            SUM(COALESCE((f).edibles_non_solid_weight,0)) AS edibles_non_solid_weight,
                            SUM(COALESCE((f).edibles_non_solid_qty, 0)) AS edibles_non_solid_qty,
                            SUM(COALESCE((f).topicals_weight,0)) AS topicals_weight,
                            SUM(COALESCE((f).topicals_qty, 0)) AS topicals_qty,
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f,
                            (f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype')).fresh_cannabis_weight,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' NOT IN ('Canada', 'ca', 'canada') THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            --FROM f_inventories_latest_stats_stage('2021-06-30', 1) as inv
                            FROM f_inventories_latest_stats_stage(final_date, org_id)  as inv
                                INNER JOIN activities AS act ON (act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)) 
                                OR (act.name = 'receive_processor' and act.data->>'to_inventory_id' = CAST(inv.id AS VARCHAR))
                                LEFT JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                                inner join stats_taxonomies as st on st.name = inv.latest_unit AND st.organization_id = org.id
                            WHERE type IN ('received inventory', 'batch') AND 
                                --inv.organization_id = 1 AND
						                            --inv.timestamp >= cast('2021-11-01' as date)
	                            inv.organization_id = org_id AND
	                            inv.timestamp >= cast(initial_date as date)
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
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
   	sift DECIMAL;
	terpene DECIMAL;
	biomass DECIMAL;
	cannabinoid DECIMAL;
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
   
   sift := 0;
    IF (unit = 'sift') THEN
        sift := GREATEST(0,quantity);
    END IF;
   
   cannabinoid := 0;
    IF (unit = 'cannabinoid') THEN
        cannabinoid := GREATEST(0,quantity);
    END IF;
   
   biomass := 0;
    IF (unit = 'biomass') THEN
        biomass := GREATEST(0,quantity);
    END IF;
   
   terpene := 0;
    IF (unit = 'terpene') THEN
        terpene := GREATEST(0,quantity);
    END IF;

    extracts_weight := distilled + crude + sift + cannabinoid + biomass + terpene;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested' AND unit NOT IN ('distilled', 'crude')) THEN
        extracts_ingested_weight := GREATEST(0,quantity);
    END IF;

    extracts_other_weight := 0;
    IF (taxonomy_subtype = 'other' AND unit NOT IN ('sift', 'cannabinoid', 'biomass', 'terpene')) THEN
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
    connection.execute(
        """
        
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
                        	orders.shipping_status IN ('shipped', 'delivered') AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND
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
















CREATE OR REPLACE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_domestic = COALESCE(T3.unpackaged_extracts_inhaled_received_domestic ,0)/1000,
                    unpackaged_extracts_ingested_received_domestic = COALESCE(T3.unpackaged_extracts_ingested_received_domestic,0)/1000,
                    unpackaged_extracts_other_received_domestic = COALESCE(T3.unpackaged_extracts_other_received_domestic ,0)/1000,
                    unpackaged_edibles_solid_received_domestic = COALESCE(T3.unpackaged_edibles_solid_received_domestic ,0)/1000,
                    unpackaged_edibles_nonsolid_received_domestic = COALESCE(T3.unpackaged_edibles_nonsolid_received_domestic ,0)/1000,
                    unpackaged_topicals_received_domestic = COALESCE(T3.unpackaged_topicals_received_domestic ,0)/1000,
                    
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_imported = COALESCE(T3.unpackaged_extracts_inhaled_received_imported ,0)/1000,
                    unpackaged_extracts_ingested_received_imported = COALESCE(T3.unpackaged_extracts_ingested_received_imported,0)/1000,
                    unpackaged_extracts_other_received_imported = COALESCE(T3.unpackaged_extracts_other_received_imported ,0)/1000,
                    unpackaged_edibles_solid_received_imported = COALESCE(T3.unpackaged_edibles_solid_received_imported ,0)/1000,
                    unpackaged_edibles_nonsolid_received_imported = COALESCE(T3.unpackaged_edibles_nonsolid_received_imported ,0)/1000,
                    unpackaged_topicals_received_imported = COALESCE(T3.unpackaged_topicals_received_imported ,0)/1000,
                    
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0),	
                    
                    packaged_extracts_inhaled_received_domestic = COALESCE(T3.packaged_extracts_inhaled_received_domestic ,0),
                    packaged_extracts_ingested_received_domestic = COALESCE(T3.packaged_extracts_ingested_received_domestic,0),
                    packaged_extracts_other_received_domestic = COALESCE(T3.packaged_extracts_other_received_domestic ,0),
                    packaged_edibles_solid_received_domestic = COALESCE(T3.packaged_edibles_solid_received_domestic ,0),
                    packaged_edibles_nonsolid_received_domestic = COALESCE(T3.packaged_edibles_nonsolid_received_domestic ,0),
                    packaged_topicals_received_domestic = COALESCE(T3.packaged_topicals_received_domestic ,0)
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
            
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_topicals_received_domestic,
                        
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_inhaled_received_imported,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_ingested_received_imported,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_other_received_imported,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_solid_received_imported,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_nonsolid_received_imported,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_topicals_received_imported,
                        
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic,
                        
                        SUM(COALESCE(T2.extracts_inhaled_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_topicals_received_domestic
                        
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,		
                            
                            SUM(COALESCE((f).extracts_inhaled_weight,0)) AS extracts_inhaled_weight,
                            SUM(COALESCE((f).extracts_inhaled_qty, 0)) AS extracts_inhaled_qty,	
                            SUM(COALESCE((f).extracts_ingested_weight,0)) AS extracts_ingested_weight,
                            SUM(COALESCE((f).extracts_ingested_qty, 0)) AS extracts_ingested_qty,	
                            SUM(COALESCE((f).extracts_other_weight,0)) AS extracts_other_weight,
                            SUM(COALESCE((f).extracts_other_qty, 0)) AS extracts_other_qty,	
                            SUM(COALESCE((f).edibles_solid_weight,0)) AS edibles_solid_weight,
                            SUM(COALESCE((f).edibles_solid_qty, 0)) AS edibles_solid_qty,	
                            SUM(COALESCE((f).edibles_non_solid_weight,0)) AS edibles_non_solid_weight,
                            SUM(COALESCE((f).edibles_non_solid_qty, 0)) AS edibles_non_solid_qty,
                            SUM(COALESCE((f).topicals_weight,0)) AS topicals_weight,
                            SUM(COALESCE((f).topicals_qty, 0)) AS topicals_qty,
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f,
                            (f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype')).fresh_cannabis_weight,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' NOT IN ('Canada', 'ca', 'canada') THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            --FROM f_inventories_latest_stats_stage('2021-06-30', 1) as inv
                            FROM f_inventories_latest_stats_stage(final_date, org_id)  as inv
                                INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
                                INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                                inner join stats_taxonomies as st on st.name = inv.latest_unit AND st.organization_id = org.id
                            WHERE type = 'received inventory' AND 
                                --inv.organization_id = 1 AND
						                            --inv.timestamp >= cast('2021-11-01' as date)
	                            inv.organization_id = org_id AND
	                            inv.timestamp >= cast(initial_date as date)
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
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
