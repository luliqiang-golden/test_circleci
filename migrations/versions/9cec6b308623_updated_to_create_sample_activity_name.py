"""Updated batch_create_name activity name to create_sample

Revision ID: 9cec6b308623
Revises: 89515362c3ef
Create Date: 2022-05-20 19:34:14.644950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cec6b308623'
down_revision = '89515362c3ef'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
UPDATE activities
            SET name = 'create_sample'
            WHERE name = 'batch_create_sample';

UPDATE activities SET data = jsonb_set(data, '{activity_name}', '"create_sample"', TRUE)
WHERE data->>'activity_name'='batch_create_sample';

CREATE OR REPLACE FUNCTION public.f_get_current_inventory(
	final_date character varying,
	org_id integer,
	OUT unpackaged_seed_inventory numeric,
	OUT unpackaged_vegetative_plants_inventory numeric,
	OUT unpackaged_whole_cannabis_plants_inventory numeric,
	OUT unpackaged_fresh_cannabis_inventory numeric,
	OUT unpackaged_extracts_inventory numeric,
	OUT unpackaged_dried_cannabis_inventory numeric,
	OUT packaged_seed_inventory numeric,
	OUT packaged_vegetative_plants_inventory numeric,
	OUT packaged_fresh_cannabis_inventory numeric,
	OUT packaged_dried_cannabis_inventory numeric,
	OUT packaged_extracts_inventory numeric,
	OUT unpackaged_extracts_inhaled_inventory numeric,
	OUT unpackaged_extracts_ingested_inventory numeric,
	OUT unpackaged_extracts_other_inventory numeric,
	OUT unpackaged_edibles_solid_inventory numeric,
	OUT unpackaged_edibles_nonsolid_inventory numeric,
	OUT unpackaged_topicals_inventory numeric,
	OUT unpackaged_other_inventory numeric,
	OUT packaged_extracts_inhaled_inventory numeric,
	OUT packaged_extracts_ingested_inventory numeric,
	OUT packaged_extracts_other_inventory numeric,
	OUT packaged_edibles_solid_inventory numeric,
	OUT packaged_edibles_nonsolid_inventory numeric,
	OUT packaged_topicals_inventory numeric,
	OUT packaged_seed_inventory_weight numeric,
	OUT packaged_fresh_cannabis_inventory_weight numeric,
	OUT packaged_dried_cannabis_inventory_weight numeric,
	OUT packaged_extracts_inventory_weight numeric,
	OUT packaged_extracts_inhaled_inventory_weight numeric,
	OUT packaged_extracts_ingested_inventory_weight numeric,
	OUT packaged_extracts_other_inventory_weight numeric,
	OUT packaged_edibles_solid_inventory_weight numeric,
	OUT packaged_edibles_nonsolid_inventory_weight numeric,
	OUT packaged_topicals_inventory_weight numeric)
    RETURNS record
    LANGUAGE plpgsql
    AS $function$
            DECLARE
                initial_date character varying;
                final_day numeric;
            BEGIN	
                SELECT TO_CHAR(MIN(timestamp), 'YYYY-MM-DD') FROM public.inventories INTO initial_date;
				
                            
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE((f).seeds_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_seed_inventory,
                    SUM(COALESCE((f).vegetative_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_vegetative_plants_inventory,		
                    SUM(COALESCE((f).whole_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_whole_cannabis_plants_inventory,
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_fresh_cannabis_inventory,
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
                    SUM(COALESCE((f).packaged_seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory,
                    SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_vegetative_plants_inventory,				
                    SUM(COALESCE((f).fresh_cannabis_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).dried_cannabis_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_topicals_inventory,
                    
                    
                    -- packaged weight(#)
                    SUM(COALESCE((f).seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory_weight, -- total number of seeds
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory_weight,
                    SUM(COALESCE((f).dried_cannabis_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory_weight,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory_weight,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inhaled_inventory_weight,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_ingested_inventory_weight,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_other_inventory_weight,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_solid_inventory_weight,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_nonsolid_inventory_weight,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_topicals_inventory_weight
            
                FROM (
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv 
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1)  
                    WHERE inv.latest_quantity > 0 and
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) AND
                        type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    --samples that have not been sent to the lab and do not come from plants
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
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
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) 
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' 
                        
            
                    ) AS T1
                    INTO
                        unpackaged_seed_inventory,
                        unpackaged_vegetative_plants_inventory,		
                        unpackaged_whole_cannabis_plants_inventory,
                        unpackaged_fresh_cannabis_inventory,
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
             
            END;$function$;



    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer,initial_date character varying,final_date character varying,org_id integer)
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
    DECLARE package_oil DECIMAL;
	
        BEGIN
        -- unpackaged seed processed and unpacked vegetative plants produced
	    SET enable_nestloop = off;
        UPDATE health_canada_report
        SET
            unpackaged_seed_produced = 0,
            unpackaged_seed_processed = COALESCE(T2.unpackaged_seed_processed,0)/1000,
            unpackaged_vegetative_plants_produced = COALESCE(T2.unpackaged_vegetative_plants_produced,0)
        FROM (
            SELECT
                SUM(COALESCE(T1.seeds_weight,0)) AS unpackaged_seed_processed,
                SUM(COALESCE(T1.plants_quantity,0)) AS unpackaged_vegetative_plants_produced
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL),0)) AS seeds_weight,
                    GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS plants_quantity
                FROM activities
                WHERE name ='germinate_seeds' AND
                    organization_id = org_id AND
                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                UNION ALL
                SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                FROM activities
                WHERE name = 'propagate_cuttings' AND
                    organization_id = org_id AND
                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged vegetative plants processed and  whole plant produced
        UPDATE health_canada_report
        SET 
            unpackaged_vegetative_plants_processed = COALESCE(T2.plants_processed,0),
            unpackaged_whole_cannabis_plants_produced = COALESCE(T2.plants_processed,0)	
        FROM (
            SELECT 
                SUM(COALESCE(T1.plants_processed,0)) AS plants_processed			
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(act.data->>'qty' AS DECIMAL),0)) AS plants_processed
                FROM activities act 
                WHERE act.name = 'update_stage' 
                    AND act.data->>'to_stage' = 'flowering' 
                    AND act.organization_id = org_id 
                    AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged fresh cannabis produced and whole plants processed
        UPDATE health_canada_report
        SET
            unpackaged_fresh_cannabis_produced = COALESCE(T2.fresh_cannabis_produced,0)/1000,
            unpackaged_whole_cannabis_plants_processed = COALESCE(T2.whole_plants_processed,0)
        FROM (
            SELECT
                SUM(COALESCE(T1.fresh_cannabis_produced,0)) AS fresh_cannabis_produced,
                SUM(COALESCE(T1.whole_plants_processed,0)) AS whole_plants_processed
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS fresh_cannabis_produced,
                    GREATEST(0,COALESCE(CAST(data->>'from_qty' AS DECIMAL),0)) AS whole_plants_processed
                FROM activities
                WHERE name IN ('batch_record_bud_harvest_weight', 'batch_record_harvest_weight')
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged dried cannabis produced, unpackaged pure intermediate produced
        UPDATE health_canada_report
        SET
            unpackaged_dried_cannabis_produced = COALESCE(T2.dried_qty,0)/1000,
            unpackaged_extracts_produced = COALESCE(T2.oil_qty,0)/1000
        FROM (
            SELECT SUM(t1.dry+t1.cured) AS dried_qty, SUM(t1.crude+t1.distilled) AS oil_qty
                FROM (
                    SELECT
                        -- we can't account as we produce something if it comes from the something from the same type, so that's why dry, can't be from dry or cured
                            CASE 
                            WHEN act.data->>'to_qty_unit' = 'dry' and act.data->>'from_qty_unit' not in ('dry', 'cured') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS dry,
                        CASE
                            WHEN act.data->>'to_qty_unit' = 'cured' and act.data->>'from_qty_unit' not in ('dry', 'cured') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS cured,
                        CASE					
                            WHEN act.data->>'to_qty_unit' = 'crude' and  act.data->>'from_qty_unit' not in ('crude', 'distilled')  THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS crude,
                        CASE						
                            WHEN act.data->>'to_qty_unit' = 'distilled' and act.data->>'from_qty_unit' not in ('crude', 'distilled') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS distilled
                    FROM inventories AS inv
                    INNER JOIN (
                        SELECT
                            CAST(act_adj.data->>'from_inventory_id' AS bigint) AS inventory_id,
                            act_adj.id AS id,
                            max(act_adj.timestamp)
                        FROM activities AS act_adj
                        WHERE act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                            AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= final_date
                        GROUP BY act_adj.data->>'from_inventory_id', act_adj.id
                    ) AS T0 ON T0.inventory_id = inv.id
                    INNER JOIN activities AS act ON act.id = t0.id
                    WHERE act.organization_id = org_id 
                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                ) AS t1
            ) AS T2
        WHERE id = report_id;

            -- dried processed
        UPDATE health_canada_report
        SET
            unpackaged_dried_cannabis_processed = COALESCE(T2.dried_cannabis_processed,0)/1000
        FROM (
            SELECT SUM(t1.dried_cannabis_used) AS dried_cannabis_processed from (
            SELECT CAST (data->>'to_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_crude_oil_weight')
                AND data->>'from_qty_unit' in ('cured', 'dry') 
                --AND organization_id = 1 
                --AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-12-01'  AND '2020-12-30'
                AND organization_id = org_id 
                AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date        
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                
                ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged new extractions processed and produced
       
        package_oil := (COALESCE((SELECT SUM(CAST(actTransf.data->>'to_qty' AS DECIMAL))
				FROM activities AS act
				INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
				INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
				LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
				WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
				actTransf.data->>'to_qty_unit' IN ('crude', 'distilled') AND
				-- act.organization_id = 1 and
				-- TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
				    act.organization_id = org_id AND
				    act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")),0));
       
				   
        UPDATE health_canada_report
        set
            -- extracts produced + oil produced
            unpackaged_extracts_produced = (COALESCE(unpackaged_extracts_produced, 0)) + (COALESCE(extracts_processed, 0)/1000),
            
            unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_produced = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_produced = COALESCE(topicals, 0)/1000,
            
            unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_processed = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_processed = COALESCE(topicals, 0)/1000,
            
            unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
        FROM (
            
				SELECT
		        SUM(COALESCE(CAST (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE st."name" NOT IN ('crude', 'distilled') AND act."data"->>'from_qty_unit' NOT IN ('crude', 'distilled')) as extracts_processed,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled')) AS extracts_ingested,
		        
				SUM(COALESCE(cast (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE act."data"->>'from_qty_unit' NOT IN ('g-wet','dry','cured','crude', 'distilled') AND act."name" IN ('batch_record_final_extracted_weight', 'queue_for_destruction')) AS extracts_oil_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act."name" IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')) AS extracts_oil,
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled') AS extracts_inhaled,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other' AND st."name" NOT IN ('sift', 'cannabinoid', 'terpene', 'biomass')) AS extracts_other,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals') AS topicals,
		        -- Other reductions if extracted from oil we need to put it on other reductions to math works.
		        --SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE act.data->>'from_qty_unit' IN ('crude', 'distilled')) AS reductions_other
		        SUM(COALESCE(0)) AS reductions_other
			    FROM activities act
			    INNER JOIN
				(
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_final_extracted_weight')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('queue_for_destruction')
					AND a1."data"->>'from_qty_unit' IN ('crude', 'distilled')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
				) AS act_oil ON 
				act."data"->>'from_inventory_id' = act_oil.id AND act."timestamp" = act_oil.timestamp AND act.name IN ('batch_record_final_extracted_weight', 'queue_for_destruction', 'batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
				INNER JOIN stats_taxonomies st ON 
				(act.data->>'to_qty_unit' = st.name OR (act.data->>'from_qty_unit' = st.name AND act."name" IN ('sample_sent_to_lab') )) AND st.organization_id = act.organization_id
				
					
        ) AS T2
        WHERE id = report_id;

            -- unpackaged fresh cannabis processed 
        UPDATE health_canada_report
        SET
            unpackaged_fresh_cannabis_processed = COALESCE(T2.fresh_cannabis_processed,0)/1000
        FROM (
            SELECT SUM(t1.fresh_cannabis_used) AS fresh_cannabis_processed 
            FROM  (
                SELECT CAST (data->>'to_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                    
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged other produced
        UPDATE health_canada_report
        SET
            unpackaged_other_produced = COALESCE(T2.gwet_produced,0) / 1000
        FROM (
            SELECT
                SUM(COALESCE(T1.gwet_produced,0)) AS gwet_produced
            FROM (
                SELECT
                    COALESCE(CAST(data->>'to_qty' AS DECIMAL),0) AS gwet_produced
                FROM activities
                WHERE name = 'create_sample'
                    AND data->>'from_qty_unit' = 'plants'
                    AND organization_id = org_id
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$;




    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer,initial_date character varying,final_date character varying,org_id integer)
    RETURNS void
    LANGUAGE 'plpgsql'
    AS $function$
    /* this functions gets all the samples that have been sent to the lab, but samples for plants, because samples for plants we don't send the entire plant, so it doens't count
        and it goes to adjustment/loss section. */

        BEGIN
        --shipped to analytical testers (samples)
	    SET enable_nestloop = off;
        UPDATE health_canada_report
        SET

            unpackaged_seed_shipped_analytical_testers = COALESCE(T2.unpackaged_seed_shipped_analytical_testers,0)/1000,
            unpackaged_vegetative_plants_shipped_analytical_testers = 0, -- this goes to adjustment/loss section
            unpackaged_whole_cannabis_plants_shipped_analytical_testers = 0,-- this goes to adjustment/loss section
            unpackaged_fresh_shipped_analytical_testers = COALESCE(T2.unpackaged_fresh_shipped_analytical_testers,0)/1000,
            unpackaged_dried_shipped_analytical_testers = COALESCE(T2.unpackaged_dried_shipped_analytical_testers,0)/1000,
            unpackaged_extracts_shipped_analytical_testers = COALESCE(T2.unpackaged_extracts_shipped_analytical_testers,0)/1000,
            unpackaged_other_shipped_analytical_testers = COALESCE(T2.unpackaged_other_shipped_analytical_testers,0)/1000,

            -- new endtypes
            unpackaged_edibles_solid_analytical_testers = COALESCE(T2.unpackaged_edibles_solid_analytical_testers,0)/1000,
            unpackaged_edibles_nonsolid_analytical_testers = COALESCE(T2.unpackaged_edibles_nonsolid_analytical_testers,0)/1000,
            unpackaged_extracts_inhaled_analytical_testers = COALESCE(T2.unpackaged_extracts_inhaled_analytical_testers,0)/1000,
            unpackaged_extracts_ingested_analytical_testers = COALESCE(T2.unpackaged_extracts_ingested_analytical_testers,0)/1000,
            unpackaged_extracts_other_analytical_testers = COALESCE(T2.unpackaged_extracts_other_analytical_testers,0)/1000,
            unpackaged_topicals_analytical_testers = COALESCE(T2.unpackaged_topicals_analytical_testers,0)/1000
        FROM (
            SELECT
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'seeds') AS unpackaged_seed_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'dry' OR T1.unit = 'cured') AS unpackaged_dried_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'distilled' OR T1.unit = 'crude') AS unpackaged_extracts_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'plants') AS unpackaged_other_shipped_analytical_testers,

                -- new endtypes
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested' AND (T1.unit != 'distilled' AND T1.unit != 'crude')) AS unpackaged_extracts_ingested_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
            FROM (
                SELECT 
                        CASE
                            WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                            ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                        END AS quantity,
                        st.data->>'subtype' AS subtype,
                        CASE
                            WHEN act_create_sample.data->>'from_qty_unit' = 'plants' THEN 'plants'
                            ELSE act.data->>'from_qty_unit'
                        END AS unit
                        			
                    FROM activities AS act 
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='create_sample'
                    INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit' AND st.organization_id = act.organization_id 
                    WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                    AND act.name = 'sample_sent_to_lab'
                    --AND act_create_sample.data->>'from_qty_unit' != 'plants'
                    --AND act.organization_id = 1 
                    --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                    AND act.organization_id = org_id 
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")			  
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
    $function$;

        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """

    UPDATE activities
            SET name = 'batch_create_sample'
            WHERE name = 'create_sample';

    UPDATE activities SET data = jsonb_set(data, '{activity_name}', '"batch_create_sample"', TRUE)
    WHERE data->>'activity_name'='create_sample';


    CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying,org_id integer,OUT unpackaged_seed_inventory numeric,OUT unpackaged_vegetative_plants_inventory numeric,OUT unpackaged_whole_cannabis_plants_inventory numeric,OUT unpackaged_fresh_cannabis_inventory numeric,OUT unpackaged_extracts_inventory numeric,OUT unpackaged_dried_cannabis_inventory numeric,OUT packaged_seed_inventory numeric,OUT packaged_vegetative_plants_inventory numeric,OUT packaged_fresh_cannabis_inventory numeric,OUT packaged_dried_cannabis_inventory numeric,OUT packaged_extracts_inventory numeric,OUT unpackaged_extracts_inhaled_inventory numeric,OUT unpackaged_extracts_ingested_inventory numeric,OUT unpackaged_extracts_other_inventory numeric,OUT unpackaged_edibles_solid_inventory numeric,OUT unpackaged_edibles_nonsolid_inventory numeric,OUT unpackaged_topicals_inventory numeric,OUT unpackaged_other_inventory numeric,OUT packaged_extracts_inhaled_inventory numeric,OUT packaged_extracts_ingested_inventory numeric,OUT packaged_extracts_other_inventory numeric,OUT packaged_edibles_solid_inventory numeric,OUT packaged_edibles_nonsolid_inventory numeric,OUT packaged_topicals_inventory numeric,OUT packaged_seed_inventory_weight numeric,OUT packaged_fresh_cannabis_inventory_weight numeric,OUT packaged_dried_cannabis_inventory_weight numeric,OUT packaged_extracts_inventory_weight numeric,OUT packaged_extracts_inhaled_inventory_weight numeric,OUT packaged_extracts_ingested_inventory_weight numeric,OUT packaged_extracts_other_inventory_weight numeric,OUT packaged_edibles_solid_inventory_weight numeric,OUT packaged_edibles_nonsolid_inventory_weight numeric,OUT packaged_topicals_inventory_weight numeric)
    RETURNS record
    LANGUAGE plpgsql
    AS $function$
    DECLARE
                initial_date character varying;
                final_day numeric;
            BEGIN	
                SELECT TO_CHAR(MIN(timestamp), 'YYYY-MM-DD') FROM public.inventories INTO initial_date;
				
                            
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE((f).seeds_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_seed_inventory,
                    SUM(COALESCE((f).vegetative_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_vegetative_plants_inventory,		
                    SUM(COALESCE((f).whole_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_whole_cannabis_plants_inventory,
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_fresh_cannabis_inventory,
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
                    SUM(COALESCE((f).packaged_seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory,
                    SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_vegetative_plants_inventory,				
                    SUM(COALESCE((f).fresh_cannabis_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).dried_cannabis_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_topicals_inventory,
                    
                    
                    -- packaged weight(#)
                    SUM(COALESCE((f).seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory_weight, -- total number of seeds
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory_weight,
                    SUM(COALESCE((f).dried_cannabis_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory_weight,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory_weight,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inhaled_inventory_weight,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_ingested_inventory_weight,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_other_inventory_weight,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_solid_inventory_weight,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_edibles_nonsolid_inventory_weight,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_topicals_inventory_weight
            
                FROM (
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv 
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1)  
                    WHERE inv.latest_quantity > 0 and
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) AND
                        type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    --samples that have not been sent to the lab and do not come from plants
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1) as inv
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    INNER JOIN (
                        SELECT 
                            CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                            MAX(sample_activity.id) AS act_id
                        FROM activities AS sample_activity
                        WHERE 
                            sample_activity.name in ('batch_create_sample', 'sample_sent_to_lab') 
                            AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= final_date
                            --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                            --AND sample_activity.data->>'from_qty_unit' != 'plants'
                        GROUP BY sample_activity.data->>'inventory_id'
                    ) AS latest_activity ON inv.id = latest_activity.id
                    INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='batch_create_sample' 
                    WHERE inv.latest_quantity > 0 AND
                          inv.type ='sample' AND
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) 
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' 
                        
            
                    ) AS T1
                    INTO
                        unpackaged_seed_inventory,
                        unpackaged_vegetative_plants_inventory,		
                        unpackaged_whole_cannabis_plants_inventory,
                        unpackaged_fresh_cannabis_inventory,
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
             
            END;
    $function$;



    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer,initial_date character varying,final_date character varying,org_id integer)
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
    DECLARE package_oil DECIMAL;
	
        BEGIN
        -- unpackaged seed processed and unpacked vegetative plants produced
	    SET enable_nestloop = off;
        UPDATE health_canada_report
        SET
            unpackaged_seed_produced = 0,
            unpackaged_seed_processed = COALESCE(T2.unpackaged_seed_processed,0)/1000,
            unpackaged_vegetative_plants_produced = COALESCE(T2.unpackaged_vegetative_plants_produced,0)
        FROM (
            SELECT
                SUM(COALESCE(T1.seeds_weight,0)) AS unpackaged_seed_processed,
                SUM(COALESCE(T1.plants_quantity,0)) AS unpackaged_vegetative_plants_produced
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL),0)) AS seeds_weight,
                    GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS plants_quantity
                FROM activities
                WHERE name ='germinate_seeds' AND
                    organization_id = org_id AND
                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                UNION ALL
                SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                FROM activities
                WHERE name = 'propagate_cuttings' AND
                    organization_id = org_id AND
                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged vegetative plants processed and  whole plant produced
        UPDATE health_canada_report
        SET 
            unpackaged_vegetative_plants_processed = COALESCE(T2.plants_processed,0),
            unpackaged_whole_cannabis_plants_produced = COALESCE(T2.plants_processed,0)	
        FROM (
            SELECT 
                SUM(COALESCE(T1.plants_processed,0)) AS plants_processed			
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(act.data->>'qty' AS DECIMAL),0)) AS plants_processed
                FROM activities act 
                WHERE act.name = 'update_stage' 
                    AND act.data->>'to_stage' = 'flowering' 
                    AND act.organization_id = org_id 
                    AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged fresh cannabis produced and whole plants processed
        UPDATE health_canada_report
        SET
            unpackaged_fresh_cannabis_produced = COALESCE(T2.fresh_cannabis_produced,0)/1000,
            unpackaged_whole_cannabis_plants_processed = COALESCE(T2.whole_plants_processed,0)
        FROM (
            SELECT
                SUM(COALESCE(T1.fresh_cannabis_produced,0)) AS fresh_cannabis_produced,
                SUM(COALESCE(T1.whole_plants_processed,0)) AS whole_plants_processed
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS fresh_cannabis_produced,
                    GREATEST(0,COALESCE(CAST(data->>'from_qty' AS DECIMAL),0)) AS whole_plants_processed
                FROM activities
                WHERE name IN ('batch_record_bud_harvest_weight', 'batch_record_harvest_weight')
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged dried cannabis produced, unpackaged pure intermediate produced
        UPDATE health_canada_report
        SET
            unpackaged_dried_cannabis_produced = COALESCE(T2.dried_qty,0)/1000,
            unpackaged_extracts_produced = COALESCE(T2.oil_qty,0)/1000
        FROM (
            SELECT SUM(t1.dry+t1.cured) AS dried_qty, SUM(t1.crude+t1.distilled) AS oil_qty
                FROM (
                    SELECT
                        -- we can't account as we produce something if it comes from the something from the same type, so that's why dry, can't be from dry or cured
                            CASE 
                            WHEN act.data->>'to_qty_unit' = 'dry' and act.data->>'from_qty_unit' not in ('dry', 'cured') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS dry,
                        CASE
                            WHEN act.data->>'to_qty_unit' = 'cured' and act.data->>'from_qty_unit' not in ('dry', 'cured') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS cured,
                        CASE					
                            WHEN act.data->>'to_qty_unit' = 'crude' and  act.data->>'from_qty_unit' not in ('crude', 'distilled')  THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS crude,
                        CASE						
                            WHEN act.data->>'to_qty_unit' = 'distilled' and act.data->>'from_qty_unit' not in ('crude', 'distilled') THEN GREATEST(0,COALESCE(CAST(act.data->>'to_qty' AS DECIMAL),0))
                            ELSE 0
                        END AS distilled
                    FROM inventories AS inv
                    INNER JOIN (
                        SELECT
                            CAST(act_adj.data->>'from_inventory_id' AS bigint) AS inventory_id,
                            act_adj.id AS id,
                            max(act_adj.timestamp)
                        FROM activities AS act_adj
                        WHERE act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                            AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= final_date
                        GROUP BY act_adj.data->>'from_inventory_id', act_adj.id
                    ) AS T0 ON T0.inventory_id = inv.id
                    INNER JOIN activities AS act ON act.id = t0.id
                    WHERE act.organization_id = org_id 
                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                ) AS t1
            ) AS T2
        WHERE id = report_id;

            -- dried processed
        UPDATE health_canada_report
        SET
            unpackaged_dried_cannabis_processed = COALESCE(T2.dried_cannabis_processed,0)/1000
        FROM (
            SELECT SUM(t1.dried_cannabis_used) AS dried_cannabis_processed from (
            SELECT CAST (data->>'to_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_crude_oil_weight')
                AND data->>'from_qty_unit' in ('cured', 'dry') 
                --AND organization_id = 1 
                --AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-12-01'  AND '2020-12-30'
                AND organization_id = org_id 
                AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date        
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                
                ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged new extractions processed and produced
       
        package_oil := (COALESCE((SELECT SUM(CAST(actTransf.data->>'to_qty' AS DECIMAL))
				FROM activities AS act
				INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
				INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
				LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
				WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
				actTransf.data->>'to_qty_unit' IN ('crude', 'distilled') AND
				-- act.organization_id = 1 and
				-- TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
				    act.organization_id = org_id AND
				    act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")),0));
       
				   
        UPDATE health_canada_report
        set
            -- extracts produced + oil produced
            unpackaged_extracts_produced = (COALESCE(unpackaged_extracts_produced, 0)) + (COALESCE(extracts_processed, 0)/1000),
            
            unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_produced = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_produced = COALESCE(topicals, 0)/1000,
            
            unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_processed = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_processed = COALESCE(topicals, 0)/1000,
            
            unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
        FROM (
            
				SELECT
		        SUM(COALESCE(CAST (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE st."name" NOT IN ('crude', 'distilled') AND act."data"->>'from_qty_unit' NOT IN ('crude', 'distilled')) as extracts_processed,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled')) AS extracts_ingested,
		        
				SUM(COALESCE(cast (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE act."data"->>'from_qty_unit' NOT IN ('g-wet','dry','cured','crude', 'distilled') AND act."name" IN ('batch_record_final_extracted_weight', 'queue_for_destruction')) AS extracts_oil_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act."name" IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')) AS extracts_oil,
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled') AS extracts_inhaled,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other' AND st."name" NOT IN ('sift', 'cannabinoid', 'terpene', 'biomass')) AS extracts_other,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals') AS topicals,
		        -- Other reductions if extracted from oil we need to put it on other reductions to math works.
		        --SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE act.data->>'from_qty_unit' IN ('crude', 'distilled')) AS reductions_other
		        SUM(COALESCE(0)) AS reductions_other
			    FROM activities act
			    INNER JOIN
				(
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_final_extracted_weight')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('queue_for_destruction')
					AND a1."data"->>'from_qty_unit' IN ('crude', 'distilled')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
					AND a1.organization_id = org_id
					AND TO_CHAR(a1.timestamp, 'YYYY-MM-DD') BETWEEN initial_date AND final_date
					GROUP BY a1."data"->>'from_inventory_id'
					
				) AS act_oil ON 
				act."data"->>'from_inventory_id' = act_oil.id AND act."timestamp" = act_oil.timestamp AND act.name IN ('batch_record_final_extracted_weight', 'queue_for_destruction', 'batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
				INNER JOIN stats_taxonomies st ON 
				(act.data->>'to_qty_unit' = st.name OR (act.data->>'from_qty_unit' = st.name AND act."name" IN ('sample_sent_to_lab') )) AND st.organization_id = act.organization_id
				
					
        ) AS T2
        WHERE id = report_id;

            -- unpackaged fresh cannabis processed 
        UPDATE health_canada_report
        SET
            unpackaged_fresh_cannabis_processed = COALESCE(T2.fresh_cannabis_processed,0)/1000
        FROM (
            SELECT SUM(t1.fresh_cannabis_used) AS fresh_cannabis_processed 
            FROM  (
                SELECT CAST (data->>'to_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                    
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged other produced
        UPDATE health_canada_report
        SET
            unpackaged_other_produced = COALESCE(T2.gwet_produced,0) / 1000
        FROM (
            SELECT
                SUM(COALESCE(T1.gwet_produced,0)) AS gwet_produced
            FROM (
                SELECT
                    COALESCE(CAST(data->>'to_qty' AS DECIMAL),0) AS gwet_produced
                FROM activities
                WHERE name = 'batch_create_sample'
                    AND data->>'from_qty_unit' = 'plants'
                    AND organization_id = org_id
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
    $function$;


    CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer,initial_date character varying,final_date character varying,org_id integer)
    RETURNS void
    LANGUAGE plpgsql
    AS $function$
    /* this functions gets all the samples that have been sent to the lab, but samples for plants, because samples for plants we don't send the entire plant, so it doens't count
        and it goes to adjustment/loss section. */

        BEGIN
        --shipped to analytical testers (samples)
	    SET enable_nestloop = off;
        UPDATE health_canada_report
        SET

            unpackaged_seed_shipped_analytical_testers = COALESCE(T2.unpackaged_seed_shipped_analytical_testers,0)/1000,
            unpackaged_vegetative_plants_shipped_analytical_testers = 0, -- this goes to adjustment/loss section
            unpackaged_whole_cannabis_plants_shipped_analytical_testers = 0,-- this goes to adjustment/loss section
            unpackaged_fresh_shipped_analytical_testers = COALESCE(T2.unpackaged_fresh_shipped_analytical_testers,0)/1000,
            unpackaged_dried_shipped_analytical_testers = COALESCE(T2.unpackaged_dried_shipped_analytical_testers,0)/1000,
            unpackaged_extracts_shipped_analytical_testers = COALESCE(T2.unpackaged_extracts_shipped_analytical_testers,0)/1000,
            unpackaged_other_shipped_analytical_testers = COALESCE(T2.unpackaged_other_shipped_analytical_testers,0)/1000,

            -- new endtypes
            unpackaged_edibles_solid_analytical_testers = COALESCE(T2.unpackaged_edibles_solid_analytical_testers,0)/1000,
            unpackaged_edibles_nonsolid_analytical_testers = COALESCE(T2.unpackaged_edibles_nonsolid_analytical_testers,0)/1000,
            unpackaged_extracts_inhaled_analytical_testers = COALESCE(T2.unpackaged_extracts_inhaled_analytical_testers,0)/1000,
            unpackaged_extracts_ingested_analytical_testers = COALESCE(T2.unpackaged_extracts_ingested_analytical_testers,0)/1000,
            unpackaged_extracts_other_analytical_testers = COALESCE(T2.unpackaged_extracts_other_analytical_testers,0)/1000,
            unpackaged_topicals_analytical_testers = COALESCE(T2.unpackaged_topicals_analytical_testers,0)/1000
        FROM (
            SELECT
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'seeds') AS unpackaged_seed_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'dry' OR T1.unit = 'cured') AS unpackaged_dried_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'distilled' OR T1.unit = 'crude') AS unpackaged_extracts_shipped_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'plants') AS unpackaged_other_shipped_analytical_testers,

                -- new endtypes
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested' AND (T1.unit != 'distilled' AND T1.unit != 'crude')) AS unpackaged_extracts_ingested_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
            FROM (
                SELECT 
                        CASE
                            WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                            ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                        END AS quantity,
                        st.data->>'subtype' AS subtype,
                        CASE
                            WHEN act_create_sample.data->>'from_qty_unit' = 'plants' THEN 'plants'
                            ELSE act.data->>'from_qty_unit'
                        END AS unit
                        			
                    FROM activities AS act 
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                    INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit' AND st.organization_id = act.organization_id 
                    WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                    AND act.name = 'sample_sent_to_lab'
                    --AND act_create_sample.data->>'from_qty_unit' != 'plants'
                    --AND act.organization_id = 1 
                    --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                    AND act.organization_id = org_id 
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")			  
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
    $function$;

        """
    )

