"""new-end-types-hcr-shipped-testers

Revision ID: bdd8b2345e34
Revises: 6257b2dbcb30
Create Date: 2021-06-15 09:28:18.576478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdd8b2345e34'
down_revision = '6257b2dbcb30'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
         RETURNS void
         LANGUAGE plpgsql
        AS $function$
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
        --				AND act.organization_id = 1 
        --				AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                        AND act.organization_id = org_id 
                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 			  
                    ) AS T1
                ) AS T2
                WHERE id = report_id;	     
            END;$function$
        ;        
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
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
                    unpackaged_extracts_shipped_analytical_testers = COALESCE(T2.unpackaged_extracts_shipped_analytical_testers,0)/1000		
                FROM (
                    SELECT 
                        SUM(T1.quantity) FILTER(WHERE T1.unit = 'seeds') AS unpackaged_seed_shipped_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.unit = 'dry' OR T1.unit = 'cured') AS unpackaged_dried_shipped_analytical_testers,
                        SUM(T1.quantity) FILTER(WHERE T1.unit = 'distilled' OR T1.unit = 'crude') AS unpackaged_extracts_shipped_analytical_testers
                        
                    FROM (
                        SELECT 
                            CASE
                                WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act.data->>'from_qty' AS DECIMAL) * CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                                ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                            END AS quantity,
                            act.data->>'from_qty_unit' AS unit			
                        FROM activities AS act 
                        INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                        WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                        AND act.name = 'sample_sent_to_lab'
                        AND act_create_sample.data->>'from_qty_unit' != 'plants'
                        --AND act.organization_id = 1 
                        --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'			
                        AND act.organization_id = org_id 
                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 			  
                    ) AS T1
                    
                ) AS T2
                WHERE id = report_id;	
                
            END;$function$
            ;
        """
    )
