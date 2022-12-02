"""improve HCR query performance

Revision ID: 109986603645
Revises: 5037ac73045e
Create Date: 2022-03-17 01:39:53.785879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '109986603645'
down_revision = '5037ac73045e'
branch_labels = None
depends_on = None


def upgrade():
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

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to cultivators and process
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_cultivators_processors = COALESCE(T2.unpackaged_seed_shipped_cultivators_processors,0),
                unpackaged_vegetative_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_vegetative_plants_shipped_cultivators_processors,0),
                unpackaged_whole_cannabis_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_cultivators_processors,0),
                unpackaged_fresh_shipped_cultivators_processors = COALESCE(T2.unpackaged_fresh_shipped_cultivators_processors,0)/1000,
                unpackaged_dried_shipped_cultivators_processors = COALESCE(T2.unpackaged_dried_shipped_cultivators_processors,0)/1000,
                unpackaged_extracts_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_shipped_cultivators_processors,0)/1000,
                
                
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_solids_shipped_cultivators_processors,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_inhaled_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_inhaled_shipped_cultivators_processors,0)/1000,    
	            unpackaged_extracts_ingested_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_ingested_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_other_shipped_cultivators_processors,0)/1000,
	            unpackaged_topicals_shipped_cultivators_processors = COALESCE(T2.unpackaged_topicals_shipped_cultivators_processors,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_shipped_cultivators_processors,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_cultivators_processors,
					0 AS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_shipped_cultivators_processors,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested' AND T1.unit NOT IN ('distilled', 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_cultivators_processors
                
                FROM (
                
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name = 'create_lot_item' AND
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND
                        	accounts.account_type IN ('distributor','license holder','retailer') AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            actShipped.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                            
                     UNION ALL 
                     
                     SELECT 
                        CAST(act.data->>'from_qty' AS DECIMAL) AS to_qty, 
                        act.data->>'from_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
                        FROM activities AS act
                        INNER JOIN stats_taxonomies AS st ON st.name = act.data->>'from_qty_unit' AND st.organization_id = act.organization_id
                        WHERE act.name = 'send_processor' AND
                              act.organization_id = org_id AND
                              act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                      
            
        END;$function$
;

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
                    SUM(COALESCE(T1.weight_destroyed,T1.quantity,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'solid') AND T1.type != 'lot item') AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type != 'lot item') AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type != 'lot item') AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type != 'lot item') AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'other') AND T1.type != 'lot item') AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type != 'lot item') AS unpackaged_topicals_destroyed,
                    
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

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported = COALESCE(T2.unpackaged_seeds_shipped_exported,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported,0),
                unpackaged_whole_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported,0),
                unpackaged_fresh_cannabis_shipped_exported = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported,0)/1000,
                unpackaged_dried_cannabis_shipped_exported = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported = COALESCE(T2.unpackaged_edibles_solids_shipped_exported,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported,0)/1000,
	            unpackaged_extracts_other_shipped_exported = COALESCE(T2.unpackaged_extracts_other_shipped_exported,0)/1000,
	            unpackaged_topicals_shipped_exported = COALESCE(T2.unpackaged_topicals_shipped_exported,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seeds_shipped_exported,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            actShipped.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export_value(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported_value = COALESCE(T2.unpackaged_seeds_shipped_exported_value,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported_value,0),
                unpackaged_whole_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported_value,0),
                unpackaged_fresh_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported_value,0)/1000,
                unpackaged_dried_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported_value,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_solids_shipped_exported_value,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported_value,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported_value = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported_value,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported_value = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported_value,0)/1000,
	            unpackaged_extracts_other_shipped_exported_value = COALESCE(T2.unpackaged_extracts_other_shipped_exported_value,0)/1000,
	            unpackaged_topicals_shipped_exported_value = COALESCE(T2.unpackaged_topicals_shipped_exported_value,0)/1000
                
                
            FROM (
                SELECT 
                    
                    0 AS unpackaged_seeds_shipped_exported_value,		
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported_value,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported_value,
                    --SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported_value
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type,
						order_items.price AS price
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0),
                    unpackaged_vegetative_plants_packaged_label = COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0),
                    unpackaged_whole_cannabis_plants_packaged_label = COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0),
                    unpackaged_fresh_cannabis_packaged_label = COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000,
                    unpackaged_dried_cannabis_packaged_label = COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000,
                    --unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                    packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                    packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                    packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                    packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                    --packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0),
                    
                    unpackaged_edibles_solid_packaged_label = COALESCE(T2.unpackaged_edibles_solid_packaged_label,0)/1000,
                    unpackaged_edibles_nonsolid_packaged_label = COALESCE(T2.unpackaged_edibles_nonsolid_packaged_label,0)/1000,
                    unpackaged_extracts_inhaled_packaged_label = COALESCE(T2.unpackaged_extracts_inhaled_packaged_label,0)/1000,
                    unpackaged_extracts_ingested_packaged_label = COALESCE(T2.unpackaged_extracts_ingested_packaged_label,0)/1000,
                    unpackaged_extracts_other_packaged_label = COALESCE(T2.unpackaged_extracts_other_packaged_label,0)/1000,
                    unpackaged_topicals_packaged_label = COALESCE(T2.unpackaged_topicals_packaged_label,0)/1000,
                    
                    packaged_edibles_solid_quantity_packaged = COALESCE(T2.packaged_edibles_solid_quantity_packaged,0),
                    packaged_edibles_nonsolid_quantity_packaged = COALESCE(T2.packaged_edibles_nonsolid_quantity_packaged,0),
                    packaged_extracts_inhaled_quantity_packaged = COALESCE(T2.packaged_extracts_inhaled_quantity_packaged,0),
                    packaged_extracts_ingested_quantity_packaged = COALESCE(T2.packaged_extracts_ingested_quantity_packaged,0),
                    packaged_extracts_other_quantity_packaged = COALESCE(T2.packaged_extracts_other_quantity_packaged,0),
                    packaged_topicals_quantity_packaged = COALESCE(T2.packaged_topicals_quantity_packaged,0)
                    
                FROM (
                    SELECT 
                         -- unpackaged packaged label
                        0 AS unpackaged_seed_packaged_label,		
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_packaged_label,
                        0 AS unpackaged_whole_cannabis_plants_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_packaged_label,
                        --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
                        
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_packaged_label,
                        
                        -- quantity packaged label
                        0 AS packaged_seed_quantity_packaged,		
                        COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_quantity_packaged,		 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_quantity_packaged,
                        --COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_quantity_packaged
                    
                    FROM (
                        SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
                        WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
                        (orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') OR (orders.shipping_address->>'country' IS NULL AND orders.shipping_status IS NULL)) AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_researchers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_researchers = COALESCE(T2.unpackaged_seed_shipped_researchers,0),
                unpackaged_vegetative_plants_shipped_researchers = COALESCE(T2.unpackaged_vegetative_plants_shipped_researchers,0),
                unpackaged_whole_cannabis_plants_shipped_researchers = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_researchers,0),
                unpackaged_fresh_shipped_researchers = COALESCE(T2.unpackaged_fresh_shipped_researchers,0)/1000,
                unpackaged_dried_shipped_researchers = COALESCE(T2.unpackaged_dried_shipped_researchers,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_researchers = COALESCE(T2.unpackaged_edibles_solids_shipped_researchers,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_researchers = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_researchers,0)/1000,
	            unpackaged_extracts_inhaled_shipped_researchers = COALESCE(T2.unpackaged_extracts_inhaled_shipped_researchers,0)/1000,    
	            unpackaged_extracts_ingested_shipped_researchers = COALESCE(T2.unpackaged_extracts_ingested_shipped_researchers,0)/1000,
	            unpackaged_extracts_other_shipped_researchers = COALESCE(T2.unpackaged_extracts_other_shipped_researchers,0)/1000,
	            unpackaged_topicals_shipped_researchers = COALESCE(T2.unpackaged_topicals_shipped_researchers,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seed_shipped_researchers,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_researchers,
					0 AS unpackaged_whole_cannabis_plants_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_researchers,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_researchers
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	accounts.account_type = 'researcher' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            actShipped.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;


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
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested' AND (T1.unit != 'distilled' AND T1.unit != 'crude')) AS unpackaged_extracts_ingested_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
            FROM (
                SELECT 
                        CASE
                            WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                            ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                        END AS quantity,
                        st.data->>'subtype' AS subtype,
                        CASE
                            WHEN act_create_sample.data->>'from_qty_unit' = 'plants' THEN 'plants'
                            ELSE act.data->>'from_qty_unit'
                        END AS unit
                        			
                    FROM activities AS act 
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                    INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit' AND st.organization_id = act.organization_id 
                    WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                    AND act.name = 'sample_sent_to_lab'
                    --AND act_create_sample.data->>'from_qty_unit' != 'plants'
                    --AND act.organization_id = 1 
                    --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                    AND act.organization_id = org_id 
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")			  
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_return_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
             BEGIN		
                --return items
                UPDATE health_canada_report
                SET 
                    --unpackaged return items
                    unpackaged_seed_reductions_shipped_returned = COALESCE(T2.unpackaged_seed_reductions_shipped_returned ,0)/1000,
                    unpackaged_vegetative_plants_reductions_shipped_returned = COALESCE(T2.unpackaged_vegetative_plants_reductions_shipped_returned,0),
                    unpackaged_fresh_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_fresh_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_dried_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_dried_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_reductions_shipped_returned ,0)/1000,
                    unpackaged_edibles_solid_reductions_shipped_returned = COALESCE(T2.unpackaged_edibles_solid_reductions_shipped_returned ,0)/1000,
                    unpackaged_edibles_nonsolid_reductions_shipped_returned = COALESCE(T2.unpackaged_edibles_nonsolid_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_inhaled_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_inhaled_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_ingested_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_ingested_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_other_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_other_reductions_shipped_returned ,0)/1000,
                    unpackaged_topicals_reductions_shipped_returned = COALESCE(T2.unpackaged_topicals_reductions_shipped_returned ,0)/1000
                FROM (
                    SELECT 
                        -- unpackage(kg)
                        SUM(COALESCE(T1.seeds_weight,0)) AS unpackaged_seed_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='plants') AS unpackaged_vegetative_plants_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='g-wet') AS unpackaged_fresh_cannabis_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='dry' OR T1.unit ='cured') AS unpackaged_dried_cannabis_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='crude' OR T1.unit ='distilled') AS unpackaged_extracts_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_reductions_shipped_returned
                   FROM (
                         SELECT 
                             GREATEST(0,COALESCE(CAST(act.data->>'from_qty' AS DECIMAL),0)) AS total_qty,
                             GREATEST(0,COALESCE(CAST(act.data->>'seeds_weight' AS DECIMAL),0)) AS seeds_weight,
                             act.data->>'from_qty_unit' as unit,
                             st.data->>'subtype' subtype
                         FROM activities act
                         INNER JOIN stats_taxonomies st ON st.name = act.data->>'from_qty_unit'
                         WHERE  act.name = 'received_inventory_return' AND 
                                act.organization_id = org_id AND
                                act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            --					act.organization_id = 1 AND
            --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01' AND '2021-06-30'
                            ) AS T1
                        ) AS T2
                    WHERE id = report_id;	
            
                END;$function$
;

        
        """)


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
                                        and TO_CHAR(timestamp, 'YYYY-MM-DD') between initial_date and final_date

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
                                        AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
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

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to cultivators and process
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_cultivators_processors = COALESCE(T2.unpackaged_seed_shipped_cultivators_processors,0),
                unpackaged_vegetative_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_vegetative_plants_shipped_cultivators_processors,0),
                unpackaged_whole_cannabis_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_cultivators_processors,0),
                unpackaged_fresh_shipped_cultivators_processors = COALESCE(T2.unpackaged_fresh_shipped_cultivators_processors,0)/1000,
                unpackaged_dried_shipped_cultivators_processors = COALESCE(T2.unpackaged_dried_shipped_cultivators_processors,0)/1000,
                unpackaged_extracts_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_shipped_cultivators_processors,0)/1000,
                
                
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_solids_shipped_cultivators_processors,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_cultivators_processors = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_inhaled_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_inhaled_shipped_cultivators_processors,0)/1000,    
	            unpackaged_extracts_ingested_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_ingested_shipped_cultivators_processors,0)/1000,
	            unpackaged_extracts_other_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_other_shipped_cultivators_processors,0)/1000,
	            unpackaged_topicals_shipped_cultivators_processors = COALESCE(T2.unpackaged_topicals_shipped_cultivators_processors,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_shipped_cultivators_processors,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_cultivators_processors,
					0 AS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_shipped_cultivators_processors,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested' AND T1.unit NOT IN ('distilled', 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_cultivators_processors
                
                FROM (
                
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name = 'create_lot_item' AND
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND
                        	accounts.account_type IN ('distributor','license holder','retailer') AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                            
                     UNION ALL 
                     
                     SELECT 
                        CAST(act.data->>'from_qty' AS DECIMAL) AS to_qty, 
                        act.data->>'from_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype
                        FROM activities AS act
                        INNER JOIN stats_taxonomies AS st ON st.name = act.data->>'from_qty_unit' AND st.organization_id = act.organization_id
                        WHERE act.name = 'send_processor' AND
                              act.organization_id = org_id AND
                              TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                      
            
        END;$function$
;

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
                    SUM(COALESCE(T1.weight_destroyed,T1.quantity,0)) FILTER (WHERE T1.unit = 'seeds' AND T1.type != 'lot item') AS unpackaged_seed_destroyed,			
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'vegetative_plants' AND T1.type != 'lot item') AS unpackaged_vegetative_plants_destroyed,					 
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'whole_plants' AND T1.type != 'lot item') AS unpackaged_whole_cannabis_plants_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'g-wet' AND T1.type != 'lot item') AS unpackaged_fresh_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured') AND T1.type != 'lot item') AS unpackaged_dried_cannabis_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude') AND T1.type != 'lot item') AS unpackaged_extracts_destroyed,
                    
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'solid') AND T1.type != 'lot item') AS unpackaged_edibles_solid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'nonsolid') AND T1.type != 'lot item') AS unpackaged_edibles_nonsolid_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'inhaled') AND T1.type != 'lot item') AS unpackaged_extracts_inhaled_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'ingested') AND T1.type != 'lot item') AS unpackaged_extracts_ingested_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'other') AND T1.type != 'lot item') AS unpackaged_extracts_other_destroyed,
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE (T1.subtype = 'topicals') AND T1.type != 'lot item') AS unpackaged_topicals_destroyed,
                    
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
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
        --					act.organization_id = 1 AND
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                    ) AS T0
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported = COALESCE(T2.unpackaged_seeds_shipped_exported,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported,0),
                unpackaged_whole_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported,0),
                unpackaged_fresh_cannabis_shipped_exported = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported,0)/1000,
                unpackaged_dried_cannabis_shipped_exported = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported = COALESCE(T2.unpackaged_edibles_solids_shipped_exported,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported,0)/1000,
	            unpackaged_extracts_other_shipped_exported = COALESCE(T2.unpackaged_extracts_other_shipped_exported,0)/1000,
	            unpackaged_topicals_shipped_exported = COALESCE(T2.unpackaged_topicals_shipped_exported,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seeds_shipped_exported,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export_value(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported_value = COALESCE(T2.unpackaged_seeds_shipped_exported_value,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported_value,0),
                unpackaged_whole_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported_value,0),
                unpackaged_fresh_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported_value,0)/1000,
                unpackaged_dried_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported_value,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_solids_shipped_exported_value,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_exported_value = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_exported_value,0)/1000,
	            unpackaged_extracts_inhaled_shipped_exported_value = COALESCE(T2.unpackaged_extracts_inhaled_shipped_exported_value,0)/1000,    
	            unpackaged_extracts_ingested_shipped_exported_value = COALESCE(T2.unpackaged_extracts_ingested_shipped_exported_value,0)/1000,
	            unpackaged_extracts_other_shipped_exported_value = COALESCE(T2.unpackaged_extracts_other_shipped_exported_value,0)/1000,
	            unpackaged_topicals_shipped_exported_value = COALESCE(T2.unpackaged_topicals_shipped_exported_value,0)/1000
                
                
            FROM (
                SELECT 
                    
                    0 AS unpackaged_seeds_shipped_exported_value,		
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_cannabis_plants_shipped_exported_value,
					0 AS unpackaged_whole_cannabis_plants_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported_value,
                    --SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_exported_value
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type,
						order_items.price AS price
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
                        WHERE act.name ='create_lot_item' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' NOT IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
                UPDATE health_canada_report
                SET 		
                    unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0),
                    unpackaged_vegetative_plants_packaged_label = COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0),
                    unpackaged_whole_cannabis_plants_packaged_label = COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0),
                    unpackaged_fresh_cannabis_packaged_label = COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000,
                    unpackaged_dried_cannabis_packaged_label = COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000,
                    --unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                    packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                    packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                    packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                    packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                    --packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0),
                    
                    unpackaged_edibles_solid_packaged_label = COALESCE(T2.unpackaged_edibles_solid_packaged_label,0)/1000,
                    unpackaged_edibles_nonsolid_packaged_label = COALESCE(T2.unpackaged_edibles_nonsolid_packaged_label,0)/1000,
                    unpackaged_extracts_inhaled_packaged_label = COALESCE(T2.unpackaged_extracts_inhaled_packaged_label,0)/1000,
                    unpackaged_extracts_ingested_packaged_label = COALESCE(T2.unpackaged_extracts_ingested_packaged_label,0)/1000,
                    unpackaged_extracts_other_packaged_label = COALESCE(T2.unpackaged_extracts_other_packaged_label,0)/1000,
                    unpackaged_topicals_packaged_label = COALESCE(T2.unpackaged_topicals_packaged_label,0)/1000,
                    
                    packaged_edibles_solid_quantity_packaged = COALESCE(T2.packaged_edibles_solid_quantity_packaged,0),
                    packaged_edibles_nonsolid_quantity_packaged = COALESCE(T2.packaged_edibles_nonsolid_quantity_packaged,0),
                    packaged_extracts_inhaled_quantity_packaged = COALESCE(T2.packaged_extracts_inhaled_quantity_packaged,0),
                    packaged_extracts_ingested_quantity_packaged = COALESCE(T2.packaged_extracts_ingested_quantity_packaged,0),
                    packaged_extracts_other_quantity_packaged = COALESCE(T2.packaged_extracts_other_quantity_packaged,0),
                    packaged_topicals_quantity_packaged = COALESCE(T2.packaged_topicals_quantity_packaged,0)
                    
                FROM (
                    SELECT 
                         -- unpackaged packaged label
                        0 AS unpackaged_seed_packaged_label,		
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_packaged_label,
                        0 AS unpackaged_whole_cannabis_plants_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_packaged_label,
                        --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
                        
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_packaged_label,
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_packaged_label,
                        
                        -- quantity packaged label
                        0 AS packaged_seed_quantity_packaged,		
                        COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_quantity_packaged,		 
                        COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_quantity_packaged,
                        --COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_quantity_packaged
                    
                    FROM (
                        SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
                        WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
                        (orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') OR (orders.shipping_address->>'country' IS NULL AND orders.shipping_status IS NULL)) AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_researchers(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_researchers = COALESCE(T2.unpackaged_seed_shipped_researchers,0),
                unpackaged_vegetative_plants_shipped_researchers = COALESCE(T2.unpackaged_vegetative_plants_shipped_researchers,0),
                unpackaged_whole_cannabis_plants_shipped_researchers = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_researchers,0),
                unpackaged_fresh_shipped_researchers = COALESCE(T2.unpackaged_fresh_shipped_researchers,0)/1000,
                unpackaged_dried_shipped_researchers = COALESCE(T2.unpackaged_dried_shipped_researchers,0)/1000,
                --unpackaged_other_shipped_domestic_researchers = COALESCE(T2.unpackaged_other_shipped_domestic_researchers,0)/1000,
                
                -- new endtypes
	            unpackaged_edibles_solids_shipped_researchers = COALESCE(T2.unpackaged_edibles_solids_shipped_researchers,0)/1000,
	            unpackaged_edibles_nonsolids_shipped_researchers = COALESCE(T2.unpackaged_edibles_nonsolids_shipped_researchers,0)/1000,
	            unpackaged_extracts_inhaled_shipped_researchers = COALESCE(T2.unpackaged_extracts_inhaled_shipped_researchers,0)/1000,    
	            unpackaged_extracts_ingested_shipped_researchers = COALESCE(T2.unpackaged_extracts_ingested_shipped_researchers,0)/1000,
	            unpackaged_extracts_other_shipped_researchers = COALESCE(T2.unpackaged_extracts_other_shipped_researchers,0)/1000,
	            unpackaged_topicals_shipped_researchers = COALESCE(T2.unpackaged_topicals_shipped_researchers,0)/1000
                
                
            FROM (
                SELECT 
                     -- unpackaged sent to researcher
                    0 AS unpackaged_seed_shipped_researchers,		
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_shipped_researchers,
					0 AS unpackaged_whole_cannabis_plants_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_researchers,
                    --SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_ingested_shipped_researchers
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_shipped_researchers
                
                FROM (
                    
                
                	SELECT 
                        CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, 
                        actTransf.data->>'to_qty_unit' AS unit, 
                        st.data->>'subtype' AS subtype,
						s.package_type AS package_type,
						orders.shipping_status AS shipping_status,
						orders.shipping_address->>'country' AS country,
						accounts.account_type AS account_type
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id 
						LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
						LEFT JOIN activities AS actOrders ON (act.data->>'inventory_id' = actOrders.data->>'inventory_id' AND actOrders.name = 'order_item_map_to_lot_item')
						LEFT JOIN order_items AS order_items ON order_items.id = CAST(actOrders.data->>'order_item_id' as bigint) 
						LEFT JOIN orders AS orders ON orders.id = order_items.order_id
						LEFT JOIN crm_accounts AS accounts ON orders.crm_account_id = accounts.id
						LEFT JOIN activities AS actShipped ON act.data->>'inventory_id' = actShipped.data->>'inventory_id' AND actShipped.name = 'inventory_adjustment' AND actShipped.data->>'activity_name' = 'shipment_shipped'
                        WHERE act.name ='create_lot_item' AND 
                        	accounts.account_type = 'researcher' AND 
                        	s.package_type = 'unpackaged' AND 
                        	orders.shipping_address->>'country' IN ('ca', 'Canada', 'canada') AND 
                        	orders.shipping_status IN ('shipped', 'delivered') AND
                        
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(actShipped.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
        END;$function$
;


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
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'ingested' AND (T1.unit != 'distilled' AND T1.unit != 'crude')) AS unpackaged_extracts_ingested_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'other') AS unpackaged_extracts_other_analytical_testers,
                SUM(T1.quantity) FILTER(WHERE T1.subtype = 'topicals') AS unpackaged_topicals_analytical_testers
            FROM (
                SELECT 
                        CASE
                            WHEN act.data->>'from_qty_unit' = 'seeds' THEN CAST(act_create_sample.data->>'seeds_weight' AS DECIMAL)
                            ELSE CAST(act.data->>'from_qty' AS DECIMAL) 
                        END AS quantity,
                        st.data->>'subtype' AS subtype,
                        CASE
                            WHEN act_create_sample.data->>'from_qty_unit' = 'plants' THEN 'plants'
                            ELSE act.data->>'from_qty_unit'
                        END AS unit
                        			
                    FROM activities AS act 
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='batch_create_sample'
                    INNER JOIN stats_taxonomies st ON st.name = act.DATA->>'from_qty_unit' AND st.organization_id = act.organization_id 
                    WHERE act.data->>'to_test_status' <> 'batch-create-sample' 
                    AND act.name = 'sample_sent_to_lab'
                    --AND act_create_sample.data->>'from_qty_unit' != 'plants'
                    --AND act.organization_id = 1 
                    --AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'			
                    AND act.organization_id = org_id 
                    AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date 			  
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$
;

CREATE OR REPLACE FUNCTION public.f_hc_report_return_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
             BEGIN		
                --return items
                UPDATE health_canada_report
                SET 
                    --unpackaged return items
                    unpackaged_seed_reductions_shipped_returned = COALESCE(T2.unpackaged_seed_reductions_shipped_returned ,0)/1000,
                    unpackaged_vegetative_plants_reductions_shipped_returned = COALESCE(T2.unpackaged_vegetative_plants_reductions_shipped_returned,0),
                    unpackaged_fresh_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_fresh_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_dried_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_dried_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_reductions_shipped_returned ,0)/1000,
                    unpackaged_edibles_solid_reductions_shipped_returned = COALESCE(T2.unpackaged_edibles_solid_reductions_shipped_returned ,0)/1000,
                    unpackaged_edibles_nonsolid_reductions_shipped_returned = COALESCE(T2.unpackaged_edibles_nonsolid_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_inhaled_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_inhaled_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_ingested_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_ingested_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_other_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_other_reductions_shipped_returned ,0)/1000,
                    unpackaged_topicals_reductions_shipped_returned = COALESCE(T2.unpackaged_topicals_reductions_shipped_returned ,0)/1000
                FROM (
                    SELECT 
                        -- unpackage(kg)
                        SUM(COALESCE(T1.seeds_weight,0)) AS unpackaged_seed_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='plants') AS unpackaged_vegetative_plants_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='g-wet') AS unpackaged_fresh_cannabis_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='dry' OR T1.unit ='cured') AS unpackaged_dried_cannabis_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='crude' OR T1.unit ='distilled') AS unpackaged_extracts_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'solid') AS unpackaged_edibles_solid_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolid_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'other') AS unpackaged_extracts_other_reductions_shipped_returned,
                        SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.subtype = 'topicals') AS unpackaged_topicals_reductions_shipped_returned
                   FROM (
                         SELECT 
                             GREATEST(0,COALESCE(CAST(act.data->>'from_qty' AS DECIMAL),0)) AS total_qty,
                             GREATEST(0,COALESCE(CAST(act.data->>'seeds_weight' AS DECIMAL),0)) AS seeds_weight,
                             act.data->>'from_qty_unit' as unit,
                             st.data->>'subtype' subtype
                         FROM activities act
                         INNER JOIN stats_taxonomies st ON st.name = act.data->>'from_qty_unit'
                         WHERE  act.name = 'received_inventory_return' AND 
                                act.organization_id = org_id AND
                                TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
            --					act.organization_id = 1 AND
            --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01' AND '2021-06-30'
                            ) AS T1
                        ) AS T2
                    WHERE id = report_id;	
            
                END;$function$
;

        
        """)
