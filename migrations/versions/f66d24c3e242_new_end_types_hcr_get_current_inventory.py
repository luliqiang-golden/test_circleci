"""new-end-types-hcr-get-current-inventory

Revision ID: f66d24c3e242
Revises: 256a80ac3d86
Create Date: 2021-06-15 08:50:48.486443

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f66d24c3e242'
down_revision = '256a80ac3d86'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS public.f_get_current_inventory(varchar, int4);
            
            CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, 
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
             
            END;$function$;                
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS f_get_current_inventory(final_date varchar, org_id integer);
            
            CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric)
             RETURNS record
             LANGUAGE plpgsql
            AS $function$
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
                                
                                -- packaged (#)
                                SUM(COALESCE((f).packaged_seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory,
                                SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_vegetative_plants_inventory,				
                                SUM(COALESCE((f).fresh_cannabis_qty, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory,
                                SUM(COALESCE((f).dried_cannabis_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory,
                                SUM(COALESCE((f).extracts_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory,
                                -- packaged weight(#)
                                SUM(COALESCE((f).seeds_qty,0)) FILTER (WHERE (f).package_type ='package') AS packaged_seed_inventory_weight, -- total number of seeds
                                SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='package') AS packaged_fresh_cannabis_inventory_weight,
                                SUM(COALESCE((f).dried_cannabis_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_dried_cannabis_inventory_weight,
                                SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='package') AS packaged_extracts_inventory_weight
            
                            FROM (
                                SELECT f_serialize_stats_fields(latest_quantity, latest_unit, latest_stage, type, data, attributes) AS f, type, data
                                FROM f_inventories_latest_stats_stage(final_date)  
                                --FROM f_inventories_latest_stats_stage('2020-05-31')  
                                WHERE latest_quantity > 0 and
                                    organization_id = org_id AND
                                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date AND
                                    --organization_id = 1 AND
                                    --TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' AND
                                    type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                                UNION ALL
                                --samples that have not been sent to the lab and do not come from plants
                                SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes) AS f, inv.type, inv.data
                                FROM f_inventories_latest_stats_stage(final_date) as inv
                                --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
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
                                    --Packaged (#)
                                    packaged_seed_inventory,
                                    packaged_vegetative_plants_inventory,				
                                    packaged_fresh_cannabis_inventory,
                                    packaged_dried_cannabis_inventory,
                                    packaged_extracts_inventory,
                                    --Upackaged weight(#)
                                    packaged_seed_inventory_weight,
                                    packaged_fresh_cannabis_inventory_weight,
                                    packaged_dried_cannabis_inventory_weight,
                                    packaged_extracts_inventory_weight;
            
                        END;$function$
            ;
        """
    )
