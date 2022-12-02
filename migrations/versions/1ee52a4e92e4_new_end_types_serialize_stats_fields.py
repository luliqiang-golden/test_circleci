"""new-end-types-serialize-stats-fields

Revision ID: 1ee52a4e92e4
Revises: fd3d376c9b7f
Create Date: 2021-06-14 14:32:54.582258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ee52a4e92e4'
down_revision = 'fd3d376c9b7f'
branch_labels = None
depends_on = None


def upgrade():

    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS f_serialize_stats_fields(numeric,varchar,varchar,varchar,jsonb,jsonb);
        
            CREATE OR REPLACE FUNCTION f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying default null, 
            OUT seeds_qty numeric, 
            OUT packaged_seeds_qty numeric,
            OUT seeds_weight numeric, 
            OUT whole_plants numeric, 
            OUT vegetative_plants numeric, 
            OUT packaged_vegetative_plants_qty numeric, 
            OUT fresh_cannabis_weight numeric,
            OUT dried_cannabis_weight numeric, 
            OUT extracts_weight numeric, 
            OUT extracts_inhaled_weight numeric,
            OUT extracts_ingested_weight numeric,
            OUT extracts_other_weight numeric,
            OUT edibles_solid_weight numeric,
            OUT edibles_non_solid_weight numeric,
            OUT topicals_weight numeric,
            OUT fresh_cannabis_qty numeric, 
            OUT dried_cannabis_qty numeric, 
            OUT extracts_qty numeric,
            OUT extracts_inhaled_qty numeric,
            OUT extracts_ingested_qty numeric,
            OUT extracts_other_qty numeric,
            OUT edibles_solid_qty numeric,
            OUT edibles_non_solid_qty numeric,
            OUT topicals_qty numeric,
            OUT package_type character varying)
             RETURNS record
             LANGUAGE plpgsql
            AS $function$
                    DECLARE
                        plants DECIMAL;
                        dry DECIMAL;
                        cured DECIMAL;
                        distilled DECIMAL;
                        crude DECIMAL;
                        taxonomy json;
                    BEGIN
                    
                    package_type := 'unpackage';
                    
                    seeds_qty := 0;
                    IF (unit = 'seeds') THEN
                        seeds_qty := GREATEST(0,quantity);
                    END IF;
                    
                    IF (seeds_qty > 0) THEN
                        IF (type = 'received inventory') THEN
                            seeds_weight = GREATEST(0,COALESCE(CAST(data->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
                        ELSIF (type = 'batch') THEN
                        IF (attributes->>'seed_weight') THEN
                            seeds_weight = GREATEST(0,COALESCE(CAST(attributes->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
                        ELSE
                            seeds_weight = GREATEST(0,COALESCE(CAST(attributes->>'seeds_weight' AS DECIMAL), 0));
                        END IF;
                        ELSIF (type = 'sample') THEN
                            seeds_weight = GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL), 0));
                        ELSE
                            seeds_weight = 0;
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
            $function$;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS f_serialize_stats_fields(numeric,varchar,varchar,varchar,jsonb,jsonb,varchar);
            
            CREATE OR REPLACE FUNCTION f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT package_type character varying)
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
                        seeds_weight = GREATEST(0,COALESCE(CAST(data->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
                    ELSIF (type = 'batch') THEN
                        seeds_weight = GREATEST(0,COALESCE(CAST(attributes->>'seeds_weight' AS DECIMAL), 0));
                    ELSIF (type = 'sample') THEN
                        seeds_weight = GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL), 0));
                    ELSE
                        seeds_weight = 0;
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
                        END IF;
                END IF;
                
                END;
                $function$
;
        """
    )
