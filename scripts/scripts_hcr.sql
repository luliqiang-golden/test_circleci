-- select unpackaged_whole_cannabis_plants_processed from health_canada_report

SELECT unpackaged_vegetative_plants_inventory, unpackaged_whole_cannabis_plants_inventory
FROM f_get_current_inventory('2021-06-30', 1);

------------ VEGETATIVE PRODUCED ------------
-- unpackaged_vegetative_plants_produced
SELECT SUM(COALESCE(t1.plants_quantity, 0)) AS unpackaged_vegetative_plants_produced
FROM (
         SELECT GREATEST(0, COALESCE(CAST(data ->> 'to_qty' AS DECIMAL), 0)) AS plants_quantity
         FROM activities
         WHERE name = 'germinate_seeds'
           AND
--         organization_id = org_id AND
--         TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
             organization_id = 1
           AND TO_CHAR(timestamp, 'YYYY-MM-DD') BETWEEN '2021-06-01' AND '2021-06-30'
     ) AS t1;
------------ VEGETATIVE PRODUCED ------------

------------ VEGETATIVE PROCESSED = WHOLE PRODUCED ------------
-- unpackaged_vegetative_plants_processed
-- unpackaged_whole_cannabis_plants_produced
SELECT SUM(COALESCE(t1.plants_processed, 0)) AS plants_processed
FROM (
         SELECT GREATEST(0, COALESCE(CAST(data ->> 'qty' AS DECIMAL), 0)) AS plants_processed, data->>'inventory_id'
         FROM activities
         WHERE name = 'update_stage'
           AND data ->> 'to_stage' = 'flowering'
           AND organization_id = 1
           AND TO_CHAR(timestamp, 'YYYY-MM-DD') BETWEEN '2021-06-01' AND '2021-06-30'
     ) AS t1;
------------ VEGETATIVE PROCESSED = WHOLE PRODUCED ------------

------------ WHOLE PROCESSED------------
-- unpackaged_whole_cannabis_plants_processed
SELECT SUM(COALESCE(t1.whole_plants_processed, 0)) AS whole_plants_processed
FROM (
         SELECT GREATEST(0, COALESCE(CAST(data ->> 'from_qty' AS DECIMAL), 0)) AS whole_plants_processed, *
         FROM activities
         WHERE name = 'batch_record_harvest_weight'
           AND organization_id = 1
           AND TO_CHAR(timestamp, 'YYYY-MM-DD') BETWEEN :initial_date AND :final_date
     ) AS t1;
------------ WHOLE PROCESSED------------

------------ RECEIVED INVENTORY ------------
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
                END AS type_shipping,
               act.data->>'inventory_id'

        FROM f_inventories_latest_stats_stage('2021-06-30') as inv
            INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
            INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
            INNER JOIN organizations as org on inv.organization_id = org.id
        WHERE type = 'received inventory' AND
            inv.organization_id = 1 and
            TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
    ) AS T1
    GROUP BY T1.type_shipping, (f).package_type
) AS T2;
------------ RECEIVED INVENTORY ------------

----- INVENTORY ACTIVITIES -----

SELECT id, timestamp, name, data FROM f_activities_from_inventory(3728) ORDER BY timestamp, id;
SELECT id, timestamp, name, data FROM f_activities_from_inventory(3722) ORDER BY timestamp, id;


------------ INVENTORY DATE --------------

update inventories
set timestamp = inv.timestamp
from (
    select i.id, a.timestamp
    from activities a
    join inventories i ON (a.data->>'inventory_id')::numeric = i.id
    where a.name = 'create_batch'
    AND TO_CHAR(a.timestamp, 'YYYY-MM-DD') BETWEEN '2021-05-18' AND '2021-05-18'
 ) inv
where inventories.id = inv.id;