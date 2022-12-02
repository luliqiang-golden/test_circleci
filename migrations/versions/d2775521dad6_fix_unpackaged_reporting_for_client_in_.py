"""fix unpackaged reporting for client in canada

Revision ID: d2775521dad6
Revises: 3ce21d0ca605
Create Date: 2022-02-03 15:48:37.289691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2775521dad6'
down_revision = '3ce21d0ca605'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
"""
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
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
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
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;





CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export_value(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported_value = COALESCE(T2.unpackaged_seeds_shipped_exported_value,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported_value,0),
                unpackaged_whole_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported_value,0),
                unpackaged_fresh_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported_value,0)/1000,
                unpackaged_dried_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported_value,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_solids_shipped_exported_value,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported_value,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported_value = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported_value,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported_value = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported_value,0)/1000,
	            unpackaged_extracts_other_shipped_exported_value = COALESCE(T2.unpackaged_extracts_other_shipped_exported_value,0)/1000,
	            unpackaged_topicals_shipped_exported_value = COALESCE(T2.unpackaged_topicals_shipped_exported_value,0)/1000
                
                
            FROM (
                SELECT 
                    
                    0 AS unpackaged_seeds_shipped_exported_value,		
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported_value,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported_value,
                    --SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported_value
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type,
						order_items.price AS price
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
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

UPDATE skus s SET package_type = s.data->>'type';

CREATE OR REPLACE FUNCTION public.populate_package_type()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
   NEW.package_type = NEW.data->>'type';
  RETURN NEW;
END;
$function$
;

DROP TRIGGER populate_package_type ON public.skus;

CREATE TRIGGER populate_package_type BEFORE
INSERT
    ON
    public.skus FOR EACH ROW EXECUTE PROCEDURE populate_package_type();

""")


def downgrade():
    connection = op.get_bind()
    connection.execute(
"""

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
                                        WHEN crm.data->'residing_address'->>'country' != org.data->'facility_details'->'facilityAddress'->>'country'  THEN 'imported' 
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






CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export_value(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported_value = COALESCE(T2.unpackaged_seeds_shipped_exported_value,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported_value,0),
                unpackaged_whole_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported_value,0),
                unpackaged_fresh_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported_value,0)/1000,
                unpackaged_dried_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported_value,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_solids_shipped_exported_value,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported_value,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported_value = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported_value,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported_value = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported_value,0)/1000,
	            unpackaged_extracts_other_shipped_exported_value = COALESCE(T2.unpackaged_extracts_other_shipped_exported_value,0)/1000,
	            unpackaged_topicals_shipped_exported_value = COALESCE(T2.unpackaged_topicals_shipped_exported_value,0)/1000
                
                
            FROM (
                SELECT 
                    
                    0 AS unpackaged_seeds_shipped_exported_value,		
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported_value,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported_value,
                    --SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported_value
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type,
						order_items.price AS price
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


""")
