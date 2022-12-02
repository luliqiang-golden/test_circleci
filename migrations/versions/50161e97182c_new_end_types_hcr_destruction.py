"""new-end-types-hcr-destruction

Revision ID: 50161e97182c
Revises: e9393a564e7b
Create Date: 2021-06-15 09:17:01.966855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50161e97182c'
down_revision = 'e9393a564e7b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_destroyed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
         RETURNS void
         LANGUAGE plpgsql
        AS $function$
        BEGIN		
            --destroyed
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_destroyed = COALESCE(T2.unpackaged_seed_destroyed,0)/1000,
                unpackaged_vegetative_plants_destroyed = COALESCE(T2.unpackaged_vegetative_plants_destroyed,0),
                unpackaged_whole_cannabis_plants_destroyed = COALESCE(T2.unpackaged_whole_cannabis_plants_destroyed,0),
                unpackaged_fresh_cannabis_destroyed = COALESCE(T2.unpackaged_fresh_cannabis_destroyed,0)/1000,
                unpackaged_dried_cannabis_destroyed = COALESCE(T2.unpackaged_dried_cannabis_destroyed,0)/1000,
                unpackaged_extracts_destroyed = COALESCE(T2.unpackaged_extracts_destroyed,0)/1000,
                
                unpackaged_edibles_solid_destroyed = COALESCE(T2.unpackaged_edibles_solid_destroyed,0)/1000,
                unpackaged_edibles_nonsolid_destroyed = COALESCE(T2.unpackaged_edibles_nonsolid_destroyed,0)/1000,
                unpackaged_extracts_inhaled_destroyed = COALESCE(T2.unpackaged_extracts_inhaled_destroyed,0)/1000,
                unpackaged_extracts_ingested_destroyed = COALESCE(T2.unpackaged_extracts_ingested_destroyed,0)/1000,
                unpackaged_extracts_other_destroyed = COALESCE(T2.unpackaged_extracts_other_destroyed,0)/1000,
                unpackaged_topicals_destroyed = COALESCE(T2.unpackaged_topicals_destroyed,0)/1000,
                
                packaged_seed_destroyed = COALESCE(T2.packaged_seed_destroyed,0),
                packaged_vegetative_plants_destroyed = COALESCE(T2.packaged_vegetative_plants_destroyed,0),
                packaged_fresh_cannabis_destroyed = COALESCE(T2.packaged_fresh_cannabis_destroyed,0),
                packaged_dried_cannabis_destroyed = COALESCE(T2.packaged_dried_cannabis_destroyed,0),
                packaged_extracts_destroyed = COALESCE(T2.packaged_extracts_destroyed,0),
                
                packaged_edibles_solid_destroyed = COALESCE(T2.packaged_edibles_solid_destroyed,0)/1000,
                packaged_edibles_nonsolid_destroyed = COALESCE(T2.packaged_edibles_nonsolid_destroyed,0)/1000,
                packaged_extracts_inhaled_destroyed = COALESCE(T2.packaged_extracts_inhaled_destroyed,0)/1000,
                packaged_extracts_ingested_destroyed = COALESCE(T2.packaged_extracts_ingested_destroyed,0)/1000,
                packaged_extracts_other_destroyed = COALESCE(T2.packaged_extracts_other_destroyed,0)/1000,
                packaged_topicals_destroyed = COALESCE(T2.packaged_topicals_destroyed,0)/1000
            FROM (
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE(T1.weight_destroyed,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'solid') AND T1.type != 'lot item') AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type != 'lot item') AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type != 'lot item') AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type != 'lot item') AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'other') AND T1.type != 'lot item') AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type != 'lot item') AS unpackaged_topicals_destroyed,
                    
                    -- packaged (#)
                    COUNT(*) FILTER (WHERE T1.unit = 'seeds' AND T1.type = 'lot item') AS packaged_seed_destroyed,			
                    COUNT(*) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type = 'lot item') AS packaged_vegetative_plants_destroyed,					 
                    COUNT(*) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type = 'lot item') AS packaged_whole_cannabis_plants_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.type = 'lot item') AS packaged_fresh_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type = 'lot item') AS packaged_dried_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type = 'lot item') AS packaged_extracts_destroyed,
                    
                    COUNT(*) FILTER (WHERE (T1.subtype = 'solid') AND T1.type = 'lot item') AS packaged_edibles_solid_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type = 'lot item') AS packaged_edibles_nonsolid_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type = 'lot item') AS packaged_extracts_inhaled_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type = 'lot item') AS packaged_extracts_ingested_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'other') AND T1.type = 'lot item') AS packaged_extracts_other_destroyed,
                    COUNT(*) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type = 'lot item') AS packaged_topicals_destroyed
                    
                FROM (
                    SELECT
                        CASE
                        /* receive inventory, mother and lot are always vegetative plants and do not have a stage associated with it
                         we need to know the stage before it was destroyed to know if it was vegetative or whole plants */
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot'))) OR (T0.end_type = 'plants')
                            THEN 'vegetative_plants'
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type not in ('received inventory', 'mother', 'mother batch', 'lot')))
                            THEN 'whole_plants'
                        ELSE T0.from_unit
                        END AS unit,
                        T0.*
                    FROM (
                        SELECT
                            CAST(act.data->>'from_qty' AS DECIMAL) AS quantity,
                            CAST(act.data->>'to_qty' AS DECIMAL) AS weight_destroyed,
                            act.data->>'from_qty_unit' AS from_unit,
                            inv.type AS type,
                            inv.data->'plan'->>'end_type' AS end_type,
                            st.data->>'subtype' as subtype,
                            
                            (SELECT act_stage.data->>'to_stage' 
                            FROM activities AS act_stage 
                            WHERE act_stage.name = 'update_stage' AND 
                                    act_stage.data->>'inventory_id' = act.data->>'from_inventory_id' AND
                                    act_stage.timestamp <= act.timestamp
                            ORDER BY timestamp DESC
                            LIMIT 1	 		
                            ) AS last_stage_before_activity
                        FROM activities as act 
                        INNER JOIN inventories AS inv ON CAST(inv.id AS VARCHAR) = act.data->>'from_inventory_id'
                        inner join stats_taxonomies st on st.name = act.data->>'from_qty_unit'
                        /* for destruction section we rely on queue_for_destruction activity, and prunning is not included because when we prune a plant, 
                        we don't destroy the entire plant but just small portion which does not count for the destruction section */
                        WHERE act.name ='queue_for_destruction' AND
                            act.data->>'reason_for_destruction' != 'pruning' AND
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
        --					act.organization_id = 1 AND
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                    ) AS T0
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
            CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_destroyed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
            BEGIN		
                --destroyed
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_destroyed = COALESCE(T2.unpackaged_seed_destroyed,0)/1000,
                    unpackaged_vegetative_plants_destroyed = COALESCE(T2.unpackaged_vegetative_plants_destroyed,0),
                    unpackaged_whole_cannabis_plants_destroyed = COALESCE(T2.unpackaged_whole_cannabis_plants_destroyed,0),
                    unpackaged_fresh_cannabis_destroyed = COALESCE(T2.unpackaged_fresh_cannabis_destroyed,0)/1000,
                    unpackaged_dried_cannabis_destroyed = COALESCE(T2.unpackaged_dried_cannabis_destroyed,0)/1000,
                    unpackaged_extracts_destroyed = COALESCE(T2.unpackaged_extracts_destroyed,0)/1000,
                    packaged_seed_destroyed = COALESCE(T2.packaged_seed_destroyed,0),
                    packaged_vegetative_plants_destroyed = COALESCE(T2.packaged_vegetative_plants_destroyed,0),
                    packaged_fresh_cannabis_destroyed = COALESCE(T2.packaged_fresh_cannabis_destroyed,0),
                    packaged_dried_cannabis_destroyed = COALESCE(T2.packaged_dried_cannabis_destroyed,0),
                    packaged_extracts_destroyed = COALESCE(T2.packaged_extracts_destroyed,0)
                FROM (
                    SELECT 
                        -- unpackage (kg)
                        SUM(COALESCE(T1.weight_destroyed,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                        SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                        SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                        SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                        SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                        SUM(COALESCE(T1.weight_destroyed, 0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                        -- packaged (#)
                        COUNT(*) FILTER (WHERE T1.unit = 'seeds' AND T1.type = 'lot item') AS packaged_seed_destroyed,			
                        COUNT(*) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type = 'lot item') AS packaged_vegetative_plants_destroyed,					 
                        COUNT(*) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type = 'lot item') AS packaged_whole_cannabis_plants_destroyed,
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.type = 'lot item') AS packaged_fresh_cannabis_destroyed,
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type = 'lot item') AS packaged_dried_cannabis_destroyed,
                        COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type = 'lot item') AS packaged_extracts_destroyed
                    FROM (
                        SELECT
                            CASE
                            /* receive inventory, mother and lot are always vegetative plants and do not have a stage associated with it
                             we need to know the stage before it was destroyed to know if it was vegetative or whole plants */
                            WHEN T0.from_unit = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot'))) OR (T0.end_type = 'plants')
                                THEN 'vegetative_plants'
                            WHEN T0.from_unit = 'plants' AND ((T0.last_stage_before_activity not in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type not in ('received inventory', 'mother', 'mother batch', 'lot')))
                                THEN 'whole_plants'
                            ELSE T0.from_unit
                            END AS unit,
                            T0.*
                        FROM (
                            SELECT
                                CAST(act.data->>'from_qty' AS DECIMAL) AS quantity,
                                CAST(act.data->>'to_qty' AS DECIMAL) AS weight_destroyed,
                                act.data->>'from_qty_unit' AS from_unit,
                                inv.type AS type,
                                inv.data->'plan'->>'end_type' AS end_type,
                                (SELECT act_stage.data->>'to_stage' 
                                FROM activities AS act_stage 
                                WHERE act_stage.name = 'update_stage' AND 
                                        act_stage.data->>'inventory_id' = act.data->>'from_inventory_id' AND
                                        act_stage.timestamp <= act.timestamp
                                ORDER BY timestamp DESC
                                LIMIT 1	 		
                                ) AS last_stage_before_activity
                            FROM activities as act 
                            INNER JOIN inventories AS inv ON CAST(inv.id AS VARCHAR) = act.data->>'from_inventory_id'
                            /* for destruction section we rely on queue_for_destruction activity, and prunning is not included because when we prune a plant, 
                            we don't destroy the entire plant but just small portion which does not count for the destruction section */
                            WHERE act.name ='queue_for_destruction' AND
                                act.data->>'reason_for_destruction' != 'pruning' AND
                                act.organization_id = org_id AND
                                TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                                --act.organization_id = 1 AND
                                --TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-11-01'  AND '2020-11-30'
                        ) AS T0
                    ) AS T1
                ) AS T2
                WHERE id = report_id;
                
            END;$function$
        ;
        """
    )
