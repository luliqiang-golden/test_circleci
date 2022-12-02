"""new-end-types-hcr-adjustment-loss

Revision ID: e9393a564e7b
Revises: c4766806dfa8
Create Date: 2021-06-15 09:13:29.866413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9393a564e7b'
down_revision = 'c4766806dfa8'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        create or replace function public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer) 
            returns void language plpgsql as $function$ begin 
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
                    end;
                $function$;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer)
             RETURNS void
             LANGUAGE plpgsql
            AS $function$
            BEGIN		
                /* 
                    Adjustment for drying/processing loss
                    this includes all the drying processing loss and also all pruning plants and all samples from plants
                */
                UPDATE health_canada_report
                SET 
                    unpackaged_vegetative_plants_adjustment_loss = COALESCE(T3.unpackaged_vegetative_plants_adjustment_loss ,0)/1000,
                    unpackaged_whole_cannabis_plants_adjustment_loss = COALESCE(T3.unpackaged_whole_cannabis_plants_adjustment_loss ,0)/1000,
                    unpackaged_fresh_cannabis_adjustment_loss = COALESCE(T3.unpackaged_fresh_cannabis_adjustment_loss ,0)/1000,
                    unpackaged_dried_cannabis_adjustment_loss = COALESCE(T3.unpackaged_dried_cannabis_adjustment_loss,0)/1000,
                    unpackaged_extracts_adjustment_loss = COALESCE(T3.unpackaged_extracts_adjustment_loss,0)/1000
                FROM (
                    SELECT SUM(T2.amount) FILTER(WHERE T2.type ='vegetative_plants' ) as unpackaged_vegetative_plants_adjustment_loss,	   
                        SUM(T2.amount) FILTER(WHERE T2.type ='whole_plants' ) as unpackaged_whole_cannabis_plants_adjustment_loss,
                        SUM(T2.amount) FILTER(WHERE T2.type ='fresh_cannabis') as unpackaged_fresh_cannabis_adjustment_loss,
                        SUM(T2.amount) FILTER(WHERE T2.type ='dry_cannabis' ) as unpackaged_dried_cannabis_adjustment_loss,
                        SUM(T2.amount) FILTER(WHERE T2.type ='oil_cannabis') as unpackaged_extracts_adjustment_loss
                        
                    FROM (
                        SELECT 
                                SUM(T1.amount) amount, T1.type 
                        FROM ( 
                                /*
                                    All the loss processing	
                                    this relies on 'batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight' activities
                                    Say we record a dry weight from a fresh cannabis with 50 g-wet, and get 20 g-dry, so in that case we lost 30g
                                    
                                */
                            
                                SELECT SUM(CAST(data->>'from_qty' AS DECIMAL)-CAST(data->>'to_qty' AS DECIMAL)) AS amount, 
                                CASE 
                                    WHEN name = 'batch_record_dry_weight' OR (name = 'batch_record_crude_oil_weight' AND data->>'from_qty_unit' = 'g-wet') THEN 'fresh_cannabis'
                                    WHEN name = 'batch_record_cured_weight' OR (name = 'batch_record_crude_oil_weight' AND data->>'from_qty_unit' in ('dry', 'cured')) THEN 'dry_cannabis'
                                    WHEN name = 'batch_record_distilled_oil_weight' THEN 'oil_cannabis'
                                END as type
                                FROM activities 
                                WHERE name IN 
                            ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_cured_weight', 'batch_record_distilled_oil_weight')
                                    AND organization_id = org_id 
                                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date			  
--                                      AND organization_id = 1 
--                                      AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'  
                            GROUP BY CASE
                                    WHEN name = 'batch_record_dry_weight' OR (name = 'batch_record_crude_oil_weight' AND data->>'from_qty_unit' = 'g-wet') THEN 'fresh_cannabis'
                                    WHEN name = 'batch_record_cured_weight' OR (name = 'batch_record_crude_oil_weight' AND data->>'from_qty_unit' in ('dry', 'cured')) THEN 'dry_cannabis'
                                    WHEN name = 'batch_record_distilled_oil_weight' THEN 'oil_cannabis'
                                    END
                                
                                
                                UNION ALL
                                /*
                                    All g-wet that comes from pruning plants			 
                                    We need the last stage before the plants_prune activity happened to distinguish beetween veg and whole plants.
                                */
                                SELECT 
                                    SUM(T0.amount) AS amount,
                                    CASE
                                    WHEN T0.last_stage_before_activity = 'vegetation' THEN 'vegetative_plants'
                                    WHEN T0.last_stage_before_activity != 'vegetation' THEN 'whole_plants'
                                    END AS type
                                FROM (
                                    SELECT
                                        CAST(act.data->>'quantity' AS DECIMAL) AS amount, 
                                        (SELECT act_stage.data->>'to_stage' 
                                        FROM activities AS act_stage 
                                        WHERE act_stage.name = 'update_stage' AND 
                                                act_stage.data->>'inventory_id' = act.data->>'inventory_id' AND
                                                act_stage.timestamp <= act.timestamp
                                        ORDER BY timestamp DESC
                                        LIMIT 1	 		
                                        ) AS last_stage_before_activity
                                    FROM activities as act
                                WHERE act.name = 'plants_prune' AND
                                    organization_id = org_id AND
                                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
--                                       act.organization_id = 1 AND
--                                       TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-30'  	
                                ) AS T0
                                GROUP BY CASE
                                        WHEN T0.last_stage_before_activity = 'vegetation' THEN 'vegetative_plants'
                                        WHEN T0.last_stage_before_activity != 'vegetation' THEN 'whole_plants'
                                        END
                                    
                                            
                                UNION all
                                /*
                                    All the samples that come from plants	 
                                    I need the last stage before the activity because they can do multiple stage changes in the same period
                                */
                                
                               SELECT
									SUM(T0.amount) AS amount,
									CASE
									WHEN T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR t0.end_type = 'plants' THEN 'vegetative_plants'
									WHEN T0.last_stage_before_activity  not in ('planning', 'propagation', 'germinating', 'vegetation') THEN 'whole_plants'
									END AS type		
								FROM (
									SELECT 
										CAST(act.data->>'to_qty' AS DECIMAL) AS amount, 
										inv.data->'plan'->>'end_type' AS end_type,
										(SELECT act_stage.data->>'to_stage' 
										FROM activities AS act_stage 
										WHERE act_stage.name = 'update_stage' AND 
												act_stage.data->>'inventory_id' = act.data->>'from_inventory_id' AND
												act_stage.timestamp <= act.timestamp
										ORDER BY timestamp DESC
										LIMIT 1	 		
										) AS last_stage_before_activity
									FROM activities AS act
									 INNER JOIN inventories as inv ON inv.id = CAST(act.data->>'from_inventory_id' AS NUMERIC)
									WHERE act.name='batch_create_sample' AND
										act.data->>'from_qty_unit' = 'plants' AND
--                                         act.organization_id = 1 AND
--                                         TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'  		
                                        act.organization_id = org_id AND
                                        TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                                ) AS T0
                                GROUP BY CASE
                                        WHEN T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR t0.end_type = 'plants' THEN 'vegetative_plants'
										WHEN T0.last_stage_before_activity  not in ('planning', 'propagation', 'germinating', 'vegetation') THEN 'whole_plants'
										END	
							   union all 
							   /*
                                    gets all the destructions from plants, that inventory adjustment wasnt required, which means that they are not 
                                    destrying the entire plant but parts of it, so it should be reported on processing loss.
                                    I need the last stage before the activity because they can do multiple stage changes in the same period
                                */
							   select 
										sum(t0.to_qty) as amount,
								        case
									        when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')  or t0.last_stage_before_activity isnull then 'vegetative_plants'
									        else 'whole_plants'
								        end AS type
								from (
									select inv.latest_unit as latest_unit, 
										   inv.latest_stage as latest_stage,
										   coalesce (cast(act.data->>'to_qty' as decimal),0) as to_qty,
										   	(SELECT act_stage.data->>'to_stage' 
												FROM activities AS act_stage 
												WHERE act_stage.name = 'update_stage' AND 
														act_stage.data->>'inventory_id' = act.data->>'from_inventory_id' AND
														act_stage.timestamp <= act.timestamp
												ORDER BY timestamp DESC
												LIMIT 1	 		
											) AS last_stage_before_activity
										   
									
									from activities act 
									inner join f_inventories_latest_stats_stage(final_date) 
									--inner join f_inventories_latest_stats_stage('2021-02-28')  
										as inv on inv.id = CAST(act.data->>'from_inventory_id' as numeric)
									
									where act.name = 'queue_for_destruction' 
										and act.data->'from_qty' is null -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required) 
										and act.organization_id = org_id 
										and TO_CHAR(act.timestamp,'YYYY-MM-DD') between initial_date and final_date
										--and act.organization_id = 1
										--and TO_CHAR(act.timestamp,'YYYY-MM-DD') between '2021-02-01' and '2021-02-28'  	
								) as t0
								where t0.latest_unit = 'plants'
								group by 
									case
									    when t0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation')  or t0.last_stage_before_activity isnull then 'vegetative_plants'
									    else 'whole_plants'
									end 
									
                        ) AS T1
                        GROUP BY T1.type
                    ) AS T2
                ) AS T3
                WHERE id = report_id;		
                
            END;$function$
;

        """
    )
