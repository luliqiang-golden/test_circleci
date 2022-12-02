"""adjust HCR to handle dequeue

Revision ID: 23496a860c3a
Revises: f845ab6b9c93
Create Date: 2022-08-12 18:21:48.490725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23496a860c3a'
down_revision = 'f845ab6b9c93'
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
	        SET enable_nestloop = off;
	       
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
                    SUM(COALESCE(T1.weight_destroyed,T1.quantity,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'solid') AND T1.type != 'lot item') AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type != 'lot item') AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type != 'lot item') AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type != 'lot item' AND T1.unit NOT IN ('crude', 'distilled')) AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'other') AND T1.type != 'lot item' AND T1.unit NOT IN ('sift', 'terpene', 'biomass', 'cannabinoid')) AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type != 'lot item') AS unpackaged_topicals_destroyed,
                    
                    -- packaged (#)
                    COUNT(*) FILTER (WHERE T1.unit = 'seeds' AND T1.type = 'lot item') AS packaged_seed_destroyed,			
                    COUNT(*) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type = 'lot item') AS packaged_vegetative_plants_destroyed,					 
                    COUNT(*) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type = 'lot item') AS packaged_whole_cannabis_plants_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.type = 'lot item') AS packaged_fresh_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type = 'lot item') AS packaged_dried_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND T1.type = 'lot item') AS packaged_extracts_destroyed,
                    
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
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot')))
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
                        inner join stats_taxonomies st on st.name = act.data->>'from_qty_unit' AND st.organization_id = org_id
                        /* for destruction section we rely on queue_for_destruction activity, and prunning is not included because when we prune a plant, 
                        we don't destroy the entire plant but just small portion which does not count for the destruction section */
                        WHERE act.name ='queue_for_destruction' AND act.deleted = FALSE AND
                            act.data->>'reason_for_destruction' != 'pruning' AND
                            act.organization_id = org_id AND
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
        --					act.organization_id = 1 AND
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                    ) AS T0
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;



















CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
                BEGIN
                /*
                    Adjustment for drying/processing loss
                    this includes all the drying processing loss and also all pruning plants and all samples from plants
                */
	            SET enable_nestloop = off;

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
                        where t2.type IN ('oil_cannabis', 'extracts')) as unpackaged_extracts_adjustment_loss,
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
                                    when name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'g-wet' then 'fresh_cannabis'
                                    when name IN ('batch_record_cured_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' in ('dry', 'cured') then 'dry_cannabis'
                                    when name IN ('batch_record_distilled_oil_weight') and data->>'from_qty_unit' in ('crude', 'distilled') then 'oil_cannabis'
                                    end as type
                                from
                                    activities
                                where
                                    name in ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight')
                                        and organization_id = org_id
                                        and timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")

                                        group by
                                        case
                                        when name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'g-wet' then 'fresh_cannabis'
                                        when name IN ('batch_record_cured_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' in ('dry', 'cured') then 'dry_cannabis'
                                        when name IN ('batch_record_distilled_oil_weight') and data->>'from_qty_unit' in ('crude', 'distilled') then 'oil_cannabis'
                                        end
                                union all
                                    select
                                        SUM(cast(act.data->>'from_qty' as DECIMAL) - cast(act.data->>'to_qty' as DECIMAL)) as amount,
                                        'extracts' as type
                                    from
                                        activities act
                                    inner join stats_taxonomies st on
                                        st.name = act.data->>'to_qty_unit' AND st.organization_id = act.organization_id
                                    where
                                        act.name = 'batch_record_final_extracted_weight'
                                        AND act.organization_id = org_id
                                        AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                                            and timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")) as t0
                                    group by
                                        case
                                            when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                            when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                        end
                                union all /*

                                            gets all the destructions from plants, that inventory adjustment wasnt required, which means that they are not

                                            destrying the entire plant but parts of it, so it should be reported on processing loss.

                                            I need the last stage before the activity because they can do multiple stage changes in the same period

                                        */
                                                                                
                                            SELECT
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
                                                    inner JOIN f_inventories_latest_stats_stage(final_date, org_id) as inv on inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                                    where
                                                        act.name = 'queue_for_destruction' AND act.deleted = FALSE
                                                        AND act.data->>'reason_for_destruction' NOT IN ('Ungerminated seeds', 'pruning')
                                                        -- and act.data->'from_qty' is null
                                                        -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required)
                                                        and --inv.organization_id = 1 AND
                                                            --inv.timestamp >= cast('2021-11-01' as date)
                                                            inv.organization_id = org_id AND
                                                            inv.timestamp >= cast(initial_date as date) ) as t0
                                            INNER JOIN (SELECT unnest(array['planning', 'propagation', 'germinating', 'vegetation', 'flowering']) AS "stage") AS stages_before_activity 
                                            ON t0.last_stage_before_activity = stages_before_activity.stage
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
                    $function$
;













        """)


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
	        SET enable_nestloop = off;
	       
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
                    SUM(COALESCE(T1.weight_destroyed,T1.quantity,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'solid') AND T1.type != 'lot item') AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type != 'lot item') AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type != 'lot item') AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type != 'lot item' AND T1.unit NOT IN ('crude', 'distilled')) AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'other') AND T1.type != 'lot item' AND T1.unit NOT IN ('sift', 'terpene', 'biomass', 'cannabinoid')) AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type != 'lot item') AS unpackaged_topicals_destroyed,
                    
                    -- packaged (#)
                    COUNT(*) FILTER (WHERE T1.unit = 'seeds' AND T1.type = 'lot item') AS packaged_seed_destroyed,			
                    COUNT(*) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type = 'lot item') AS packaged_vegetative_plants_destroyed,					 
                    COUNT(*) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type = 'lot item') AS packaged_whole_cannabis_plants_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit = 'g-wet' AND T1.type = 'lot item') AS packaged_fresh_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type = 'lot item') AS packaged_dried_cannabis_destroyed,
                    COUNT(*) FILTER (WHERE T1.unit IN ('distilled', 'crude', 'sift', 'terpene', 'biomass', 'cannabinoid') AND T1.type = 'lot item') AS packaged_extracts_destroyed,
                    
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
                        WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot')))
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
                        inner join stats_taxonomies st on st.name = act.data->>'from_qty_unit' AND st.organization_id = org_id
                        /* for destruction section we rely on queue_for_destruction activity, and prunning is not included because when we prune a plant, 
                        we don't destroy the entire plant but just small portion which does not count for the destruction section */
                        WHERE act.name ='queue_for_destruction' AND
                            act.data->>'reason_for_destruction' != 'pruning' AND
                            act.organization_id = org_id AND
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
        --					act.organization_id = 1 AND
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                    ) AS T0
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;











CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
                BEGIN
                /*
                    Adjustment for drying/processing loss
                    this includes all the drying processing loss and also all pruning plants and all samples from plants
                */
	            SET enable_nestloop = off;

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
                        where t2.type IN ('oil_cannabis', 'extracts')) as unpackaged_extracts_adjustment_loss,
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
                                    when name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'g-wet' then 'fresh_cannabis'
                                    when name IN ('batch_record_cured_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' in ('dry', 'cured') then 'dry_cannabis'
                                    when name IN ('batch_record_distilled_oil_weight') and data->>'from_qty_unit' in ('crude', 'distilled') then 'oil_cannabis'
                                    end as type
                                from
                                    activities
                                where
                                    name in ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight')
                                        and organization_id = org_id
                                        and timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")

                                        group by
                                        case
                                        when name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'g-wet' then 'fresh_cannabis'
                                        when name IN ('batch_record_cured_weight', 'batch_record_crude_oil_weight') and data->>'from_qty_unit' in ('dry', 'cured') then 'dry_cannabis'
                                        when name IN ('batch_record_distilled_oil_weight') and data->>'from_qty_unit' in ('crude', 'distilled') then 'oil_cannabis'
                                        end
                                union all
                                    select
                                        SUM(cast(act.data->>'from_qty' as DECIMAL) - cast(act.data->>'to_qty' as DECIMAL)) as amount,
                                        'extracts' as type
                                    from
                                        activities act
                                    inner join stats_taxonomies st on
                                        st.name = act.data->>'to_qty_unit' AND st.organization_id = act.organization_id
                                    where
                                        act.name = 'batch_record_final_extracted_weight'
                                        AND act.organization_id = org_id
                                        AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                                            and timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")) as t0
                                    group by
                                        case
                                            when t0.last_stage_before_activity = 'vegetation' then 'vegetative_plants'
                                            when t0.last_stage_before_activity != 'vegetation' then 'whole_plants'
                                        end
                                union all /*

                                            gets all the destructions from plants, that inventory adjustment wasnt required, which means that they are not

                                            destrying the entire plant but parts of it, so it should be reported on processing loss.

                                            I need the last stage before the activity because they can do multiple stage changes in the same period

                                        */
                                                                                
                                            SELECT
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
                                                    inner JOIN f_inventories_latest_stats_stage(final_date, org_id) as inv on inv.id = cast(act.data->>'from_inventory_id' as numeric)
                                                    where
                                                        act.name = 'queue_for_destruction'
                                                        AND act.data->>'reason_for_destruction' NOT IN ('Ungerminated seeds', 'pruning')
                                                        -- and act.data->'from_qty' is null
                                                        -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required)
                                                        and --inv.organization_id = 1 AND
                                                            --inv.timestamp >= cast('2021-11-01' as date)
                                                            inv.organization_id = org_id AND
                                                            inv.timestamp >= cast(initial_date as date) ) as t0
                                            INNER JOIN (SELECT unnest(array['planning', 'propagation', 'germinating', 'vegetation', 'flowering']) AS "stage") AS stages_before_activity 
                                            ON t0.last_stage_before_activity = stages_before_activity.stage
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
                    $function$
;

        """)
