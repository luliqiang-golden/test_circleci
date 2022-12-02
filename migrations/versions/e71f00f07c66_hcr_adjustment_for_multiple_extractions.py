"""hcr adjustment for multiple extractions

Revision ID: e71f00f07c66
Revises: d6669238e3ae
Create Date: 2022-07-04 13:53:21.720440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e71f00f07c66'
down_revision = 'd6669238e3ae'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
        CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
    DECLARE package_oil DECIMAL;
   	DECLARE v_taxonomy_id bigint;
	
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
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                UNION ALL
                SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                FROM activities
                WHERE name = 'propagate_cuttings' AND
                    organization_id = org_id AND
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                            AND act_adj.timestamp <= CAST(final_date AS "timestamp")
                        GROUP BY act_adj.data->>'from_inventory_id', act_adj.id
                    ) AS T0 ON T0.inventory_id = inv.id
                    INNER JOIN activities AS act ON act.id = t0.id
                    WHERE act.organization_id = org_id 
                        AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
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
       	

		
		v_taxonomy_id := (SELECT id FROM taxonomies t WHERE name = 'stats' AND organization_id = org_id);
				   		
				   
        UPDATE health_canada_report
        set
            -- extracts produced + oil produced
            unpackaged_extracts_produced = (COALESCE(unpackaged_extracts_produced, 0)) + (COALESCE(extracts_processed, 0)/1000)
            + (COALESCE(edibles_solid, 0)/1000)
            + (COALESCE(edibles_nonsolid, 0)/1000)
            + (COALESCE(extracts_ingested, 0)/1000)
            + (COALESCE(extracts_inhaled, 0)/1000)
            + (COALESCE(extracts_other, 0)/1000)
            - (COALESCE(extracts_pure_intermediate_reductions, 0)/1000),
            
            unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_produced = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) - (COALESCE(extracts_ingested_reductions, 0)/1000) + (COALESCE(extracts_ingested_additions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000 - (COALESCE(extracts_inhaled_reductions, 0)/1000) + (COALESCE(extracts_inhaled_additions, 0)/1000),
            unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000 - (COALESCE(extracts_other_reductions, 0)/1000) + (COALESCE(extracts_other_additions, 0)/1000),
            unpackaged_topicals_produced = COALESCE(topicals, 0)/1000 - (COALESCE(extracts_topicals_reductions, 0)/1000) + (COALESCE(extracts_topicals_additions, 0)/1000),
            
            unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_processed = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) - (COALESCE(extracts_ingested_reductions, 0)/1000) + (COALESCE(extracts_ingested_additions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000 - (COALESCE(extracts_inhaled_reductions, 0)/1000) + (COALESCE(extracts_inhaled_additions, 0)/1000),
            unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000 - (COALESCE(extracts_other_reductions, 0)/1000) + (COALESCE(extracts_other_additions, 0)/1000),
            unpackaged_topicals_processed = COALESCE(topicals, 0)/1000 - (COALESCE(extracts_topicals_reductions, 0)/1000) + (COALESCE(extracts_topicals_additions, 0)/1000),
            
            unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
        FROM (
            
				SELECT
		        SUM(COALESCE(CAST (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE (st."name" NOT IN ('crude', 'distilled') AND st."name" NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AND (act."data"->>'from_qty_unit' NOT IN ('crude', 'distilled') AND act."data"->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract' ))) as extracts_processed,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_ingested,
		        
				SUM(COALESCE(cast (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE act."data"->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND name NOT IN ('seeds', 'plants')) AND act."name" IN ('batch_record_final_extracted_weight', 'queue_for_destruction')) AS extracts_oil_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act."name" IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')) AS extracts_oil,
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled' AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_inhaled,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other' /*AND st."name" NOT IN ('sift', 'cannabinoid', 'terpene', 'biomass')*/ AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_other,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals' AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS topicals,
		        
		        
		        
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'inhaled' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_inhaled_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'ingested' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_ingested_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'other' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_other_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'topicals' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_topicals_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st."name" IN ('crude', 'distilled') AND st.DATA->>'type' = 'extract') AS extracts_pure_intermediate_reductions,
		        
		        
		        
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'inhaled' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_inhaled_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'ingested' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_ingested_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'other' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_other_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'topicals' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_topicals_additions,
		        
		        
		        
		        
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
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('queue_for_destruction')
					AND a1."data"->>'from_qty_unit' IN ('crude', 'distilled')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
				) AS act_oil ON 
				act."data"->>'from_inventory_id' = act_oil.id AND act."timestamp" = act_oil.timestamp AND act.name IN ('batch_record_final_extracted_weight', 'queue_for_destruction', 'batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
				INNER JOIN stats_taxonomies st ON 
				(act.data->>'to_qty_unit' = st.name OR (act.data->>'from_qty_unit' = st.name AND act."name" IN ('sample_sent_to_lab') )) AND st.organization_id = act.organization_id
				INNER JOIN stats_taxonomies from_st ON 
				(act.data->>'from_qty_unit' = from_st.name OR (act.data->>'from_qty_unit' = from_st.name AND act."name" IN ('sample_sent_to_lab'))) AND from_st.organization_id = act.organization_id
				
					
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                    
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$
;




























CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT shipping_status character varying, OUT other_weight numeric)
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
    
        IF (fresh_cannabis_weight > 0) THEN
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

        
        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
        CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
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
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                UNION ALL
                SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                FROM activities
                WHERE name = 'propagate_cuttings' AND
                    organization_id = org_id AND
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                            AND act_adj.timestamp <= CAST(final_date AS "timestamp")
                        GROUP BY act_adj.data->>'from_inventory_id', act_adj.id
                    ) AS T0 ON T0.inventory_id = inv.id
                    INNER JOIN activities AS act ON act.id = t0.id
                    WHERE act.organization_id = org_id 
                        AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
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
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('queue_for_destruction')
					AND a1."data"->>'from_qty_unit' IN ('crude', 'distilled')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                    
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$
;




















CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT shipping_status character varying, OUT other_weight numeric)
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

    extracts_weight := distilled + crude + cannabinoid + sift + terpene + biomass;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested' AND (unit NOT IN ('crude', 'distilled') OR (unit IN ('crude', 'distilled') AND type = 'lot item' AND p_package_type != 'unpackaged'))) THEN
        extracts_ingested_weight := GREATEST(0,quantity);
    END IF;

    extracts_other_weight := 0;
    IF (taxonomy_subtype = 'other' AND (unit NOT IN ('cannabinoid', 'sift', 'terpene', 'biomass'))) THEN
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
        --ELSIF (extracts_weight > 0) THEN
        --    extracts_qty := 1;
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
