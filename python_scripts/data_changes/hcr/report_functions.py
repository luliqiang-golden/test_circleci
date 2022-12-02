import psycopg2
import pandas as pd
from acreage_cred import *

conn = psycopg2.connect(f'dbname={DB_NAME} host={DB_HOST} password={DB_PASSWORD} user={DB_USERNAME}')
cursor = conn.cursor()


# Query as DataFrame
def sql_as_df(query, cursor =  cursor):
    # conn = psycopg2.connect(f'dbname={DB_NAME} host={DB_HOST} password={DB_PASSWORD} user={DB_USERNAME}')
    # cursor = conn.cursor()
    cursor.execute(query)
    out_col_headers = [col[0] for col in cursor.description]
    result = dict(zip(out_col_headers, cursor.fetchone()))
    # out_df = pd.DataFrame.from_dict(result.values(), orient='index', columns=out_col_headers)
    return result

# Opening Inventory
def pd_f_hc_report_opening_inventory(initial_date, final_date, org_id):
    query = f'''
    SELECT
        COALESCE(T2.unpackaged_seed_inventory,0)/1000 AS unpackaged_seed_opening_inventory,
        COALESCE(T2.unpackaged_vegetative_plants_inventory,0) AS unpackaged_vegetative_plants_opening_inventory,
        COALESCE(T2.unpackaged_whole_cannabis_plants_inventory,0) AS unpackaged_whole_cannabis_plants_opening_inventory,
        COALESCE(T2.unpackaged_fresh_cannabis_inventory,0)/1000 AS unpackaged_fresh_cannabis_opening_inventory,
        COALESCE(T2.unpackaged_dried_cannabis_inventory,0)/1000 AS unpackaged_dried_cannabis_opening_inventory,
        COALESCE(T2.unpackaged_extracts_inventory,0)/1000 AS unpackaged_extracts_opening_inventory,
        
        COALESCE(T2.packaged_seed_inventory,0) AS packaged_seed_opening_inventory,
        COALESCE(T2.packaged_vegetative_plants_inventory,0) AS packaged_vegetative_plants_opening_inventory,
        COALESCE(T2.packaged_fresh_cannabis_inventory,0) AS packaged_fresh_cannabis_opening_inventory,
        COALESCE(T2.packaged_dried_cannabis_inventory,0) AS packaged_dried_cannabis_opening_inventory,
        COALESCE(T2.packaged_extracts_inventory,0) AS packaged_extracts_opening_inventory
    FROM (
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
            FROM f_inventories_latest_stats_stage('{final_date}')
            --FROM f_inventories_latest_stats_stage('2020-05-31')
            WHERE latest_quantity > 0 and
                organization_id = {org_id} AND
                TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}' AND
                --organization_id = 1 AND
                --TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' AND
                type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
        
            UNION ALL
            --samples that have not been sent to the lab and do not come from plants
            SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes) AS f, inv.type, inv.data
            FROM f_inventories_latest_stats_stage('{final_date}') as inv
            --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
            INNER JOIN (
                SELECT
                    CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                    MAX(sample_activity.id) AS act_id
                FROM activities AS sample_activity
                WHERE
                    sample_activity.name in ('batch_create_sample', 'sample_sent_to_lab')
                    AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '{final_date}'
                    --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                    AND sample_activity.data->>'from_qty_unit' != 'plants'
                GROUP BY sample_activity.data->>'inventory_id'
            ) AS latest_activity ON inv.id = latest_activity.id
            INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='batch_create_sample'
            WHERE inv.latest_quantity > 0 AND
                  inv.type ='sample' AND
                inv.organization_id = {org_id} AND
                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
                --inv.organization_id = 1 AND
                --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31'
            ) AS T1
        ) T2
    '''
    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_inventory_produced_processed(initial_date, final_date, org_id):
    # unpackaged seed processed and unpacked vegetative plants produced : subdf_01
    query = f'''
        SELECT 
            0 AS unpackaged_seed_produced,
            COALESCE(T2.unpackaged_seed_processed,0)/1000 AS unpackaged_seed_processed,
            COALESCE(T2.unpackaged_vegetative_plants_produced,0) AS unpackaged_vegetative_plants_produced
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
                    organization_id = {org_id} AND
                    TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
            ) AS T1
        ) AS T2
        '''
    subdf_01 = sql_as_df(query)
    
    # unpacakged vegetative plants processed and  whole plant produced : subdf_02
    query = f'''
    SELECT 
        COALESCE(T2.plants_processed,0) AS unpackaged_vegetative_plants_processed,
        COALESCE(T2.plants_processed,0) AS unpackaged_whole_cannabis_plants_produced
            FROM (
                SELECT 
                    SUM(COALESCE(T1.plants_processed,0)) AS plants_processed
                FROM (
                    SELECT
                        GREATEST(0,COALESCE(CAST(data->>'qty' AS DECIMAL),0)) AS plants_processed
                    FROM activities
                    WHERE name = 'update_stage' AND 
                        data->>'to_stage' = 'flowering' AND
                        organization_id = {org_id} AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
                ) AS T1
            ) AS T2
    '''
    subdf_02 = sql_as_df(query)
    
    # unpacakged fresh cannabis produced and whole plants processed : subdf_03
    query = f'''
    SELECT 
        COALESCE(T2.fresh_cannabis_produced,0)/1000 AS unpackaged_fresh_cannabis_produced,
        COALESCE(T2.whole_plants_processed,0) AS unpackaged_whole_cannabis_plants_processed
    FROM (
        SELECT
            SUM(COALESCE(T1.fresh_cannabis_produced,0)) AS fresh_cannabis_produced,
            SUM(COALESCE(T1.whole_plants_processed,0)) AS whole_plants_processed
        FROM (
            SELECT
                GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS fresh_cannabis_produced,
                GREATEST(0,COALESCE(CAST(data->>'from_qty' AS DECIMAL),0)) AS whole_plants_processed

            FROM activities
            WHERE name = 'batch_record_harvest_weight' AND
                organization_id = {org_id} AND
                TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
        ) AS T1
    ) AS T2
    '''
    subdf_03 = sql_as_df(query)
    
    # unpacakged dried cannabis produced, unpacakged extracts produced : subdf_04
    query = f'''
    SELECT 
        COALESCE(T2.dried_qty,0)/1000 AS unpackaged_dried_cannabis_produced,
        COALESCE(T2.oil_qty,0)/1000 AS unpackaged_extracts_produced
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
                FROM
                inventories AS inv
                INNER JOIN (
                    SELECT
                    CAST(act_adj.data->>'from_inventory_id' AS bigint) AS inventory_id,
                    MAX(act_adj.id) AS id
                    FROM activities AS act_adj
                    WHERE
                     act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                    AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= '{final_date}'
                    GROUP BY act_adj.data->>'from_inventory_id'
                ) AS T0 ON T0.inventory_id = inv.id
                INNER JOIN activities AS act ON act.id = t0.id
                     WHERE
                     act.organization_id = {org_id} AND
                     TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
            ) AS t1
        ) AS T2
    '''
    subdf_04 = sql_as_df(query)
    
    # dried processed : subdf_05
    query = f'''
    SELECT 
        COALESCE(T2.dried_cannabis_processed,0)/1000 AS unpackaged_dried_cannabis_processed
    FROM (
        SELECT SUM(t1.dried_cannabis_used) AS dried_cannabis_processed from (
        SELECT CAST (data->>'to_qty' AS numeric) as dried_cannabis_used 
            FROM activities 
            WHERE name IN ('batch_record_crude_oil_weight')
            AND data->>'from_qty_unit' in ('cured', 'dry') 
            AND organization_id = {org_id} 
            AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'                 
            ) as t1
    ) AS T2
    
    '''
    subdf_05 = sql_as_df(query)
    
    # unpacakged fresh cannabis processed (amount of fresh cannabis processed : subdf_06
    query = f'''
    SELECT 
        COALESCE(T2.fresh_cannabis_processed,0)/1000 AS unpackaged_fresh_cannabis_processed
    FROM (
        SELECT SUM(t1.fresh_cannabis_used) AS fresh_cannabis_processed from (
        SELECT CAST (data->>'to_qty' AS numeric) as fresh_cannabis_used 
            FROM activities 
            WHERE name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight')
            AND data->>'from_qty_unit' = 'g-wet' 
            AND organization_id = {org_id} 
            AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'                 
            ) as t1
    ) AS T2
    
    '''

    subdf_06 = sql_as_df(query)

    result = dict()
    result.update(subdf_01)
    result.update(subdf_02)
    result.update(subdf_03)
    result.update(subdf_04)
    result.update(subdf_05)
    result.update(subdf_06)

    return result

def pd_f_hc_report_received_inventory(initial_date, final_date, org_id):
    query = f'''
                SELECT	
                    --unpackaged domestic
                    COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000 AS unpackaged_seed_received_domestic,
                    COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0) AS unpackaged_vegetative_plants_received_domestic,
                    COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000 AS unpackaged_fresh_cannabis_received_domestic,
                    COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000 AS unpackaged_dried_cannabis_received_domestic,
                    COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000 AS unpackaged_extracts_received_domestic,
                    --unpackaged imported		
                    COALESCE(T3.unpackaged_seed_received_imported ,0)/1000 AS unpackaged_seed_received_imported,
                    COALESCE(T3.unpackaged_vegetative_plants_received_imported,0) AS unpackaged_vegetative_plants_received_imported,
                    COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000 AS unpackaged_fresh_cannabis_received_imported,
                    COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000 AS unpackaged_dried_cannabis_received_imported,
                    COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000 AS unpackaged_extracts_received_imported,
                    --packaged domestic
                    COALESCE(T3.packaged_seed_received_domestic ,0) AS packaged_seed_received_domestic,
                    COALESCE(T3.packaged_vegetative_plants_received_domestic,0) AS packaged_vegetative_plants_received_domestic,
                    COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0) AS packaged_fresh_cannabis_received_domestic,
                    COALESCE(T3.packaged_dried_cannabis_received_domestic ,0) AS packaged_dried_cannabis_received_domestic,
                    COALESCE(T3.packaged_extracts_received_domestic ,0) AS packaged_extracts_received_domestic
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,				
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, null, inv.type, inv.data, inv.attributes) AS f,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' != org.data->'facility_details'->'facilityAddress'->>'country'  THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            FROM f_inventories_latest_stats_stage('{final_date}')  as inv
                                INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
                                INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                            WHERE type = 'received inventory' AND 
                                inv.organization_id = {org_id} AND
                                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
    '''

    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_other_additions(initial_date, final_date, org_id):
    query = f'''
    SELECT 
        COALESCE(T1.unpackaged_vegetative_plants_other_additions,0) AS unpackaged_vegetative_plants_other_additions
    FROM (       
        SELECT SUM(CAST(data->>'to_qty' as numeric)) as unpackaged_vegetative_plants_other_additions
        FROM activities
        WHERE name = 'propagate_cuttings' AND 
        organization_id = {org_id} AND
        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
    ) AS T1

    '''
    out_df = sql_as_df(query)
    return out_df
    
def pd_f_hc_report_inventory_packaged_label(initial_date, final_date, org_id):
    query = f'''
    SELECT
        COALESCE(T2.unpackaged_seed_packaged_label,0) AS unpackaged_seed_packaged_label,
        COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0) AS unpackaged_vegetative_plants_packaged_label,
        COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0) AS unpackaged_whole_cannabis_plants_packaged_label,
        COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000 AS unpackaged_fresh_cannabis_packaged_label,
        COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000 AS unpackaged_dried_cannabis_packaged_label,
        COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000 unpackaged_extracts_packaged_label,
        COALESCE(T2.packaged_seed_quantity_packaged,0) AS packaged_seed_quantity_packaged,
        COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0) AS packaged_vegetative_plants_quantity_packaged,
        COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0) AS packaged_fresh_cannabis_quantity_packaged,
        COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0) AS packaged_dried_cannabis_quantity_packaged,
        COALESCE(T2.packaged_extracts_quantity_packaged,0) AS packaged_extracts_quantity_packaged
    FROM (
        SELECT 
             -- unpackaged packaged label
            0 AS unpackaged_seed_packaged_label,		
            SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'plants') AS unpackaged_vegetative_plants_packaged_label,
            0 AS unpackaged_whole_cannabis_plants_packaged_label,
            SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_cannabis_packaged_label,
            SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_packaged_label,
            SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
            -- quantity packaged label
            0 AS packaged_seed_quantity_packaged,		
            COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_quantity_packaged,		 
            COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_quantity_packaged,
            COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_quantity_packaged,
            COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged

        FROM (
            SELECT act.*, CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, actTransf.data->>'to_qty_unit' AS unit
            FROM activities AS act
            INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
            WHERE act.name ='create_lot_item' AND
                act.organization_id = {org_id} AND
                TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
        ) AS T1
    ) AS T2
    '''
    out_df = sql_as_df(query)
    return out_df
    
def pd_f_hc_report_inventory_shipped_testers(initial_date, final_date, org_id):
    query = f'''
    SELECT
        COALESCE(T2.unpackaged_seed_shipped_analytical_testers,0)/1000 AS unpackaged_seed_shipped_analytical_testers,
        0 AS unpackaged_vegetative_plants_shipped_analytical_testers, -- this goes to adjustment/loss section
        0 AS unpackaged_whole_cannabis_plants_shipped_analytical_testers,-- this goes to adjustment/loss section
        COALESCE(T2.unpackaged_fresh_shipped_analytical_testers,0)/1000 AS unpackaged_fresh_shipped_analytical_testers,
        COALESCE(T2.unpackaged_dried_shipped_analytical_testers,0)/1000 AS unpackaged_dried_shipped_analytical_testers,
        COALESCE(T2.unpackaged_extracts_shipped_analytical_testers,0)/1000 AS unpackaged_extracts_shipped_analytical_testers
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
            AND act.organization_id = {org_id} 
            AND TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
        ) AS T1

    ) AS T2
    '''
    out_df = sql_as_df(query)
    return out_df
    
def pd_f_hc_report_inventory_adjustment_loss(initial_date, final_date, org_id):
    query = f'''
    SELECT
        COALESCE(T3.unpackaged_vegetative_plants_adjustment_loss ,0)/1000 AS unpackaged_vegetative_plants_adjustment_loss,
        COALESCE(T3.unpackaged_whole_cannabis_plants_adjustment_loss ,0)/1000 AS unpackaged_whole_cannabis_plants_adjustment_loss,
        COALESCE(T3.unpackaged_fresh_cannabis_adjustment_loss ,0)/1000 AS unpackaged_fresh_cannabis_adjustment_loss,
        COALESCE(T3.unpackaged_dried_cannabis_adjustment_loss,0)/1000 AS unpackaged_dried_cannabis_adjustment_loss,
        COALESCE(T3.unpackaged_extracts_adjustment_loss,0)/1000 AS unpackaged_extracts_adjustment_loss
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
                        AND organization_id = {org_id} 
                        AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
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
                        organization_id = {org_id} AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
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
                            act.organization_id = {org_id} AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
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
                        inner join f_inventories_latest_stats_stage('{final_date}') 
                            as inv on inv.id = CAST(act.data->>'from_inventory_id' as numeric)

                        where act.name = 'queue_for_destruction' 
                            and act.data->'from_qty' is null -- this is to check if the data column hasn't the property from_qty (inventory adjustment not required) 
                            and act.organization_id = {org_id} 
                            and TO_CHAR(act.timestamp,'YYYY-MM-DD') between '{initial_date}' and '{final_date}'
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

    '''
    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_inventory_destroyed(initial_date, final_date, org_id):
    query = f'''
    SELECT
        COALESCE(T2.unpackaged_seed_destroyed,0)/1000 AS unpackaged_seed_destroyed,
        COALESCE(T2.unpackaged_vegetative_plants_destroyed,0) AS unpackaged_vegetative_plants_destroyed,
        COALESCE(T2.unpackaged_whole_cannabis_plants_destroyed,0) AS unpackaged_whole_cannabis_plants_destroyed,
        COALESCE(T2.unpackaged_fresh_cannabis_destroyed,0)/1000 AS unpackaged_fresh_cannabis_destroyed,
        COALESCE(T2.unpackaged_dried_cannabis_destroyed,0)/1000 AS unpackaged_dried_cannabis_destroyed,
        COALESCE(T2.unpackaged_extracts_destroyed,0)/1000 AS unpackaged_extracts_destroyed,
        COALESCE(T2.packaged_seed_destroyed,0) AS packaged_seed_destroyed,
        COALESCE(T2.packaged_vegetative_plants_destroyed,0) AS packaged_vegetative_plants_destroyed,
        COALESCE(T2.packaged_fresh_cannabis_destroyed,0) AS packaged_fresh_cannabis_destroyed,
        COALESCE(T2.packaged_dried_cannabis_destroyed,0) AS packaged_dried_cannabis_destroyed,
        COALESCE(T2.packaged_extracts_destroyed,0) AS packaged_extracts_destroyed
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
                    act.organization_id = {org_id} AND
                    TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
            ) AS T0
        ) AS T1
    ) AS T2
    '''
    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_inventory_shipped_domestic(initial_date, final_date, org_id):
    query = f'''
    SELECT
        0 AS packaged_seed_shipped_domestic, -- we don't sell seeds
        COALESCE(T2.packaged_vegetative_plants_shipped_domestic ,0) AS packaged_vegetative_plants_shipped_domestic,
        COALESCE(T2.packaged_fresh_cannabis_shipped_domestic ,0) AS packaged_fresh_cannabis_shipped_domestic,
        COALESCE(T2.packaged_dried_cannabis_shipped_domestic ,0) AS packaged_dried_cannabis_shipped_domestic,
        COALESCE(T2.packaged_extracts_shipped_domestic ,0) AS packaged_extracts_shipped_domestic
    FROM (
        SELECT 
            COUNT(*) FILTER (WHERE T1.unit = 'plants') AS packaged_vegetative_plants_shipped_domestic, 
            COUNT(*) FILTER (WHERE T1.unit = 'g-wet') AS packaged_fresh_cannabis_shipped_domestic, 
            COUNT(*) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS packaged_dried_cannabis_shipped_domestic, 
            COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_shipped_domestic
        FROM (
            SELECT act_map.data->>'inventory_id' AS inventory_id, inv.latest_unit AS unit FROM activities AS act
                INNER JOIN order_items AS oi ON act.data->>'shipment_id' = CAST(oi.shipment_id AS varchar)
                INNER JOIN activities AS act_map ON CAST(oi.id AS varchar) = act_map.data->>'order_item_id' AND act_map.name = 'order_item_map_to_lot_item'
                INNER JOIN f_inventories_latest_stats_stage('{final_date}') AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
            WHERE act.name = 'shipment_shipped' AND
                inv.organization_id = {org_id} AND
                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
        ) AS T1   
    ) AS T2

'''
    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_closing_inventory(initial_date, final_date, org_id):
    query = f'''
    SELECT
        -- unpackage (kg)
        COALESCE(T2.unpackaged_seed_inventory,0)/1000 AS unpackaged_seed_closing_inventory,
        COALESCE(T2.unpackaged_vegetative_plants_inventory,0) AS unpackaged_vegetative_cannabis_plants_closing_inventory,
        COALESCE(T2.unpackaged_whole_cannabis_plants_inventory,0) AS unpackaged_whole_cannabis_plants_closing_inventory,
        COALESCE(T2.unpackaged_fresh_cannabis_inventory,0)/1000 AS unpackaged_fresh_cannabis_closing_inventory,
        COALESCE(T2.unpackaged_dried_cannabis_inventory,0)/1000 AS unpackaged_dried_cannabis_closing_inventory,
        COALESCE(T2.unpackaged_extracts_inventory,0)/1000 AS unpackaged_extracts_closing_inventory,
        -- packaged (#)
        COALESCE(T2.packaged_seed_inventory,0) AS packaged_seed_closing_inventory,
        COALESCE(T2.packaged_vegetative_plants_inventory,0) AS packaged_vegetative_cannabis_plants_closing_inventory,
        COALESCE(T2.packaged_fresh_cannabis_inventory,0) AS packaged_fresh_cannabis_closing_inventory,
        COALESCE(T2.packaged_dried_cannabis_inventory,0) AS packaged_dried_cannabis_closing_inventory,
        COALESCE(T2.packaged_extracts_inventory,0) AS packaged_extracts_closing_inventory,
        -- packaged weight (kg)
        COALESCE(T2.packaged_seed_inventory_weight,0) AS packaged_seed_closing_inventory_weight,-- total number of seeds
        COALESCE(T2.packaged_fresh_cannabis_inventory_weight,0)/1000 AS packaged_fresh_cannabis_closing_inventory_weight,
        COALESCE(T2.packaged_dried_cannabis_inventory_weight,0)/1000 AS packaged_dried_cannabis_closing_inventory_weight,
        COALESCE(T2.packaged_extracts_inventory_weight,0)/1000 AS packaged_extracts_closing_inventory_weight

    FROM (
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
            FROM f_inventories_latest_stats_stage('{final_date}')
            --FROM f_inventories_latest_stats_stage('2020-05-31')
            WHERE latest_quantity > 0 and
                organization_id = {org_id} AND
                TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}' AND
                --organization_id = 1 AND
                --TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' AND
                type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
        
            UNION ALL
            --samples that have not been sent to the lab and do not come from plants
            SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.type, inv.data, inv.attributes) AS f, inv.type, inv.data
            FROM f_inventories_latest_stats_stage('{final_date}') as inv
            --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
            INNER JOIN (
                SELECT
                    CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                    MAX(sample_activity.id) AS act_id
                FROM activities AS sample_activity
                WHERE
                    sample_activity.name in ('batch_create_sample', 'sample_sent_to_lab')
                    AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '{final_date}'
                    --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                    AND sample_activity.data->>'from_qty_unit' != 'plants'
                GROUP BY sample_activity.data->>'inventory_id'
            ) AS latest_activity ON inv.id = latest_activity.id
            INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='batch_create_sample'
            WHERE inv.latest_quantity > 0 AND
                  inv.type ='sample' AND
                inv.organization_id = {org_id} AND
                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
                --inv.organization_id = 1 AND
                --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31'
            ) AS T1
    ) AS T2

    '''
    out_df = sql_as_df(query)
    return out_df

def pd_f_hc_report_return_received_inventory(initial_date, final_date, org_id):
    query = f'''
    SELECT
        --unpackaged return items
        COALESCE(T2.unpackaged_seed_reductions_shipped_returned ,0)/1000 AS unpackaged_seed_reductions_shipped_returned,
        COALESCE(T2.unpackaged_vegetative_plants_reductions_shipped_returned,0) AS unpackaged_vegetative_plants_reductions_shipped_returned,
        COALESCE(T2.unpackaged_fresh_cannabis_reductions_shipped_returned ,0)/1000 AS unpackaged_fresh_cannabis_reductions_shipped_returned,
        COALESCE(T2.unpackaged_dried_cannabis_reductions_shipped_returned ,0)/1000 AS unpackaged_dried_cannabis_reductions_shipped_returned,
        COALESCE(T2.unpackaged_extracts_reductions_shipped_returned ,0)/1000 AS unpackaged_extracts_reductions_shipped_returned
    FROM (
        SELECT 
            -- unpackage(kg)
            SUM(COALESCE(T1.seeds_weight,0)) AS unpackaged_seed_reductions_shipped_returned,
            SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='plants') AS unpackaged_vegetative_plants_reductions_shipped_returned,
            SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='g-wet') AS unpackaged_fresh_cannabis_reductions_shipped_returned,
            SUM(COALESCE(T1.total_qty,0)) FILTER (WHERE T1.unit ='dry' OR T1.unit ='cured') AS unpackaged_dried_cannabis_reductions_shipped_returned,
            SUM(COALESCE(T1.total_qty, 0)) FILTER (WHERE T1.unit ='crude' OR T1.unit ='distilled') AS unpackaged_extracts_reductions_shipped_returned
       FROM (
             SELECT 
             GREATEST(0,COALESCE(CAST(data->>'from_qty' AS DECIMAL),0)) AS total_qty,
             GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL),0)) AS seeds_weight,
             data->>'from_qty_unit' as unit
            FROM activities
            WHERE name = 'received_inventory_return' AND 
            organization_id = {org_id} AND
             TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '{initial_date}' AND '{final_date}'
    ) AS T1
    ) AS T2

'''
    out_df = sql_as_df(query)
    return out_df

