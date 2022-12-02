"""fix propagate clones 2.0

Revision ID: b19422a872df
Revises: 28fb16b803e7
Create Date: 2021-09-01 14:55:16.081454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b19422a872df'
down_revision = '28fb16b803e7'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
    RETURNS void
    LANGUAGE plpgsql
AS $$
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
                
                SELECT 
                    0,
                    COALESCE((data->>'to_qty')::numeric, 0) as clones
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
--				AND act.organization_id = 1 
--				AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
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
    """)


def downgrade():
    connection = op.get_bind()
    connection.execute("""
CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
    RETURNS void
    LANGUAGE plpgsql
AS $$
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
--				AND act.organization_id = 1 
--				AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
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
    """)
