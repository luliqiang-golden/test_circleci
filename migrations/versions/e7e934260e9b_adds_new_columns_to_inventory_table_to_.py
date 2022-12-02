"""adds new columns to inventory table to implement multiple harvesting and adjust HCR accordingly

Revision ID: e7e934260e9b
Revises: fa6b5940cc56
Create Date: 2022-08-23 20:33:50.446353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7e934260e9b'
down_revision = 'fa6b5940cc56'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """

        ALTER TABLE inventories 
        ADD COLUMN is_child boolean DEFAULT FALSE;

        ALTER TABLE inventories 
        ADD COLUMN is_parent boolean DEFAULT FALSE;

        ALTER TABLE inventories 
        ADD COLUMN parent_id bigint;

        ALTER TABLE public.inventories ADD CONSTRAINT inventory_relation FOREIGN KEY (parent_id) REFERENCES public.inventories(id);
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
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
    	LEFT JOIN activities AS act_samples ON inv.id = cast(act_samples.data->>'to_inventory_id' AS BIGINT) AND act_samples.name IN ('create_sample');
    END;
    $function$
;


























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
                WHERE name IN ('batch_record_bud_harvest_weight', 'batch_record_harvest_weight', 'batch_record_harvest_weight_partially')
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

        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
            ALTER TABLE inventories 
            DROP COLUMN is_child;


            ALTER TABLE inventories 
            DROP COLUMN is_parent;


            ALTER TABLE public.inventories DROP CONSTRAINT inventory_relation;

            ALTER TABLE inventories 
            DROP COLUMN parent_id;
            
            
            
            
            
            
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
    	LEFT JOIN activities AS act_samples ON inv.id = cast(act_samples.data->>'to_inventory_id' AS BIGINT) AND act_samples.name IN ('create_sample');
    END;
    $function$
;
















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



        """)
