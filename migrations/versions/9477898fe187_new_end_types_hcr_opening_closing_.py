"""new-end-types-hcr-opening-closing-inventory

Revision ID: 9477898fe187
Revises: f66d24c3e242
Create Date: 2021-06-15 08:57:10.478607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9477898fe187'
down_revision = 'f66d24c3e242'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
               CREATE OR REPLACE FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer)
                RETURNS void
                LANGUAGE plpgsql
               AS $function$
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
            END;$function$
           ;
           
           
            CREATE OR REPLACE FUNCTION public.f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
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
            
            END;$function$
;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
            BEGIN		
                --closing inventory
                UPDATE health_canada_report
                SET 
                    -- unpackage (kg)
                    unpackaged_seed_closing_inventory = COALESCE(T2.unpackaged_seed_inventory,0)/1000,
                    unpackaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T2.unpackaged_vegetative_plants_inventory,0),
                    unpackaged_whole_cannabis_plants_closing_inventory = COALESCE(T2.unpackaged_whole_cannabis_plants_inventory,0),
                    unpackaged_fresh_cannabis_closing_inventory = COALESCE(T2.unpackaged_fresh_cannabis_inventory,0)/1000,
                    unpackaged_dried_cannabis_closing_inventory = COALESCE(T2.unpackaged_dried_cannabis_inventory,0)/1000,
                    unpackaged_extracts_closing_inventory = COALESCE(T2.unpackaged_extracts_inventory,0)/1000,
                    -- packaged (#)
                    packaged_seed_closing_inventory = COALESCE(T2.packaged_seed_inventory,0),
                    packaged_vegetative_cannabis_plants_closing_inventory = COALESCE(T2.packaged_vegetative_plants_inventory,0),
                    packaged_fresh_cannabis_closing_inventory = COALESCE(T2.packaged_fresh_cannabis_inventory,0),
                    packaged_dried_cannabis_closing_inventory = COALESCE(T2.packaged_dried_cannabis_inventory,0),
                    packaged_extracts_closing_inventory = COALESCE(T2.packaged_extracts_inventory,0),
                    -- packaged weight (kg)
                    packaged_seed_closing_inventory_weight = COALESCE(T2.packaged_seed_inventory_weight,0),-- total number of seeds
                    packaged_fresh_cannabis_closing_inventory_weight = COALESCE(T2.packaged_fresh_cannabis_inventory_weight,0)/1000,
                    packaged_dried_cannabis_closing_inventory_weight = COALESCE(T2.packaged_dried_cannabis_inventory_weight,0)/1000,
                    packaged_extracts_closing_inventory_weight = COALESCE(T2.packaged_extracts_inventory_weight,0)/1000



                FROM (
                    --SELECT * FROM f_get_current_inventory('2020-05-31', 1)
                    SELECT * FROM f_get_current_inventory(final_date, org_id)
                ) AS T2
                WHERE id = report_id;	

            END;$function$
            ;
            
            
            CREATE OR REPLACE FUNCTION public.f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
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
                    -- packaged (#)
                    packaged_seed_opening_inventory = COALESCE(T1.packaged_seed_inventory,0),
                    packaged_vegetative_plants_opening_inventory = COALESCE(T1.packaged_vegetative_plants_inventory,0),
                    packaged_fresh_cannabis_opening_inventory = COALESCE(T1.packaged_fresh_cannabis_inventory,0),
                    packaged_dried_cannabis_opening_inventory = COALESCE(T1.packaged_dried_cannabis_inventory,0),
                    packaged_extracts_opening_inventory = COALESCE(T1.packaged_extracts_inventory,0)

                FROM (
                    --SELECT * FROM f_get_current_inventory('2020-05-01', 1)
                    SELECT * FROM f_get_current_inventory(initial_date, org_id)
                ) AS T1
                WHERE id = report_id;	

            END;$function$
            ;
        """
    )
