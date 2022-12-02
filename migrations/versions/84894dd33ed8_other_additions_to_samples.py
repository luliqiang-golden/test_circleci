"""other_additions_to_samples

Revision ID: 84894dd33ed8
Revises: 13fc696bc0df 
Create Date: 2021-10-29 18:39:35.295607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84894dd33ed8'
down_revision = '13fc696bc0df'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        ALTER TABLE health_canada_report ADD COLUMN IF NOT EXISTS unpackaged_other_shipped_analytical_testers numeric(14,3) DEFAULT 0;
        ALTER TABLE health_canada_report ADD COLUMN IF NOT EXISTS unpackaged_other_produced numeric(14,3) DEFAULT 0;
        ALTER TABLE health_canada_report ADD COLUMN IF NOT EXISTS unpackaged_other_opening_inventory numeric(14,3) DEFAULT 0;
        ALTER TABLE health_canada_report ADD COLUMN IF NOT EXISTS unpackaged_other_closing_inventory numeric(14,3) DEFAULT 0;


        CREATE OR REPLACE FUNCTION f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
        LANGUAGE plpgsql
        AS
        $$
        /* this functions gets all the samples that have been sent to the lab, but samples for plants, because samples for plants we don't send the entire plant, so it doens't count
        and it goes to adjustment/loss section. */

        BEGIN
        --shipped to analytical testers (samples)
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
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
            FROM (
                SELECT 
                        CASE
                            WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act.data->>'from_qty' AS DECIMAL) * CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                            ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                        END AS quantity,
                        st.data->>'subtype' AS subtype,
                        act.data->>'from_qty_unit' AS unit			
                    FROM activities AS act 
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                    INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit'
                    WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                    AND act.name = 'sample_sent_to_lab'
                    AND act_create_sample.data->>'from_qty_unit' != 'plants'
                    --AND act.organization_id = 1 
                    --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                    AND act.organization_id = org_id 
                    AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 			  
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $$;



        CREATE OR REPLACE FUNCTION f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
        LANGUAGE plpgsql
        AS
        $$
        BEGIN
        -- unpackaged seed processed and unpacked vegetative plants produced
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
                    GREATEST(0,COALESCE(CAST(data->>'qty' AS DECIMAL),0)) AS plants_processed
                FROM activities 			
                WHERE name = 'update_stage' 
                    AND data->>'to_stage' = 'flowering' 
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
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
                WHERE name = 'batch_record_bud_harvest_weight' 
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
                            MIN(act_adj.id) AS id
                        FROM activities AS act_adj
                        WHERE act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                            AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= final_date
                        GROUP BY act_adj.data->>'from_inventory_id'
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
                
                ) as t1
        ) AS T2
        WHERE id = report_id;


        -- unpackaged new extractions processed and produced
        UPDATE health_canada_report
        set
            -- extracts produced + oil produced
            unpackaged_extracts_produced = coalesce(unpackaged_extracts_produced, 0) + (COALESCE(T2.extracts_processed,0)/1000),
            
            unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_produced = COALESCE(extracts_ingested, 0)/1000,
            unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_produced = COALESCE(topicals, 0)/1000,
            
            unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_processed = COALESCE(extracts_ingested, 0)/1000,
            unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000,
            unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000,
            unpackaged_topicals_processed = COALESCE(topicals, 0)/1000,
            
            unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
        FROM (
            select
                sum(coalesce(cast(act.data->>'to_qty' as DECIMAL))) as extracts_processed,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested') AS extracts_ingested,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled') AS extracts_inhaled,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other') AS extracts_other,
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals') AS topicals,
                -- Other reductions if extracted from oil we need to put it on other reductions to math works.
                SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE act.data->>'from_qty_unit' IN ('crude', 'distilled')) AS reductions_other
            from
                activities act
            inner join stats_taxonomies st on act.data->>'to_qty_unit' = st.name
            where
                act.name in ('batch_record_extracted_weight')
            and act.organization_id = org_id
            and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date        
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
        $$;


        DROP FUNCTION IF EXISTS public.f_serialize_stats_fields(numeric,varchar,varchar,varchar,jsonb,jsonb,varchar);

        CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT others_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying) RETURNS record
        LANGUAGE plpgsql
        AS
        $$
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
                IF ((stage in ('planning', 'propagation', 'germinating', 'vegetation') OR type IN ('received inventory', 'mother', 'mother batch', 'lot'))) OR (data->'plan'->>'end_type'='plants') THEN
                    vegetative_plants := plants;
                ELSE
                    whole_plants := plants;
                END IF;
        END IF;


        fresh_cannabis_weight := 0;
        others_qty := 0;
        IF (unit = 'g-wet') THEN
            IF (type = 'sample') THEN
                others_qty := GREATEST(0,quantity);
            ELSE
                fresh_cannabis_weight := GREATEST(0,quantity);
            END IF;
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

        extracts_weight := distilled + crude;


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


        IF (type = 'lot item') THEN
            package_type := 'package';
            IF (fresh_cannabis_weight > 0) THEN
                fresh_cannabis_qty := 1;
            ELSIF (dried_cannabis_weight > 0) THEN
                dried_cannabis_qty := 1;
            ELSIF (extracts_weight > 0) THEN
                extracts_qty := 1;
            ELSIF (plants > 0) THEN
                packaged_vegetative_plants_qty := 1;
            
            -- new endtypes
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
        $$;



        DROP FUNCTION IF EXISTS public.f_get_current_inventory(varchar,integer);

        CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT unpackaged_other_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT unpackaged_extracts_inhaled_inventory numeric, OUT unpackaged_extracts_ingested_inventory numeric, OUT unpackaged_extracts_other_inventory numeric, OUT unpackaged_edibles_solid_inventory numeric, OUT unpackaged_edibles_nonsolid_inventory numeric, OUT unpackaged_topicals_inventory numeric, OUT packaged_extracts_inhaled_inventory numeric, OUT packaged_extracts_ingested_inventory numeric, OUT packaged_extracts_other_inventory numeric, OUT packaged_edibles_solid_inventory numeric, OUT packaged_edibles_nonsolid_inventory numeric, OUT packaged_topicals_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric, OUT packaged_extracts_inhaled_inventory_weight numeric, OUT packaged_extracts_ingested_inventory_weight numeric, OUT packaged_extracts_other_inventory_weight numeric, OUT packaged_edibles_solid_inventory_weight numeric, OUT packaged_edibles_nonsolid_inventory_weight numeric, OUT packaged_topicals_inventory_weight numeric) RETURNS record
        LANGUAGE plpgsql
        AS
        $$
        DECLARE
            initial_date character varying;
            final_day numeric;
        BEGIN	
            -- since we shouldn't include the 1st day of the month for opening inventory
            SELECT EXTRACT(DAY FROM TO_DATE(final_date, 'YYYY-MM-DD')) INTO final_day;
            IF final_day = 1 THEN
                SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-DD')
                                - interval '1 day', 'YYYY-MM-DD') INTO final_date;
                
                    -- get the initial date as 1 year constraint for opening inventory
                SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-DD') 
                                - interval '1 year', 'YYYY-MM-DD') INTO initial_date;			
            ELSE
                    -- get the initial date as 1 year constraint for closing inventory
                    -- last day of the previus month and year
                SELECT TO_CHAR(TO_DATE(t1.final_dt, 'YYYY-MM-DD') 
                                + interval '1 month'
                                - interval '1 day', 'YYYY-MM-DD') 
                FROM (
                SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-01') 									
                                - interval '1 month'
                                - interval '1 year'
                                , 'YYYY-MM-DD') as final_dt
                    ) AS t1 INTO initial_date;		

            END IF;


        SELECT

            -- unpackage (kg)
            SUM(COALESCE((f).seeds_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_seed_inventory,
            SUM(COALESCE((f).vegetative_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_vegetative_plants_inventory,
            SUM(COALESCE((f).whole_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_whole_cannabis_plants_inventory,
            SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_fresh_cannabis_inventory,
            SUM(COALESCE((f).dried_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_dried_cannabis_inventory,
            SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inventory,
            SUM(COALESCE((f).others_qty,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_other_inventory,

            SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inhaled_inventory,
            SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_ingested_inventory,
            SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_other_inventory,
            SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_solid_inventory,
            SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_nonsolid_inventory,
            SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_topicals_inventory,

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
            SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
            FROM f_inventories_latest_stats_stage(final_date) as inv 
            inner join stats_taxonomies as st on st.name = inv.latest_unit
            --FROM f_inventories_latest_stats_stage('2020-05-31')  
            WHERE inv.latest_quantity > 0 and
                inv.organization_id = org_id AND
                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date AND
                type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory', 'sample')

            UNION ALL
            --samples that have not been sent to the lab and do not come from plants
            SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
            FROM f_inventories_latest_stats_stage(final_date) as inv
            inner join stats_taxonomies as st on st.name = inv.latest_unit
            INNER JOIN (
                SELECT
                    CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                    MAX(sample_activity.id) AS act_id
                FROM activities AS sample_activity
                WHERE 
                    sample_activity.name in ('batch_create_sample', 'sample_sent_to_lab') 
                    AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= final_date
                    --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                    AND sample_activity.data->>'from_qty_unit' != 'plants'
                GROUP BY sample_activity.data->>'inventory_id'
            ) AS latest_activity ON inv.id = latest_activity.id
            INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='batch_create_sample'
            WHERE inv.latest_quantity > 0 AND
                    inv.type ='sample' AND
                inv.organization_id = org_id AND
                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            ) AS T1
        INTO
            unpackaged_seed_inventory,
            unpackaged_vegetative_plants_inventory,
            unpackaged_whole_cannabis_plants_inventory,
            unpackaged_fresh_cannabis_inventory,
            unpackaged_dried_cannabis_inventory,
            unpackaged_extracts_inventory,
            unpackaged_other_inventory,

            unpackaged_extracts_inhaled_inventory,
            unpackaged_extracts_ingested_inventory,		
            unpackaged_extracts_other_inventory,
            unpackaged_edibles_solid_inventory,
            unpackaged_edibles_nonsolid_inventory,
            unpackaged_topicals_inventory,

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

            --Upackaged weight(#)
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
        $$;



        CREATE OR REPLACE FUNCTION f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer) RETURNS void
        LANGUAGE plpgsql
        AS
        $$
        BEGIN
        --opening inventory
        UPDATE health_canada_report
        SET
            -- unpackage (kg)
            unpackaged_seed_opening_inventory = COALESCE(T1.unpackaged_seed_inventory,0)/1000,
            unpackaged_vegetative_plants_opening_inventory = COALESCE(T1.unpackaged_vegetative_plants_inventory,0),
            unpackaged_whole_cannabis_plants_opening_inventory = COALESCE(T1.unpackaged_whole_cannabis_plants_inventory,0),
            unpackaged_fresh_cannabis_opening_inventory = COALESCE(T1.unpackaged_fresh_cannabis_inventory,0)/1000,
            unpackaged_dried_cannabis_opening_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
            unpackaged_extracts_opening_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
            unpackaged_other_opening_inventory = COALESCE(T1.unpackaged_other_inventory,0)/1000,
            
            unpackaged_edibles_solid_opening_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
            unpackaged_edibles_nonsolid_opening_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
            unpackaged_extracts_inhaled_opening_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
            unpackaged_extracts_ingested_opening_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
            unpackaged_extracts_other_opening_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
            unpackaged_topicals_opening_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,

            -- packaged (#)
            packaged_seed_opening_inventory = COALESCE(T1.packaged_seed_inventory,0),
            packaged_vegetative_plants_opening_inventory = COALESCE(T1.packaged_vegetative_plants_inventory,0),
            packaged_fresh_cannabis_opening_inventory = COALESCE(T1.packaged_fresh_cannabis_inventory,0),
            packaged_dried_cannabis_opening_inventory = COALESCE(T1.packaged_dried_cannabis_inventory,0),
            packaged_extracts_opening_inventory = COALESCE(T1.packaged_extracts_inventory,0),
            
            packaged_edibles_solid_opening_inventory = COALESCE(T1.packaged_edibles_solid_inventory,0),
            packaged_edibles_nonsolid_opening_inventory = COALESCE(T1.packaged_edibles_nonsolid_inventory,0),
            packaged_extracts_inhaled_opening_inventory = COALESCE(T1.packaged_extracts_inhaled_inventory,0),
            packaged_extracts_ingested_opening_inventory = COALESCE(T1.packaged_extracts_ingested_inventory,0),
            packaged_extracts_other_opening_inventory = COALESCE(T1.packaged_extracts_other_inventory,0),
            packaged_topicals_opening_inventory = COALESCE(T1.packaged_topicals_inventory,0)

        FROM (
            SELECT * FROM f_get_current_inventory(initial_date, org_id)
        ) AS T1
        WHERE id = report_id;
        END;
        $$;



        CREATE OR REPLACE FUNCTION f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer) RETURNS void
        LANGUAGE plpgsql
        AS
        $$
        BEGIN
        --closing inventory
        UPDATE health_canada_report
        SET
            -- unpackage (kg)
            unpackaged_seed_closing_inventory = COALESCE(T1.unpackaged_seed_inventory,0)/1000,
            unpackaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_vegetative_plants_inventory,0),
            unpackaged_whole_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_whole_cannabis_plants_inventory,0),
            unpackaged_fresh_cannabis_closing_inventory = COALESCE(T1.unpackaged_fresh_cannabis_inventory,0)/1000,
            unpackaged_dried_cannabis_closing_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
            unpackaged_extracts_closing_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
            unpackaged_other_closing_inventory = COALESCE(T1.unpackaged_other_inventory,0)/1000,

            unpackaged_extracts_inhaled_closing_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
            unpackaged_extracts_ingested_closing_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
            unpackaged_extracts_other_closing_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
            unpackaged_edibles_solid_closing_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
            unpackaged_edibles_nonsolid_closing_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
            unpackaged_topicals_closing_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,


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
            packaged_seed_closing_inventory_weight = COALESCE(T1.packaged_seed_inventory_weight,0),-- total number of seeds
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
        END;
        $$;



        CREATE OR REPLACE FUNCTION f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
        LANGUAGE plpgsql
        AS
        $$
        BEGIN
        /*
            Adjustment for drying/processing loss
            this includes all the drying processing loss and also all pruning plants and all samples from plants
        */

        UPDATE health_canada_report
        SET
            unpackaged_vegetative_plants_adjustment_loss = coalesce(t3.unpackaged_vegetative_plants_adjustment_loss , 0)/ 1000,
            unpackaged_whole_cannabis_plants_adjustment_loss = coalesce(t3.unpackaged_whole_cannabis_plants_adjustment_loss , 0)/ 1000,
            unpackaged_fresh_cannabis_adjustment_loss = coalesce(t3.unpackaged_fresh_cannabis_adjustment_loss , 0)/ 1000,
            unpackaged_dried_cannabis_adjustment_loss = coalesce(t3.unpackaged_dried_cannabis_adjustment_loss, 0)/ 1000,
            unpackaged_extracts_adjustment_loss = coalesce(t3.unpackaged_extracts_adjustment_loss, 0)/ 1000,
            unpackaged_edibles_solid_adjustment_loss = coalesce(t3.unpackaged_edibles_solid_adjustment_loss, 0)/ 1000,
            unpackaged_edibles_nonsolid_adjustment_loss = coalesce(t3.unpackaged_edibles_nonsolid_adjustment_loss, 0)/ 1000,
            unpackaged_extracts_inhaled_adjustment_loss = coalesce(t3.unpackaged_extracts_inhaled_adjustment_loss, 0)/ 1000,
            unpackaged_extracts_ingested_adjustment_loss = coalesce(t3.unpackaged_extracts_ingested_adjustment_loss, 0)/ 1000,
            unpackaged_extracts_other_adjustment_loss = coalesce(t3.unpackaged_extracts_other_adjustment_loss, 0)/ 1000,
            unpackaged_topicals_adjustment_loss = coalesce(t3.unpackaged_topicals_adjustment_loss, 0)/ 1000
        FROM (
            SELECT
                SUM(t2.amount) filter(
                where t2.type = 'vegetative_plants' ) as unpackaged_vegetative_plants_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'whole_plants' ) as unpackaged_whole_cannabis_plants_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'fresh_cannabis') as unpackaged_fresh_cannabis_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'dry_cannabis' ) as unpackaged_dried_cannabis_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'oil_cannabis') as unpackaged_extracts_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'solid') as unpackaged_edibles_solid_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'nonsolid') as unpackaged_edibles_nonsolid_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'inhaled') as unpackaged_extracts_inhaled_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'ingested') as unpackaged_extracts_ingested_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'other') as unpackaged_extracts_other_adjustment_loss,
                SUM(t2.amount) filter(
                where t2.type = 'topicals') as unpackaged_topicals_adjustment_loss
            from
                (
                select
                    SUM(t1.amount) amount,
                    t1.type
                from (
                    select
                        SUM(cast(data->>'from_qty' as DECIMAL)-cast(data->>'to_qty' as DECIMAL)) as amount,
                        case
                            when name = 'batch_record_dry_weight'
                                or (name = 'batch_record_crude_oil_weight'
                                    and data->>'from_qty_unit' = 'g-wet') then 'fresh_cannabis'
                                when name = 'batch_record_cured_weight'
                                or (name = 'batch_record_crude_oil_weight'
                                    and data->>'from_qty_unit' in ('dry', 'cured')) then 'dry_cannabis'
                                when name = 'batch_record_distilled_oil_weight' then 'oil_cannabis'
                            end as type
                        from
                            activities
                        where
                            name in ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight')
                                and organization_id = org_id
                                and TO_CHAR(timestamp, 'YYYY-MM-DD') between initial_date and final_date

                                group by
                                case
                                    when name = 'batch_record_dry_weight'
                                    or (name = 'batch_record_crude_oil_weight'
                                        and data->>'from_qty_unit' = 'g-wet') then 'fresh_cannabis'
                                    when name = 'batch_record_cured_weight'
                                    or (name = 'batch_record_crude_oil_weight'
                                        and data->>'from_qty_unit' in ('dry', 'cured')) then 'dry_cannabis'
                                    when name = 'batch_record_distilled_oil_weight' then 'oil_cannabis'
                                end
                        union all
                            select
                                SUM(cast(act.data->>'from_qty' as DECIMAL)) as amount,
                                st.data->>'subtype' as type
                            from
                                activities act
                            inner join stats_taxonomies st on
                                st.name = act.data->>'from_qty_unit'
                            where
                                act.name = 'batch_record_final_extracted_weight'
                                AND act.organization_id = org_id
                                AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date  AND final_date
                            group by
                                st.data->>'subtype'
                        union all /*

                                    All g-wet that comes from pruning plants

                                    We need the last stage before the plants_prune activity happened to distinguish beetween veg and whole plants.

                                */
                            select
                                SUM(t0.amount) as amount,
                                case
                                    when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                    when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                end as type
                            from
                                (
                                select
                                    cast(act.data->>'quantity' as DECIMAL) as amount,
                                    (
                                    select
                                        act_stage.data->>'to_stage'
                                    from
                                        activities as act_stage
                                    where
                                        act_stage.name = 'update_stage'
                                        and act_stage.data->>'inventory_id' = act.data->>'inventory_id'
                                        and act_stage.timestamp <= act.timestamp
                                    order by
                                        timestamp desc
                                    limit 1 ) as last_stage_before_activity
                                from
                                    activities as act
                                where
                                    act.name = 'plants_prune'
                                    and organization_id = org_id
                                    and TO_CHAR(timestamp, 'YYYY-MM-DD') between initial_date and final_date) as t0
                            group by
                                case
                                    when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                    when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                end
                        union all /*

                                    All the samples that come from plants

                                    I need the last stage before the activity because they can do multiple stage changes in the same period

                                */
                            select
                                SUM(t0.amount) as amount,
                                case
                                    when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                        or t0.end_type = 'plants' then 'vegetative_plants'
                                        when t0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') then 'whole_plants'
                                    end as type
                                from
                                    (
                                    select
                                        cast(act.data->>'to_qty' as DECIMAL) as amount,
                                        inv.data->'plan'->>'end_type' as end_type,
                                        (
                                        select
                                            act_stage.data->>'to_stage'
                                        from
                                            activities as act_stage
                                        where
                                            act_stage.name = 'update_stage'
                                            and act_stage.data->>'inventory_id' = act.data->>'from_inventory_id'
                                            and act_stage.timestamp <= act.timestamp
                                        order by
                                            timestamp desc
                                        limit 1 ) as last_stage_before_activity
                                    from
                                        activities as act
                                    inner join inventories as inv on
                                        inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                    where
                                        act.name = 'batch_create_sample'
                                        and act.data->>'from_qty_unit' = 'plants'
                                        and act.organization_id = org_id
                                        and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date ) as t0
                                group by
                                    case
                                        when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                            or t0.end_type = 'plants' then 'vegetative_plants'
                                            when t0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') then 'whole_plants'
                                        end
                                union all /*

                                    gets all the destructions from plants, that inventory adjustment wasnt required, which means that they are not

                                    destrying the entire plant but parts of it, so it should be reported on processing loss.

                                    I need the last stage before the activity because they can do multiple stage changes in the same period

                                */
                                    select
                                        SUM(t0.to_qty) as amount,
                                        case
                                            when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                                or t0.last_stage_before_activity isnull then 'vegetative_plants'
                                                else 'whole_plants'
                                            end as type
                                        from
                                            (
                                            select
                                                inv.latest_unit as latest_unit,
                                                inv.latest_stage as latest_stage,
                                                coalesce (cast(act.data->>'to_qty' as decimal),
                                                0) as to_qty,
                                                (
                                                select
                                                    act_stage.data->>'to_stage'
                                                from
                                                    activities as act_stage
                                                where
                                                    act_stage.name = 'update_stage'
                                                    and act_stage.data->>'inventory_id' = act.data->>'from_inventory_id'
                                                    and act_stage.timestamp <= act.timestamp
                                                order by
                                                    timestamp desc
                                                limit 1 ) as last_stage_before_activity
                                            from
                                                activities act
                                            inner join f_inventories_latest_stats_stage(final_date) as inv on inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                            where
                                                act.name = 'queue_for_destruction'
                                                and act.data->'from_qty' is null
                                                -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required)
                                                and act.organization_id = org_id
                                                and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date) as t0
                                        where
                                            t0.latest_unit = 'plants'
                                        group by
                                            case
                                                when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                                    or t0.last_stage_before_activity isnull then 'vegetative_plants'
                                                    else 'whole_plants'
                                                end ) as t1
                                group by t1.type ) as t2 ) as t3
                            where
                                id = report_id;
            END;
            $$;
    """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        -- Drop this columns broke HCR. 
        -- ALTER TABLE health_canada_report DROP COLUMN IF EXISTS unpackaged_other_shipped_analytical_testers;
        -- ALTER TABLE health_canada_report DROP COLUMN IF EXISTS unpackaged_other_produced;
        -- ALTER TABLE health_canada_report DROP COLUMN IF EXISTS unpackaged_other_opening_inventory;
        -- ALTER TABLE health_canada_report DROP COLUMN IF EXISTS unpackaged_other_closing_inventory;


        CREATE OR REPLACE FUNCTION f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
            LANGUAGE plpgsql
        AS
        $$
            /* this functions gets all the samples that have been sent to the lab, but samples for plants, because samples for plants we don't send the entire plant, so it doens't count
            and it goes to adjustment/loss section. */

            BEGIN		
                --shipped to analytical testers (samples)
                UPDATE health_canada_report
                SET 
                    unpackaged_seed_shipped_analytical_testers = COALESCE(T2.unpackaged_seed_shipped_analytical_testers,0)/1000,
                    unpackaged_vegetative_plants_shipped_analytical_testers = 0, -- this goes to adjustment/loss section
                    unpackaged_whole_cannabis_plants_shipped_analytical_testers = 0,-- this goes to adjustment/loss section
                    unpackaged_fresh_shipped_analytical_testers = COALESCE(T2.unpackaged_fresh_shipped_analytical_testers,0)/1000,
                    unpackaged_dried_shipped_analytical_testers = COALESCE(T2.unpackaged_dried_shipped_analytical_testers,0)/1000,
                    unpackaged_extracts_shipped_analytical_testers = COALESCE(T2.unpackaged_extracts_shipped_analytical_testers,0)/1000,
                    
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
                        
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
                        
                    FROM (
                        SELECT 
                            CASE
                                WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act.data->>'from_qty' AS DECIMAL) * CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                                ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                            END AS quantity,
                            st.data->>'subtype' AS subtype,
                            act.data->>'from_qty_unit' AS unit			
                        FROM activities AS act 
                        INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                        INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit'
                        WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                        AND act.name = 'sample_sent_to_lab'
                        AND act_create_sample.data->>'from_qty_unit' != 'plants'
                        --AND act.organization_id = 1 
                        --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                        AND act.organization_id = org_id 
                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 			  
                    ) AS T1
                ) AS T2
                WHERE id = report_id;	
            END;
        $$;



        CREATE OR REPLACE FUNCTION f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
            LANGUAGE plpgsql
        AS
        $$
        BEGIN		
                --unpackaged seed processed and unpacked vegetative plants produced
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
                        WHERE name ='germinate_seeds' 
                        AND organization_id = org_id 
                        AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
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
                            GREATEST(0,COALESCE(CAST(data->>'qty' AS DECIMAL),0)) AS plants_processed
                        FROM activities 			
                        WHERE name = 'update_stage' 
                        AND data->>'to_stage' = 'flowering' 
                        AND organization_id = org_id 
                        AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
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
                        WHERE name = 'batch_record_bud_harvest_weight' 
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
                                    MIN(act_adj.id) AS id
                                FROM activities AS act_adj
                                WHERE act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                                AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= final_date
                                GROUP BY act_adj.data->>'from_inventory_id'
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
                        AND organization_id = org_id 
                        AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date                 
                        
                        ) as t1
                ) AS T2
                WHERE id = report_id;
            
                -- unpackaged new extractions processed and produced
                UPDATE health_canada_report
                set
                    -- extracts produced + oil produced
                    unpackaged_extracts_produced = coalesce(unpackaged_extracts_produced, 0) + (COALESCE(T2.extracts_processed,0)/1000),
                    
                    unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
                    unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
                    unpackaged_extracts_ingested_produced = COALESCE(extracts_ingested, 0)/1000,
                    unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000,
                    unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000,
                    unpackaged_topicals_produced = COALESCE(topicals, 0)/1000,
                    
                    unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
                    unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
                    unpackaged_extracts_ingested_processed = COALESCE(extracts_ingested, 0)/1000,
                    unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000,
                    unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000,
                    unpackaged_topicals_processed = COALESCE(topicals, 0)/1000,
                    
                    unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
                FROM (
                    select
                        sum(coalesce(cast(act.data->>'to_qty' as DECIMAL))) as extracts_processed,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested') AS extracts_ingested,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled') AS extracts_inhaled,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other') AS extracts_other,
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals') AS topicals,
                        -- Other reductions if extracted from oil we need to put it on other reductions to math works.
                        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE act.data->>'from_qty_unit' IN ('crude', 'distilled')) AS reductions_other
                    from
                        activities act
                    inner join stats_taxonomies st on act.data->>'to_qty_unit' = st.name
                    where
                        act.name in ('batch_record_extracted_weight')
                    and act.organization_id = org_id
                    and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date        
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
                    ) as t1
                ) AS T2
                WHERE id = report_id;

        END;
        $$;


        DROP FUNCTION IF EXISTS public.f_serialize_stats_fields(numeric,varchar,varchar,varchar,jsonb,jsonb,varchar);

        CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying) RETURNS record
        LANGUAGE plpgsql
            AS
        $$
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
                    IF ((stage in ('planning', 'propagation', 'germinating', 'vegetation') OR type IN ('received inventory', 'mother', 'mother batch', 'lot'))) OR (data->'plan'->>'end_type'='plants') THEN
                        vegetative_plants := plants;
                    ELSE
                        whole_plants := plants;
                    END IF;
            END IF;

            fresh_cannabis_weight := 0;
            IF (unit = 'g-wet') THEN
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

            extracts_weight := distilled + crude;

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



            IF (type = 'lot item') THEN
                    package_type := 'package';
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
        $$;



        DROP FUNCTION IF EXISTS public.f_get_current_inventory(varchar,integer);

        CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT unpackaged_extracts_inhaled_inventory numeric, OUT unpackaged_extracts_ingested_inventory numeric, OUT unpackaged_extracts_other_inventory numeric, OUT unpackaged_edibles_solid_inventory numeric, OUT unpackaged_edibles_nonsolid_inventory numeric, OUT unpackaged_topicals_inventory numeric, OUT packaged_extracts_inhaled_inventory numeric, OUT packaged_extracts_ingested_inventory numeric, OUT packaged_extracts_other_inventory numeric, OUT packaged_edibles_solid_inventory numeric, OUT packaged_edibles_nonsolid_inventory numeric, OUT packaged_topicals_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric, OUT packaged_extracts_inhaled_inventory_weight numeric, OUT packaged_extracts_ingested_inventory_weight numeric, OUT packaged_extracts_other_inventory_weight numeric, OUT packaged_edibles_solid_inventory_weight numeric, OUT packaged_edibles_nonsolid_inventory_weight numeric, OUT packaged_topicals_inventory_weight numeric) RETURNS record
            LANGUAGE plpgsql
        AS
        $$

            DECLARE
                initial_date character varying;
                final_day numeric;
            BEGIN	
                -- since we shouldn't include the 1st day of the month for opening inventory
                SELECT EXTRACT(DAY FROM TO_DATE(final_date, 'YYYY-MM-DD')) INTO final_day;
                IF final_day = 1 THEN
                    SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-DD')
                                    - interval '1 day', 'YYYY-MM-DD') INTO final_date;
                    
                        -- get the initial date as 1 year constraint for opening inventory
                    SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-DD') 
                                    - interval '1 year', 'YYYY-MM-DD') INTO initial_date;			
                ELSE
                        -- get the initial date as 1 year constraint for closing inventory
                        -- last day of the previus month and year
                    SELECT TO_CHAR(TO_DATE(t1.final_dt, 'YYYY-MM-DD') 
                                    + interval '1 month'
                                    - interval '1 day', 'YYYY-MM-DD') 
                    FROM (
                    SELECT TO_CHAR(TO_DATE(final_date, 'YYYY-MM-01') 									
                                    - interval '1 month'
                                    - interval '1 year'
                                    , 'YYYY-MM-DD') as final_dt
                        ) AS t1 INTO initial_date;		
                    
                
                END IF;	
                            
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
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date) as inv 
                    inner join stats_taxonomies as st on st.name = inv.latest_unit
                    --FROM f_inventories_latest_stats_stage('2020-05-31')  
                    WHERE inv.latest_quantity > 0 and
                        inv.organization_id = org_id AND
                        TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date AND
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' AND
                        type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    --samples that have not been sent to the lab and do not come from plants
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date) as inv
                    --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
                    inner join stats_taxonomies as st on st.name = inv.latest_unit
                    INNER JOIN (
                        SELECT 
                            CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                            MAX(sample_activity.id) AS act_id
                        FROM activities AS sample_activity
                        WHERE 
                            sample_activity.name in ('batch_create_sample', 'sample_sent_to_lab') 
                            AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= final_date
                            --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                            AND sample_activity.data->>'from_qty_unit' != 'plants'
                        GROUP BY sample_activity.data->>'inventory_id'
                    ) AS latest_activity ON inv.id = latest_activity.id
                    INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='batch_create_sample' 
                    WHERE inv.latest_quantity > 0 AND
                            inv.type ='sample' AND
                        inv.organization_id = org_id AND
                        TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 
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
        $$;


        CREATE OR REPLACE FUNCTION public.f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer) RETURNS void
            LANGUAGE plpgsql
        AS
        $$
            BEGIN
                --opening inventory
                UPDATE health_canada_report
                SET 
                    -- unpackage (kg)
                    unpackaged_seed_opening_inventory = COALESCE(T1.unpackaged_seed_inventory,0)/1000,
                    unpackaged_vegetative_plants_opening_inventory = COALESCE(T1.unpackaged_vegetative_plants_inventory,0),
                    unpackaged_whole_cannabis_plants_opening_inventory = COALESCE(T1.unpackaged_whole_cannabis_plants_inventory,0),
                    unpackaged_fresh_cannabis_opening_inventory = COALESCE(T1.unpackaged_fresh_cannabis_inventory,0)/1000,
                    unpackaged_dried_cannabis_opening_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
                    unpackaged_extracts_opening_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
                    
                    unpackaged_edibles_solid_opening_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
                    unpackaged_edibles_nonsolid_opening_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
                    unpackaged_extracts_inhaled_opening_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
                    unpackaged_extracts_ingested_opening_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
                    unpackaged_extracts_other_opening_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
                    unpackaged_topicals_opening_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,
                    
                    
                    -- packaged (#)
                    packaged_seed_opening_inventory = COALESCE(T1.packaged_seed_inventory,0),
                    packaged_vegetative_plants_opening_inventory = COALESCE(T1.packaged_vegetative_plants_inventory,0),
                    packaged_fresh_cannabis_opening_inventory = COALESCE(T1.packaged_fresh_cannabis_inventory,0),
                    packaged_dried_cannabis_opening_inventory = COALESCE(T1.packaged_dried_cannabis_inventory,0),
                    packaged_extracts_opening_inventory = COALESCE(T1.packaged_extracts_inventory,0),
                    
                    packaged_edibles_solid_opening_inventory = COALESCE(T1.packaged_edibles_solid_inventory,0),
                    packaged_edibles_nonsolid_opening_inventory = COALESCE(T1.packaged_edibles_nonsolid_inventory,0),
                    packaged_extracts_inhaled_opening_inventory = COALESCE(T1.packaged_extracts_inhaled_inventory,0),
                    packaged_extracts_ingested_opening_inventory = COALESCE(T1.packaged_extracts_ingested_inventory,0),
                    packaged_extracts_other_opening_inventory = COALESCE(T1.packaged_extracts_other_inventory,0),
                    packaged_topicals_opening_inventory = COALESCE(T1.packaged_topicals_inventory,0)
            
                FROM (
                    --SELECT * FROM f_get_current_inventory('2020-05-01', 1)
                    SELECT * FROM f_get_current_inventory(initial_date, org_id)
                ) AS T1
                WHERE id = report_id;
            END;
        $$;



        CREATE OR REPLACE FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer) RETURNS void
            LANGUAGE plpgsql
        AS
        $$
        BEGIN

            --closing inventory
            UPDATE health_canada_report
            SET 
                -- unpackage (kg)
                unpackaged_seed_closing_inventory = COALESCE(T1.unpackaged_seed_inventory,0)/1000,
                unpackaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_vegetative_plants_inventory,0),
                unpackaged_whole_cannabis_plants_closing_inventory = COALESCE(T1.unpackaged_whole_cannabis_plants_inventory,0),
                unpackaged_fresh_cannabis_closing_inventory = COALESCE(T1.unpackaged_fresh_cannabis_inventory,0)/1000,
                unpackaged_dried_cannabis_closing_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
                unpackaged_extracts_closing_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
                unpackaged_extracts_inhaled_closing_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
                unpackaged_extracts_ingested_closing_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
                unpackaged_extracts_other_closing_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
                unpackaged_edibles_solid_closing_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
                unpackaged_edibles_nonsolid_closing_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
                unpackaged_topicals_closing_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,
                
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
                packaged_seed_closing_inventory_weight = COALESCE(T1.packaged_seed_inventory_weight,0),-- total number of seeds
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
        END;
        $$;


        CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
            LANGUAGE plpgsql
        AS
        $$

            BEGIN
                /*
                    Adjustment for drying/processing loss
                    this includes all the drying processing loss and also all pruning plants and all samples from plants
                */
                update
                    health_canada_report
                set
                    unpackaged_vegetative_plants_adjustment_loss = coalesce(t3.unpackaged_vegetative_plants_adjustment_loss , 0)/ 1000,
                    unpackaged_whole_cannabis_plants_adjustment_loss = coalesce(t3.unpackaged_whole_cannabis_plants_adjustment_loss , 0)/ 1000,
                    unpackaged_fresh_cannabis_adjustment_loss = coalesce(t3.unpackaged_fresh_cannabis_adjustment_loss , 0)/ 1000,
                    unpackaged_dried_cannabis_adjustment_loss = coalesce(t3.unpackaged_dried_cannabis_adjustment_loss, 0)/ 1000,
                    unpackaged_extracts_adjustment_loss = coalesce(t3.unpackaged_extracts_adjustment_loss, 0)/ 1000,
                    unpackaged_edibles_solid_adjustment_loss = coalesce(t3.unpackaged_edibles_solid_adjustment_loss, 0)/ 1000,
                    unpackaged_edibles_nonsolid_adjustment_loss = coalesce(t3.unpackaged_edibles_nonsolid_adjustment_loss, 0)/ 1000,
                    unpackaged_extracts_inhaled_adjustment_loss = coalesce(t3.unpackaged_extracts_inhaled_adjustment_loss, 0)/ 1000,
                    unpackaged_extracts_ingested_adjustment_loss = coalesce(t3.unpackaged_extracts_ingested_adjustment_loss, 0)/ 1000,
                    unpackaged_extracts_other_adjustment_loss = coalesce(t3.unpackaged_extracts_other_adjustment_loss, 0)/ 1000,
                    unpackaged_topicals_adjustment_loss = coalesce(t3.unpackaged_topicals_adjustment_loss, 0)/ 1000
                from
                (
                select
                    SUM(t2.amount) filter(
                    where t2.type = 'vegetative_plants' ) as unpackaged_vegetative_plants_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'whole_plants' ) as unpackaged_whole_cannabis_plants_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'fresh_cannabis') as unpackaged_fresh_cannabis_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'dry_cannabis' ) as unpackaged_dried_cannabis_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'oil_cannabis') as unpackaged_extracts_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'solid') as unpackaged_edibles_solid_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'nonsolid') as unpackaged_edibles_nonsolid_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'inhaled') as unpackaged_extracts_inhaled_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'ingested') as unpackaged_extracts_ingested_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'other') as unpackaged_extracts_other_adjustment_loss,
                    SUM(t2.amount) filter(
                    where t2.type = 'topicals') as unpackaged_topicals_adjustment_loss
                from
                    (
                    select
                        SUM(t1.amount) amount,
                        t1.type
                    from (
                        select
                            SUM(cast(data->>'from_qty' as DECIMAL)-cast(data->>'to_qty' as DECIMAL)) as amount,
                            case
                                when name = 'batch_record_dry_weight'
                                    or (name = 'batch_record_crude_oil_weight'
                                        and data->>'from_qty_unit' = 'g-wet') then 'fresh_cannabis'
                                    when name = 'batch_record_cured_weight'
                                    or (name = 'batch_record_crude_oil_weight'
                                        and data->>'from_qty_unit' in ('dry', 'cured')) then 'dry_cannabis'
                                    when name = 'batch_record_distilled_oil_weight' then 'oil_cannabis'
                                end as type
                            from
                                activities
                            where
                                name in ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight')
                                    and organization_id = org_id
                                    and TO_CHAR(timestamp, 'YYYY-MM-DD') between initial_date and final_date
            
                                    group by
                                    case
                                        when name = 'batch_record_dry_weight'
                                        or (name = 'batch_record_crude_oil_weight'
                                            and data->>'from_qty_unit' = 'g-wet') then 'fresh_cannabis'
                                        when name = 'batch_record_cured_weight'
                                        or (name = 'batch_record_crude_oil_weight'
                                            and data->>'from_qty_unit' in ('dry', 'cured')) then 'dry_cannabis'
                                        when name = 'batch_record_distilled_oil_weight' then 'oil_cannabis'
                                    end
                            union all
                                select
                                    SUM(cast(act.data->>'from_qty' as DECIMAL)) as amount,
                                    st.data->>'subtype' as type
                                from
                                    activities act
                                inner join stats_taxonomies st on
                                    st.name = act.data->>'from_qty_unit'
                                where
                                    act.name = 'batch_record_final_extracted_weight'
                                AND act.organization_id = org_id
                                AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date  AND final_date
                                group by
                                    st.data->>'subtype'
                            union all /*
            
                                        All g-wet that comes from pruning plants
            
                                        We need the last stage before the plants_prune activity happened to distinguish beetween veg and whole plants.
            
                                    */
                                select
                                    SUM(t0.amount) as amount,
                                    case
                                        when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                        when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                    end as type
                                from
                                    (
                                    select
                                        cast(act.data->>'quantity' as DECIMAL) as amount,
                                        (
                                        select
                                            act_stage.data->>'to_stage'
                                        from
                                            activities as act_stage
                                        where
                                            act_stage.name = 'update_stage'
                                            and act_stage.data->>'inventory_id' = act.data->>'inventory_id'
                                            and act_stage.timestamp <= act.timestamp
                                        order by
                                            timestamp desc
                                        limit 1 ) as last_stage_before_activity
                                    from
                                        activities as act
                                    where
                                        act.name = 'plants_prune'
                                        and organization_id = org_id
                                        and TO_CHAR(timestamp, 'YYYY-MM-DD') between initial_date and final_date) as t0
                                group by
                                    case
                                        when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                        when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                    end
                            union all /*
            
                                        All the samples that come from plants
            
                                        I need the last stage before the activity because they can do multiple stage changes in the same period
            
                                    */
                                select
                                    SUM(t0.amount) as amount,
                                    case
                                        when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                            or t0.end_type = 'plants' then 'vegetative_plants'
                                            when t0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') then 'whole_plants'
                                        end as type
                                    from
                                        (
                                        select
                                            cast(act.data->>'to_qty' as DECIMAL) as amount,
                                            inv.data->'plan'->>'end_type' as end_type,
                                            (
                                            select
                                                act_stage.data->>'to_stage'
                                            from
                                                activities as act_stage
                                            where
                                                act_stage.name = 'update_stage'
                                                and act_stage.data->>'inventory_id' = act.data->>'from_inventory_id'
                                                and act_stage.timestamp <= act.timestamp
                                            order by
                                                timestamp desc
                                            limit 1 ) as last_stage_before_activity
                                        from
                                            activities as act
                                        inner join inventories as inv on
                                            inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                        where
                                            act.name = 'batch_create_sample'
                                            and act.data->>'from_qty_unit' = 'plants'
                                            and act.organization_id = org_id
                                            and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date ) as t0
                                    group by
                                        case
                                            when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                                or t0.end_type = 'plants' then 'vegetative_plants'
                                                when t0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') then 'whole_plants'
                                            end
                                    union all /*
            
                                        gets all the destructions from plants, that inventory adjustment wasnt required, which means that they are not
            
                                        destrying the entire plant but parts of it, so it should be reported on processing loss.
            
                                        I need the last stage before the activity because they can do multiple stage changes in the same period
            
                                    */
                                        select
                                            SUM(t0.to_qty) as amount,
                                            case
                                                when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                                    or t0.last_stage_before_activity isnull then 'vegetative_plants'
                                                    else 'whole_plants'
                                                end as type
                                            from
                                                (
                                                select
                                                    inv.latest_unit as latest_unit,
                                                    inv.latest_stage as latest_stage,
                                                    coalesce (cast(act.data->>'to_qty' as decimal),
                                                    0) as to_qty,
                                                    (
                                                    select
                                                        act_stage.data->>'to_stage'
                                                    from
                                                        activities as act_stage
                                                    where
                                                        act_stage.name = 'update_stage'
                                                        and act_stage.data->>'inventory_id' = act.data->>'from_inventory_id'
                                                        and act_stage.timestamp <= act.timestamp
                                                    order by
                                                        timestamp desc
                                                    limit 1 ) as last_stage_before_activity
                                                from
                                                    activities act
                                                inner join f_inventories_latest_stats_stage(final_date) as inv on inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                                where
                                                    act.name = 'queue_for_destruction'
                                                    and act.data->'from_qty' is null
                                                    -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required)
                                                    and act.organization_id = org_id
                                                    and TO_CHAR(act.timestamp, 'YYYY-MM-DD') between initial_date and final_date) as t0
                                            where
                                                t0.latest_unit = 'plants'
                                            group by
                                                case
                                                    when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')
                                                        or t0.last_stage_before_activity isnull then 'vegetative_plants'
                                                        else 'whole_plants'
                                                    end ) as t1
                                    group by t1.type ) as t2 ) as t3
                                where
                                    id = report_id;
                        END;
                $$;
    """
    )
