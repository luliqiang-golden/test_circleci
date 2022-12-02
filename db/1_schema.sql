--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.23
-- Dumped by pg_dump version 9.6.23

-- Started on 2022-02-18 19:58:12 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 6 (class 2615 OID 16388)
-- Name: sensor_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA sensor_data;


ALTER SCHEMA sensor_data OWNER TO postgres;

--
-- TOC entry 1 (class 3079 OID 12393)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 3657 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- TOC entry 303 (class 1255 OID 20066)
-- Name: f_activities_from_inventory(bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_activities_from_inventory(inv_id bigint) RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, inventory_id bigint)
    LANGUAGE plpgsql
    AS $$
begin
  return QUERY
    select *, 
	CASE 
         WHEN 
		 cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
		 THEN 
         cast(act.data->>'inventory_id' as bigint)
         ELSE 
         inv_id 
      END
    as inventory_id from activities as act 
    where
		(concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
		concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
		concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
		inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
		inv_id = cast(act.data->>'to_inventory_id' as integer) or
		inv_id = cast(act.data->>'inventory_id'as integer) or
		inv_id = cast(act.data->>'related_inventory_id' as integer) or
		inv_id = cast(act.data->>'linked_inventory_id' as integer));

END;
$$;


ALTER FUNCTION public.f_activities_from_inventory(inv_id bigint) OWNER TO postgres;

--
-- TOC entry 297 (class 1255 OID 18998)
-- Name: f_get_current_inventory(character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric) RETURNS record
    LANGUAGE plpgsql
    AS $$
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
								
								
 				--raise notice 'initial date: %', initial_date;
 				--raise notice 'final date: %', final_date;
                            		
                            
                            
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

            END;$$;


ALTER FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric) OWNER TO postgres;

--
-- TOC entry 300 (class 1255 OID 19361)
-- Name: f_hc_report(character varying, character varying, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report(month_period character varying, year_period character varying, org_id integer, create_by_id integer, OUT report_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
            DECLARE	
                var_province VARCHAR; 
                var_type VARCHAR; --Identify whether the report is being submitted by a retailer or a distributor. If both activities are conducted, identify as a distributor. For .csv uploads, input 1 for a retailer or 2 for a distributor.
                var_company_name VARCHAR;
                var_site_id VARCHAR;--issued by the provincial or territorial authority to the distributor or retailer.
                var_city VARCHAR;
                var_postal_code	VARCHAR;
                var_country VARCHAR;
                var_license_id VARCHAR; 
                var_total_buildings_area DECIMAL;
                var_licensed_growing_area DECIMAL;
                var_licensed_processing_area DECIMAL;
                var_licensed_outdoor_growing_area DECIMAL; 
                initial_date VARCHAR;
                final_date VARCHAR;
            BEGIN
                -- get the first day of the month
                SELECT TO_DATE(CONCAT(year_period,'-',month_period,'-01'), 'YYYY-MM-DD') INTO initial_date;
                raise notice 'initial date: %', initial_date;

                -- get the last day of the month
                SELECT TO_CHAR(TO_DATE(initial_date, 'YYYY-MM-DD') 
                                + interval '1 month'
                                - interval '1 day', 'YYYY-MM-DD') into final_date;
                raise notice 'final date: %', final_date;

    

                SELECT org.name,
                    org.data->>'license_id',
                    org.data->'facility_details'->>'total_buildings_area',
                    org.data->'facility_details'->>'licensed_growing_area',
                    org.data->'facility_details'->>'licensed_processing_area',
                    org.data->'facility_details'->>'licensed_outdoor_growing_area',
                    org.data->'facility_details'->'facilityAddress'->>'city',
                    org.data->'facility_details'->'facilityAddress'->>'country',
                    org.data->'facility_details'->'facilityAddress'->>'province',
                    org.data->'facility_details'->'facilityAddress'->>'postalCode',
                    '1' as type,
                    '0' as site_id
                FROM organizations as org 
                WHERE org.id = 1 
                INTO var_company_name, 
                    var_license_id, 
                    var_total_buildings_area,
                    var_licensed_growing_area,
                    var_licensed_processing_area,
                    var_licensed_outdoor_growing_area, 
                    var_city,
                    var_country,
                    var_province,
                    var_postal_code,
                    var_type,
                    var_site_id;             

                -- check if there is the report	
                SELECT hcr.id 
                FROM health_canada_report AS hcr 
                WHERE hcr.organization_id = org_id AND 
                    hcr.report_period_year = year_period AND 
                    hcr.report_period_month = month_period  
                INTO report_id;

                IF report_id IS NULL THEN
                    INSERT INTO health_canada_report (timestamp, created_by, organization_id, report_period_year, report_period_month, province, type, site_id, city, postal_code, company_name, license_id, total_buildings_area, licensed_growing_area, licensed_processing_area, licensed_outdoor_growing_area)
                    VALUES (CURRENT_DATE, create_by_id, org_id, year_period, month_period, var_province, var_type, var_site_id, var_city, var_postal_code, var_company_name, var_license_id, var_total_buildings_area, var_licensed_growing_area, var_licensed_processing_area, var_licensed_outdoor_growing_area)
                    RETURNING id INTO report_id;	
                else
                
                
                	UPDATE health_canada_report set timestamp = CURRENT_DATE, 
                									created_by = create_by_id, 
                									organization_id = org_id, 
                									"province"= var_province, 
                									"type" = var_type, 
                									site_id = var_site_id, 
                									city = var_city, 
                									postal_code = var_postal_code, 
                									company_name = var_company_name, 
                									license_id = var_license_id, 
                									total_buildings_area = var_total_buildings_area, 
                									licensed_growing_area = var_licensed_growing_area, 
                									licensed_processing_area = var_licensed_processing_area, 
                									licensed_outdoor_growing_area = var_licensed_outdoor_growing_area
                    where id = report_id;
                
                end if;
                raise notice 'report id: %', report_id;

                --FUNCTIONS
                PERFORM f_hc_report_inventory(report_id, initial_date, final_date, org_id);
                PERFORM f_hc_report_sales(report_id, initial_date, final_date, org_id);

        END;$$;


ALTER FUNCTION public.f_hc_report(month_period character varying, year_period character varying, org_id integer, create_by_id integer, OUT report_id integer) OWNER TO postgres;

--
-- TOC entry 292 (class 1255 OID 18986)
-- Name: f_hc_report_closing_inventory(integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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

            END;$$;


ALTER FUNCTION public.f_hc_report_closing_inventory(report_id integer, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 305 (class 1255 OID 19891)
-- Name: f_hc_report_inventory(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN		
            --opening inventory
            PERFORM f_hc_report_opening_inventory(report_id, initial_date, org_id);	
            
            -- processed and produced
            PERFORM f_hc_report_inventory_produced_processed(report_id, initial_date, final_date, org_id);
            
            -- received inventory
            PERFORM f_hc_report_received_inventory(report_id, initial_date, final_date, org_id);
                
            -- packaged and labels (lot items)
            PERFORM f_hc_report_inventory_packaged_label(report_id, initial_date, final_date, org_id);
            
            -- samples sent to lab
            PERFORM f_hc_report_inventory_shipped_testers(report_id, initial_date, final_date, org_id);

            -- cultivator and processor
            PERFORM f_hc_report_inventory_cultivators_processors(report_id, initial_date, final_date, org_id);
                
            -- adjustment and loss
            PERFORM f_hc_report_inventory_adjustment_loss(report_id, initial_date, final_date, org_id);

            --destruction
            PERFORM f_hc_report_inventory_destroyed(report_id, initial_date, final_date, org_id);
            
            -- packaged shipped domestic
            PERFORM f_hc_report_inventory_shipped_domestic(report_id, initial_date, final_date, org_id);	
            
            --closing inventory
            PERFORM f_hc_report_closing_inventory(report_id, final_date, org_id);

            --return items
            PERFORM f_hc_report_return_received_inventory(report_id, initial_date, final_date, org_id);
            
        END;
        $$;


ALTER FUNCTION public.f_hc_report_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 301 (class 1255 OID 18992)
-- Name: f_hc_report_inventory_adjustment_loss(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
                
            END;$$;


ALTER FUNCTION public.f_hc_report_inventory_adjustment_loss(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 302 (class 1255 OID 20053)
-- Name: f_hc_report_inventory_cultivators_processors(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
                unpackaged_extracts_shipped_cultivators_processors = COALESCE(T2.unpackaged_extracts_shipped_cultivators_processors,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_shipped_cultivators_processors,		
                    0 AS unpackaged_vegetative_plants_shipped_cultivators_processors,
					0 AS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'g-wet') AS unpackaged_fresh_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_shipped_cultivators_processors
                  
                
                FROM (
                    
                
                	SELECT  CAST(act.data->>'from_qty' AS DECIMAL) AS to_qty, act.data->>'from_qty_unit' AS unit
                    FROM activities AS act
                    WHERE act.name ='send_processor' AND
                        --act.organization_id = 1 and
                        --TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-02-01'  AND '2021-02-28'
                        act.organization_id = org_id AND
                        TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
           
           
           
           /* 
	             received from cultivators and process
	            
            */
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_received_returned = COALESCE(T2.unpackaged_seed_received_returned,0),
                unpackaged_vegetative_plants_received_returned = COALESCE(T2.unpackaged_vegetative_plants_received_returned,0),
                unpackaged_whole_cannabis_plants_received_returned = COALESCE(T2.unpackaged_whole_cannabis_plants_received_returned,0),
                unpackaged_fresh_cannabis_received_returned = COALESCE(T2.unpackaged_fresh_cannabis_received_returned,0)/1000,
                unpackaged_dried_cannabis_received_returned = COALESCE(T2.unpackaged_dried_cannabis_received_returned,0)/1000,
                unpackaged_extracts_received_returned = COALESCE(T2.unpackaged_extracts_received_returned,0)/1000
                
            FROM (
                SELECT 
                     -- unpackaged sent to processor
                    0 AS unpackaged_seed_received_returned,		
                    0 AS unpackaged_vegetative_plants_received_returned,
					0 AS unpackaged_whole_cannabis_plants_received_returned,
                    0 AS unpackaged_fresh_cannabis_received_returned, -- we will never receive from a processor wet
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_received_returned,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_received_returned
                  
                
                FROM (
                    
                
                	SELECT  act.*, CAST(act.data->>'to_qty' AS DECIMAL) AS to_qty, act.data->>'to_qty_unit' AS unit
                    FROM activities AS act
                    WHERE act.name ='receive_processor' AND
                        --act.organization_id = 1 and
                        --TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-02-01'  AND '2021-02-28'
                        act.organization_id = org_id AND
                        TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        
                        
                        
                        
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
            
        END;$$;


ALTER FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 306 (class 1255 OID 18987)
-- Name: f_hc_report_inventory_destroyed(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_destroyed(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
                            WHEN LOWER(T0.from_unit) = 'plants' AND ((T0.last_stage_before_activity in ('planning', 'propagation', 'germinating', 'vegetation') OR T0.type in ('received inventory', 'mother', 'mother batch', 'lot'))) OR ((T0.end_type = 'plants') AND (T0.last_stage_before_activity != 'germinating'))
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
                
            END;
        $$;


ALTER FUNCTION public.f_hc_report_inventory_destroyed(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 293 (class 1255 OID 18988)
-- Name: f_hc_report_inventory_packaged_label(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN		
            -- packaged and labels (lot items) - should we rely on f_inventories_latest_stats_stage()?
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_packaged_label = COALESCE(T2.unpackaged_seed_packaged_label,0),
                unpackaged_vegetative_plants_packaged_label = COALESCE(T2.unpackaged_vegetative_plants_packaged_label,0),
                unpackaged_whole_cannabis_plants_packaged_label = COALESCE(T2.unpackaged_whole_cannabis_plants_packaged_label,0),
                unpackaged_fresh_cannabis_packaged_label = COALESCE(T2.unpackaged_fresh_cannabis_packaged_label,0)/1000,
                unpackaged_dried_cannabis_packaged_label = COALESCE(T2.unpackaged_dried_cannabis_packaged_label,0)/1000,
                unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0)
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
                        --act.organization_id = 1 and
                        --TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-04-01'  AND '2020-04-30'
                        act.organization_id = org_id AND
                        TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                ) AS T1
            ) AS T2
            WHERE id = report_id;
            
            
        END;$$;


ALTER FUNCTION public.f_hc_report_inventory_packaged_label(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 304 (class 1255 OID 18989)
-- Name: f_hc_report_inventory_produced_processed(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
        BEGIN		
            --unpackaged seed processed and unpacked vegetative plants produced
            UPDATE health_canada_report
            SET 
                unpackaged_seed_produced = 0,
                unpackaged_seed_processed = COALESCE(T2.unpackaged_seed_processed,0)/1000,
                unpackaged_vegetative_plants_produced = COALESCE(T2.unpackaged_vegetative_plants_produced,0)
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
                        organization_id = org_id AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                    UNION ALL
                    SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                    FROM activities
                    WHERE name = 'propagate_cuttings' AND
                        organization_id = org_id AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                ) AS T1
            ) AS T2
            WHERE id = report_id;	
            
                    
            -- unpacakged vegetative plants processed and  whole plant produced
            UPDATE health_canada_report
            SET 
                unpackaged_vegetative_plants_processed = COALESCE(T2.plants_processed,0),
                unpackaged_whole_cannabis_plants_produced = COALESCE(T2.plants_processed,0)	
            FROM (
                SELECT 
                    SUM(COALESCE(T1.plants_processed,0)) AS plants_processed			
                FROM (
                    SELECT
                        GREATEST(0,COALESCE(CAST(data->>'qty' AS DECIMAL),0)) AS plants_processed
                    FROM activities 			
                    WHERE name = 'update_stage' AND 
                        data->>'to_stage' = 'flowering' AND
                        organization_id = org_id AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
--                         organization_id = 1 and
--                         TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2021-08-01'  AND '2021-08-31'
                ) AS T1
            ) AS T2
            WHERE id = report_id;	
                    
                    
            -- unpacakged fresh cannabis produced and whole plants processed
            UPDATE health_canada_report
            SET
                unpackaged_fresh_cannabis_produced = COALESCE(T2.fresh_cannabis_produced,0)/1000,
                unpackaged_whole_cannabis_plants_processed = COALESCE(T2.whole_plants_processed,0)
            FROM (
                SELECT
                    SUM(COALESCE(T1.fresh_cannabis_produced,0)) AS fresh_cannabis_produced,
                    SUM(COALESCE(T1.whole_plants_processed,0)) AS whole_plants_processed
                FROM (
                    SELECT
                        GREATEST(0,COALESCE(CAST(data->>'to_qty' AS DECIMAL),0)) AS fresh_cannabis_produced,
                        GREATEST(0,COALESCE(CAST(data->>'from_qty' AS DECIMAL),0)) AS whole_plants_processed

                    FROM activities
                    WHERE name = 'batch_record_bud_harvest_weight' AND
                        organization_id = org_id AND
                        TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        --organization_id = 1 and
                        --TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                ) AS T1
            ) AS T2
            WHERE id = report_id;
                    
            
            -- unpacakged dried cannabis produced, unpacakged extracts produced
            UPDATE health_canada_report
            SET
                unpackaged_dried_cannabis_produced = COALESCE(T2.dried_qty,0)/1000,
                unpackaged_extracts_produced = COALESCE(T2.oil_qty,0)/1000
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
                            MIN(act_adj.id) AS id
                            FROM activities AS act_adj
                            WHERE
                             act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                            AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= final_date
                            --AND TO_CHAR(act_adj.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                            GROUP BY act_adj.data->>'from_inventory_id'
                        ) AS T0 ON T0.inventory_id = inv.id
                        INNER JOIN activities AS act ON act.id = t0.id
                             WHERE
                             act.organization_id = org_id AND
                             TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                             --act.organization_id = 1 AND
                             --TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                    ) AS t1
                ) AS T2
            WHERE id = report_id; 
            
            
             -- dried processed
            UPDATE health_canada_report
            SET
                unpackaged_dried_cannabis_processed = COALESCE(T2.dried_cannabis_processed,0)/1000
            FROM (
                SELECT SUM(t1.dried_cannabis_used) AS dried_cannabis_processed from (
                SELECT CAST (data->>'to_qty' AS numeric) as dried_cannabis_used 
                    FROM activities 
                    WHERE name IN ('batch_record_crude_oil_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    --AND organization_id = 1 
                    --AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-12-01'  AND '2020-12-30'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date                 
                    
                    ) as t1
            ) AS T2
            WHERE id = report_id;
            
             -- unpacakged fresh cannabis processed (amount of fresh cannabis processed = fresh cannabis used for drying & extraction process + loss incurred during those processes i.e., to_qty in batch_record_dry_weight and batch_record_crude_oil_weight + (from_qty - to_qty) in the same activities)
            UPDATE health_canada_report
            SET
                unpackaged_fresh_cannabis_processed = COALESCE(T2.fresh_cannabis_processed,0)/1000
            FROM (
                SELECT SUM(t1.fresh_cannabis_used) AS fresh_cannabis_processed from (
                SELECT CAST (data->>'to_qty' AS numeric) as fresh_cannabis_used 
                    FROM activities 
                    WHERE name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight')
                    AND data->>'from_qty_unit' = 'g-wet' 
                    --AND organization_id = 1 
                    --AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                    AND organization_id = org_id 
                    AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date                 
                    
                    ) as t1
            ) AS T2
            WHERE id = report_id;
        END;
        $$;


ALTER FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 288 (class 1255 OID 18990)
-- Name: f_hc_report_inventory_shipped_domestic(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_shipped_domestic(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
            BEGIN		
                -- packaged shipped domestic
                UPDATE health_canada_report
                SET 
                    packaged_seed_shipped_domestic = 0, -- we don't sell seeds
                    packaged_vegetative_plants_shipped_domestic = COALESCE(T2.packaged_vegetative_plants_shipped_domestic ,0),
                    packaged_fresh_cannabis_shipped_domestic = COALESCE(T2.packaged_fresh_cannabis_shipped_domestic ,0),
                    packaged_dried_cannabis_shipped_domestic = COALESCE(T2.packaged_dried_cannabis_shipped_domestic ,0),
                    packaged_extracts_shipped_domestic = COALESCE(T2.packaged_extracts_shipped_domestic ,0)
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
                            INNER JOIN f_inventories_latest_stats_stage(final_date) AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                            --INNER JOIN f_inventories_latest_stats_stage('2020-05-31') AS inv ON act_map.data->>'inventory_id' = CAST(inv.id AS varchar)
                        WHERE act.name = 'shipment_shipped' AND
                            --inv.organization_id = 1 AND
                            --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                            inv.organization_id = org_id AND
                            TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                    ) AS T1   
                ) AS T2
                WHERE id = report_id;	
                
            END;$$;


ALTER FUNCTION public.f_hc_report_inventory_shipped_domestic(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 295 (class 1255 OID 18994)
-- Name: f_hc_report_inventory_shipped_testers(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
                            
                        END;$$;


ALTER FUNCTION public.f_hc_report_inventory_shipped_testers(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 287 (class 1255 OID 18991)
-- Name: f_hc_report_opening_inventory(integer, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
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

            END;$$;


ALTER FUNCTION public.f_hc_report_opening_inventory(report_id integer, initial_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 291 (class 1255 OID 18993)
-- Name: f_hc_report_received_inventory(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000, 		
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0)	
                    
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
                                    
                            --FROM f_inventories_latest_stats_stage('2020-05-31') as inv
                            FROM f_inventories_latest_stats_stage(final_date)  as inv
                                INNER JOIN activities AS act ON act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)
                                INNER JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                            WHERE type = 'received inventory' AND 
                                --inv.organization_id = 1 and
                                --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2020-05-01'  AND '2020-05-31'
                                inv.organization_id = org_id AND
                                TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
                WHERE id = report_id;	
                            
            END;$$;


ALTER FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 296 (class 1255 OID 19890)
-- Name: f_hc_report_return_received_inventory(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_return_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
             BEGIN		
                --return items
                UPDATE health_canada_report
                SET 
                    --unpackaged return items
                    unpackaged_seed_reductions_shipped_returned = COALESCE(T2.unpackaged_seed_reductions_shipped_returned ,0)/1000,
                    unpackaged_vegetative_plants_reductions_shipped_returned = COALESCE(T2.unpackaged_vegetative_plants_reductions_shipped_returned,0),
                    unpackaged_fresh_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_fresh_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_dried_cannabis_reductions_shipped_returned = COALESCE(T2.unpackaged_dried_cannabis_reductions_shipped_returned ,0)/1000,
                    unpackaged_extracts_reductions_shipped_returned = COALESCE(T2.unpackaged_extracts_reductions_shipped_returned ,0)/1000
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
	 					organization_id = org_id AND
	                     TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
	--						organization_id = 1 AND
	--						TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2019-07-31' AND '2020-07-31'
                ) AS T1
				) AS T2
                WHERE id = report_id;	

            END;$$;


ALTER FUNCTION public.f_hc_report_return_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 290 (class 1255 OID 19695)
-- Name: f_hc_report_sales(integer, character varying, character varying, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_hc_report_sales(report_id integer, initial_date character varying, final_date character varying, org_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
                                BEGIN		
                                    

                        UPDATE health_canada_report
                        SET
                            -- distributor seeds
                            ab_distributor_seeds_amount = COALESCE(seeds_ab_nomedical_distributor,0),
                            bc_distributor_seeds_amount = COALESCE(seeds_bc_nomedical_distributor,0),
                            mb_distributor_seeds_amount = COALESCE(seeds_mb_nomedical_distributor,0),
                            nb_distributor_seeds_amount = COALESCE(seeds_nb_nomedical_distributor,0), 
                            nl_distributor_seeds_amount = COALESCE(seeds_nl_nomedical_distributor,0), 
                            ns_distributor_seeds_amount = COALESCE(seeds_ns_nomedical_distributor,0),
                            nt_distributor_seeds_amount = COALESCE(seeds_nt_nomedical_distributor,0),
                            nu_distributor_seeds_amount = COALESCE(seeds_nu_nomedical_distributor,0),
                            on_distributor_seeds_amount = COALESCE(seeds_on_nomedical_distributor,0),
                            pe_distributor_seeds_amount = COALESCE(seeds_pe_nomedical_distributor,0),
                            qc_distributor_seeds_amount = COALESCE(seeds_qc_nomedical_distributor,0), 
                            sk_distributor_seeds_amount = COALESCE(seeds_sk_nomedical_distributor,0), 
                            yt_distributor_seeds_amount = COALESCE(seeds_yt_nomedical_distributor,0), 
                            total_distributor_seeds_amount = COALESCE(seeds_total_nomedical_distributor,0),

                            ab_distributor_seeds_value = COALESCE(seeds_ab_nomedical_distributor_value,0),
                            bc_distributor_seeds_value = COALESCE(seeds_bc_nomedical_distributor_value,0),
                            mb_distributor_seeds_value = COALESCE(seeds_mb_nomedical_distributor_value,0),
                            nb_distributor_seeds_value = COALESCE(seeds_nb_nomedical_distributor_value,0), 
                            nl_distributor_seeds_value = COALESCE(seeds_nl_nomedical_distributor_value,0), 
                            ns_distributor_seeds_value = COALESCE(seeds_ns_nomedical_distributor_value,0),
                            nt_distributor_seeds_value = COALESCE(seeds_nt_nomedical_distributor_value,0),
                            nu_distributor_seeds_value = COALESCE(seeds_nu_nomedical_distributor_value,0),
                            on_distributor_seeds_value = COALESCE(seeds_on_nomedical_distributor_value,0),
                            pe_distributor_seeds_value = COALESCE(seeds_pe_nomedical_distributor_value,0),
                            qc_distributor_seeds_value = COALESCE(seeds_qc_nomedical_distributor_value,0), 
                            sk_distributor_seeds_value = COALESCE(seeds_sk_nomedical_distributor_value,0), 
                            yt_distributor_seeds_value = COALESCE(seeds_yt_nomedical_distributor_value,0), 
                            total_distributor_seeds_value = COALESCE(seeds_total_nomedical_distributor_value,0),
                            
                            
                            -- recreational consumer seeds
                            ab_recreational_consumer_seeds_amount = COALESCE(seeds_ab_nomedical_recreational_consumer,0),
                            bc_recreational_consumer_seeds_amount = COALESCE(seeds_bc_nomedical_recreational_consumer,0),
                            mb_recreational_consumer_seeds_amount = COALESCE(seeds_mb_nomedical_recreational_consumer,0),
                            nb_recreational_consumer_seeds_amount = COALESCE(seeds_nb_nomedical_recreational_consumer,0), 
                            nl_recreational_consumer_seeds_amount = COALESCE(seeds_nl_nomedical_recreational_consumer,0), 
                            ns_recreational_consumer_seeds_amount = COALESCE(seeds_ns_nomedical_recreational_consumer,0),
                            nt_recreational_consumer_seeds_amount = COALESCE(seeds_nt_nomedical_recreational_consumer,0),
                            nu_recreational_consumer_seeds_amount = COALESCE(seeds_nu_nomedical_recreational_consumer,0),
                            on_recreational_consumer_seeds_amount = COALESCE(seeds_on_nomedical_recreational_consumer,0),
                            pe_recreational_consumer_seeds_amount = COALESCE(seeds_pe_nomedical_recreational_consumer,0),
                            qc_recreational_consumer_seeds_amount = COALESCE(seeds_qc_nomedical_recreational_consumer,0), 
                            sk_recreational_consumer_seeds_amount = COALESCE(seeds_sk_nomedical_recreational_consumer,0), 
                            yt_recreational_consumer_seeds_amount = COALESCE(seeds_yt_nomedical_recreational_consumer,0), 
                            total_recreational_consumer_seeds_amount = COALESCE(seeds_total_nomedical_recreational_consumer,0),
                            
                            
                            ab_recreational_consumer_seeds_value = COALESCE(seeds_ab_nomedical_recreational_consumer_value,0),
                            bc_recreational_consumer_seeds_value = COALESCE(seeds_bc_nomedical_recreational_consumer_value,0),
                            mb_recreational_consumer_seeds_value = COALESCE(seeds_mb_nomedical_recreational_consumer_value,0),
                            nb_recreational_consumer_seeds_value = COALESCE(seeds_nb_nomedical_recreational_consumer_value,0), 
                            nl_recreational_consumer_seeds_value = COALESCE(seeds_nl_nomedical_recreational_consumer_value,0), 
                            ns_recreational_consumer_seeds_value = COALESCE(seeds_ns_nomedical_recreational_consumer_value,0),
                            nt_recreational_consumer_seeds_value = COALESCE(seeds_nt_nomedical_recreational_consumer_value,0),
                            nu_recreational_consumer_seeds_value = COALESCE(seeds_nu_nomedical_recreational_consumer_value,0),
                            on_recreational_consumer_seeds_value = COALESCE(seeds_on_nomedical_recreational_consumer_value,0),
                            pe_recreational_consumer_seeds_value = COALESCE(seeds_pe_nomedical_recreational_consumer_value,0),
                            qc_recreational_consumer_seeds_value = COALESCE(seeds_qc_nomedical_recreational_consumer_value,0), 
                            sk_recreational_consumer_seeds_value = COALESCE(seeds_sk_nomedical_recreational_consumer_value,0), 
                            yt_recreational_consumer_seeds_value = COALESCE(seeds_yt_nomedical_recreational_consumer_value,0), 
                            total_recreational_consumer_seeds_value = COALESCE(seeds_total_nomedical_recreational_consumer_value,0),

                            -- retailer seeds
                            ab_retailer_seeds_amount = COALESCE(seeds_ab_nomedical_retailer,0),
                            bc_retailer_seeds_amount = COALESCE(seeds_bc_nomedical_retailer,0),
                            mb_retailer_seeds_amount = COALESCE(seeds_mb_nomedical_retailer,0),
                            nb_retailer_seeds_amount = COALESCE(seeds_nb_nomedical_retailer,0), 
                            nl_retailer_seeds_amount = COALESCE(seeds_nl_nomedical_retailer,0), 
                            ns_retailer_seeds_amount = COALESCE(seeds_ns_nomedical_retailer,0),
                            nt_retailer_seeds_amount = COALESCE(seeds_nt_nomedical_retailer,0),
                            nu_retailer_seeds_amount = COALESCE(seeds_nu_nomedical_retailer,0),
                            on_retailer_seeds_amount = COALESCE(seeds_on_nomedical_retailer,0),
                            pe_retailer_seeds_amount = COALESCE(seeds_pe_nomedical_retailer,0),
                            qc_retailer_seeds_amount = COALESCE(seeds_qc_nomedical_retailer,0), 
                            sk_retailer_seeds_amount = COALESCE(seeds_sk_nomedical_retailer,0), 
                            yt_retailer_seeds_amount = COALESCE(seeds_yt_nomedical_retailer,0), 
                            total_retailer_seeds_amount = COALESCE(seeds_total_nomedical_retailer,0),
                            
                            ab_retailer_seeds_value = COALESCE(seeds_ab_nomedical_retailer_value,0),
                            bc_retailer_seeds_value = COALESCE(seeds_bc_nomedical_retailer_value,0),
                            mb_retailer_seeds_value = COALESCE(seeds_mb_nomedical_retailer_value,0),
                            nb_retailer_seeds_value = COALESCE(seeds_nb_nomedical_retailer_value,0), 
                            nl_retailer_seeds_value = COALESCE(seeds_nl_nomedical_retailer_value,0), 
                            ns_retailer_seeds_value = COALESCE(seeds_ns_nomedical_retailer_value,0),
                            nt_retailer_seeds_value = COALESCE(seeds_nt_nomedical_retailer_value,0),
                            nu_retailer_seeds_value = COALESCE(seeds_nu_nomedical_retailer_value,0),
                            on_retailer_seeds_value = COALESCE(seeds_on_nomedical_retailer_value,0),
                            pe_retailer_seeds_value = COALESCE(seeds_pe_nomedical_retailer_value,0),
                            qc_retailer_seeds_value = COALESCE(seeds_qc_nomedical_retailer_value,0), 
                            sk_retailer_seeds_value = COALESCE(seeds_sk_nomedical_retailer_value,0), 
                            yt_retailer_seeds_value = COALESCE(seeds_yt_nomedical_retailer_value,0), 
                            total_retailer_seeds_value = COALESCE(seeds_total_nomedical_retailer_value,0),

                            -- distributor plants
                            ab_distributor_veg_plants_amount = COALESCE(plants_ab_nomedical_distributor,0),
                            bc_distributor_veg_plants_amount = COALESCE(plants_bc_nomedical_distributor,0),
                            mb_distributor_veg_plants_amount = COALESCE(plants_mb_nomedical_distributor,0),
                            nb_distributor_veg_plants_amount = COALESCE(plants_nb_nomedical_distributor,0), 
                            nl_distributor_veg_plants_amount = COALESCE(plants_nl_nomedical_distributor,0), 
                            ns_distributor_veg_plants_amount = COALESCE(plants_ns_nomedical_distributor,0),
                            nt_distributor_veg_plants_amount = COALESCE(plants_nt_nomedical_distributor,0),
                            nu_distributor_veg_plants_amount = COALESCE(plants_nu_nomedical_distributor,0),
                            on_distributor_veg_plants_amount = COALESCE(plants_on_nomedical_distributor,0),
                            pe_distributor_veg_plants_amount = COALESCE(plants_pe_nomedical_distributor,0),
                            qc_distributor_veg_plants_amount = COALESCE(plants_qc_nomedical_distributor,0), 
                            sk_distributor_veg_plants_amount = COALESCE(plants_sk_nomedical_distributor,0), 
                            yt_distributor_veg_plants_amount = COALESCE(plants_yt_nomedical_distributor,0), 
                            total_distributor_veg_plants_amount = COALESCE(plants_total_nomedical_distributor,0),
                            
                            ab_distributor_veg_plants_value = COALESCE(plants_ab_nomedical_distributor_value,0),
                            bc_distributor_veg_plants_value = COALESCE(plants_bc_nomedical_distributor_value,0),
                            mb_distributor_veg_plants_value = COALESCE(plants_mb_nomedical_distributor_value,0),
                            nb_distributor_veg_plants_value = COALESCE(plants_nb_nomedical_distributor_value,0), 
                            nl_distributor_veg_plants_value = COALESCE(plants_nl_nomedical_distributor_value,0), 
                            ns_distributor_veg_plants_value = COALESCE(plants_ns_nomedical_distributor_value,0),
                            nt_distributor_veg_plants_value = COALESCE(plants_nt_nomedical_distributor_value,0),
                            nu_distributor_veg_plants_value = COALESCE(plants_nu_nomedical_distributor_value,0),
                            on_distributor_veg_plants_value = COALESCE(plants_on_nomedical_distributor_value,0),
                            pe_distributor_veg_plants_value = COALESCE(plants_pe_nomedical_distributor_value,0),
                            qc_distributor_veg_plants_value = COALESCE(plants_qc_nomedical_distributor_value,0), 
                            sk_distributor_veg_plants_value = COALESCE(plants_sk_nomedical_distributor_value,0), 
                            yt_distributor_veg_plants_value = COALESCE(plants_yt_nomedical_distributor_value,0), 
                            total_distributor_veg_plants_value = COALESCE(plants_total_nomedical_distributor_value,0),

                            -- recreational consumer plants
                            ab_recreational_consumer_veg_plants_amount = COALESCE(plants_ab_nomedical_recreational_consumer,0),
                            bc_recreational_consumer_veg_plants_amount = COALESCE(plants_bc_nomedical_recreational_consumer,0),
                            mb_recreational_consumer_veg_plants_amount = COALESCE(plants_mb_nomedical_recreational_consumer,0),
                            nb_recreational_consumer_veg_plants_amount = COALESCE(plants_nb_nomedical_recreational_consumer,0), 
                            nl_recreational_consumer_veg_plants_amount = COALESCE(plants_nl_nomedical_recreational_consumer,0), 
                            ns_recreational_consumer_veg_plants_amount = COALESCE(plants_ns_nomedical_recreational_consumer,0),
                            nt_recreational_consumer_veg_plants_amount = COALESCE(plants_nt_nomedical_recreational_consumer,0),
                            nu_recreational_consumer_veg_plants_amount = COALESCE(plants_nu_nomedical_recreational_consumer,0),
                            on_recreational_consumer_veg_plants_amount = COALESCE(plants_on_nomedical_recreational_consumer,0),
                            pe_recreational_consumer_veg_plants_amount = COALESCE(plants_pe_nomedical_recreational_consumer,0),
                            qc_recreational_consumer_veg_plants_amount = COALESCE(plants_qc_nomedical_recreational_consumer,0), 
                            sk_recreational_consumer_veg_plants_amount = COALESCE(plants_sk_nomedical_recreational_consumer,0), 
                            yt_recreational_consumer_veg_plants_amount = COALESCE(plants_yt_nomedical_recreational_consumer,0), 
                            total_recreational_consumer_veg_plants_amount = COALESCE(plants_total_nomedical_recreational_consumer,0),
                            
                            ab_recreational_consumer_veg_plants_value = COALESCE(plants_ab_nomedical_recreational_consumer_value,0),
                            bc_recreational_consumer_veg_plants_value = COALESCE(plants_bc_nomedical_recreational_consumer_value,0),
                            mb_recreational_consumer_veg_plants_value = COALESCE(plants_mb_nomedical_recreational_consumer_value,0),
                            nb_recreational_consumer_veg_plants_value = COALESCE(plants_nb_nomedical_recreational_consumer_value,0), 
                            nl_recreational_consumer_veg_plants_value = COALESCE(plants_nl_nomedical_recreational_consumer_value,0), 
                            ns_recreational_consumer_veg_plants_value = COALESCE(plants_ns_nomedical_recreational_consumer_value,0),
                            nt_recreational_consumer_veg_plants_value = COALESCE(plants_nt_nomedical_recreational_consumer_value,0),
                            nu_recreational_consumer_veg_plants_value = COALESCE(plants_nu_nomedical_recreational_consumer_value,0),
                            on_recreational_consumer_veg_plants_value = COALESCE(plants_on_nomedical_recreational_consumer_value,0),
                            pe_recreational_consumer_veg_plants_value = COALESCE(plants_pe_nomedical_recreational_consumer_value,0),
                            qc_recreational_consumer_veg_plants_value = COALESCE(plants_qc_nomedical_recreational_consumer_value,0), 
                            sk_recreational_consumer_veg_plants_value = COALESCE(plants_sk_nomedical_recreational_consumer_value,0), 
                            yt_recreational_consumer_veg_plants_value = COALESCE(plants_yt_nomedical_recreational_consumer_value,0), 
                            total_recreational_consumer_veg_plants_value = COALESCE(plants_total_nomedical_recreational_consumer_value,0),

                            -- retailer plants
                            ab_retailer_veg_plants_amount = COALESCE(plants_ab_nomedical_retailer,0),
                            bc_retailer_veg_plants_amount = COALESCE(plants_bc_nomedical_retailer,0),
                            mb_retailer_veg_plants_amount = COALESCE(plants_mb_nomedical_retailer,0),
                            nb_retailer_veg_plants_amount = COALESCE(plants_nb_nomedical_retailer,0), 
                            nl_retailer_veg_plants_amount = COALESCE(plants_nl_nomedical_retailer,0), 
                            ns_retailer_veg_plants_amount = COALESCE(plants_ns_nomedical_retailer,0),
                            nt_retailer_veg_plants_amount = COALESCE(plants_nt_nomedical_retailer,0),
                            nu_retailer_veg_plants_amount = COALESCE(plants_nu_nomedical_retailer,0),
                            on_retailer_veg_plants_amount = COALESCE(plants_on_nomedical_retailer,0),
                            pe_retailer_veg_plants_amount = COALESCE(plants_pe_nomedical_retailer,0),
                            qc_retailer_veg_plants_amount = COALESCE(plants_qc_nomedical_retailer,0), 
                            sk_retailer_veg_plants_amount = COALESCE(plants_sk_nomedical_retailer,0), 
                            yt_retailer_veg_plants_amount = COALESCE(plants_yt_nomedical_retailer,0), 
                            total_retailer_veg_plants_amount = COALESCE(plants_total_nomedical_retailer,0),
                            
                            ab_retailer_veg_plants_value = COALESCE(plants_ab_nomedical_retailer_value,0),
                            bc_retailer_veg_plants_value = COALESCE(plants_bc_nomedical_retailer_value,0),
                            mb_retailer_veg_plants_value = COALESCE(plants_mb_nomedical_retailer_value,0),
                            nb_retailer_veg_plants_value = COALESCE(plants_nb_nomedical_retailer_value,0), 
                            nl_retailer_veg_plants_value = COALESCE(plants_nl_nomedical_retailer_value,0), 
                            ns_retailer_veg_plants_value = COALESCE(plants_ns_nomedical_retailer_value,0),
                            nt_retailer_veg_plants_value = COALESCE(plants_nt_nomedical_retailer_value,0),
                            nu_retailer_veg_plants_value = COALESCE(plants_nu_nomedical_retailer_value,0),
                            on_retailer_veg_plants_value = COALESCE(plants_on_nomedical_retailer_value,0),
                            pe_retailer_veg_plants_value = COALESCE(plants_pe_nomedical_retailer_value,0),
                            qc_retailer_veg_plants_value = COALESCE(plants_qc_nomedical_retailer_value,0), 
                            sk_retailer_veg_plants_value = COALESCE(plants_sk_nomedical_retailer_value,0), 
                            yt_retailer_veg_plants_value = COALESCE(plants_yt_nomedical_retailer_value,0), 
                            total_retailer_veg_plants_value = COALESCE(plants_total_nomedical_retailer_value,0),

                            -- intra industry plants
                            ab_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_ab_nomedical_intra_industry_unpackaged,0),
                            bc_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_bc_nomedical_intra_industry_unpackaged,0),
                            mb_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_mb_nomedical_intra_industry_unpackaged,0),
                            nb_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_nb_nomedical_intra_industry_unpackaged,0), 
                            nl_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_nl_nomedical_intra_industry_unpackaged,0), 
                            ns_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_ns_nomedical_intra_industry_unpackaged,0),
                            nt_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_nt_nomedical_intra_industry_unpackaged,0),
                            nu_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_nu_nomedical_intra_industry_unpackaged,0),
                            on_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_on_nomedical_intra_industry_unpackaged,0),
                            pe_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_pe_nomedical_intra_industry_unpackaged,0),
                            qc_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_qc_nomedical_intra_industry_unpackaged,0), 
                            sk_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_sk_nomedical_intra_industry_unpackaged,0),
                            yt_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_yt_nomedical_intra_industry_unpackaged,0), 
                            total_unpackaged_intra_industry_veg_plants_amount = COALESCE(plants_total_nomedical_intra_industry_unpackaged,0),
                            
                            ab_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_ab_nomedical_intra_industry_unpackaged_value,0),
                            mb_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_mb_nomedical_intra_industry_unpackaged_value,0),
                            bc_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_bc_nomedical_intra_industry_unpackaged_value,0),
                            nb_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_nb_nomedical_intra_industry_unpackaged_value,0), 
                            nl_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_nl_nomedical_intra_industry_unpackaged_value,0), 
                            ns_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_ns_nomedical_intra_industry_unpackaged_value,0),
                            nt_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_nt_nomedical_intra_industry_unpackaged_value,0),
                            nu_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_nu_nomedical_intra_industry_unpackaged_value,0),
                            on_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_on_nomedical_intra_industry_unpackaged_value,0),
                            pe_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_pe_nomedical_intra_industry_unpackaged_value,0),
                            qc_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_qc_nomedical_intra_industry_unpackaged_value,0), 
                            sk_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_sk_nomedical_intra_industry_unpackaged_value,0),
                            yt_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_yt_nomedical_intra_industry_unpackaged_value,0), 
                            total_unpackaged_intra_industry_veg_plants_value = COALESCE(plants_total_nomedical_intra_industry_unpackaged_value,0),

                            ab_packaged_intra_industry_veg_plants_amount = COALESCE(plants_ab_nomedical_intra_industry_packaged,0),
                            bc_packaged_intra_industry_veg_plants_amount = COALESCE(plants_bc_nomedical_intra_industry_packaged,0),
                            mb_packaged_intra_industry_veg_plants_amount = COALESCE(plants_mb_nomedical_intra_industry_packaged,0),
                            nb_packaged_intra_industry_veg_plants_amount = COALESCE(plants_nb_nomedical_intra_industry_packaged,0), 
                            nl_packaged_intra_industry_veg_plants_amount = COALESCE(plants_nl_nomedical_intra_industry_packaged,0), 
                            ns_packaged_intra_industry_veg_plants_amount = COALESCE(plants_ns_nomedical_intra_industry_packaged,0),
                            nt_packaged_intra_industry_veg_plants_amount = COALESCE(plants_nt_nomedical_intra_industry_packaged,0),
                            nu_packaged_intra_industry_veg_plants_amount = COALESCE(plants_nu_nomedical_intra_industry_packaged,0),
                            on_packaged_intra_industry_veg_plants_amount = COALESCE(plants_on_nomedical_intra_industry_packaged,0),
                            pe_packaged_intra_industry_veg_plants_amount = COALESCE(plants_pe_nomedical_intra_industry_packaged,0),
                            qc_packaged_intra_industry_veg_plants_amount = COALESCE(plants_qc_nomedical_intra_industry_packaged,0), 
                            sk_packaged_intra_industry_veg_plants_amount = COALESCE(plants_sk_nomedical_intra_industry_packaged,0),
                            yt_packaged_intra_industry_veg_plants_amount = COALESCE(plants_yt_nomedical_intra_industry_packaged,0), 
                            total_packaged_intra_industry_veg_plants_amount = COALESCE(plants_total_nomedical_intra_industry_packaged,0),

                            ab_packaged_intra_industry_veg_plants_value = COALESCE(plants_ab_nomedical_intra_industry_packaged_value,0),
                            mb_packaged_intra_industry_veg_plants_value = COALESCE(plants_mb_nomedical_intra_industry_packaged_value,0),
                            bc_packaged_intra_industry_veg_plants_value = COALESCE(plants_bc_nomedical_intra_industry_packaged_value,0),
                            nb_packaged_intra_industry_veg_plants_value = COALESCE(plants_nb_nomedical_intra_industry_packaged_value,0), 
                            nl_packaged_intra_industry_veg_plants_value = COALESCE(plants_nl_nomedical_intra_industry_packaged_value,0), 
                            ns_packaged_intra_industry_veg_plants_value = COALESCE(plants_ns_nomedical_intra_industry_packaged_value,0),
                            nt_packaged_intra_industry_veg_plants_value = COALESCE(plants_nt_nomedical_intra_industry_packaged_value,0),
                            nu_packaged_intra_industry_veg_plants_value = COALESCE(plants_nu_nomedical_intra_industry_packaged_value,0),
                            on_packaged_intra_industry_veg_plants_value = COALESCE(plants_on_nomedical_intra_industry_packaged_value,0),
                            pe_packaged_intra_industry_veg_plants_value = COALESCE(plants_pe_nomedical_intra_industry_packaged_value,0),
                            qc_packaged_intra_industry_veg_plants_value = COALESCE(plants_qc_nomedical_intra_industry_packaged_value,0), 
                            sk_packaged_intra_industry_veg_plants_value = COALESCE(plants_sk_nomedical_intra_industry_packaged_value,0),
                            yt_packaged_intra_industry_veg_plants_value = COALESCE(plants_yt_nomedical_intra_industry_packaged_value,0), 
                            total_packaged_intra_industry_veg_plants_value = COALESCE(plants_total_nomedical_intra_industry_packaged_value,0),

                            -- distributor fresh_cannabis
                            ab_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_ab_nomedical_distributor,0),
                            bc_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_bc_nomedical_distributor,0),
                            mb_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_mb_nomedical_distributor,0),
                            nb_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_nb_nomedical_distributor,0), 
                            nl_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_nl_nomedical_distributor,0), 
                            ns_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_ns_nomedical_distributor,0),
                            nt_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_nt_nomedical_distributor,0),
                            nu_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_nu_nomedical_distributor,0),
                            on_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_on_nomedical_distributor,0),
                            pe_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_pe_nomedical_distributor,0),
                            qc_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_qc_nomedical_distributor,0), 
                            sk_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_sk_nomedical_distributor,0), 
                            yt_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_yt_nomedical_distributor,0), 
                            total_distributor_fresh_cannabis_amount = COALESCE(fresh_cannabis_total_nomedical_distributor,0),
                            
                            ab_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_ab_nomedical_distributor_value,0),
                            bc_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_bc_nomedical_distributor_value,0),
                            mb_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_mb_nomedical_distributor_value,0),
                            nb_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_nb_nomedical_distributor_value,0), 
                            nl_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_nl_nomedical_distributor_value,0), 
                            ns_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_ns_nomedical_distributor_value,0),
                            nt_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_nt_nomedical_distributor_value,0),
                            nu_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_nu_nomedical_distributor_value,0),
                            on_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_on_nomedical_distributor_value,0),
                            pe_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_pe_nomedical_distributor_value,0),
                            qc_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_qc_nomedical_distributor_value,0), 
                            sk_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_sk_nomedical_distributor_value,0), 
                            yt_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_yt_nomedical_distributor_value,0), 
                            total_distributor_fresh_cannabis_value = COALESCE(fresh_cannabis_total_nomedical_distributor_value,0),

                            -- recreational consumer fresh_cannabis
                            ab_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_ab_nomedical_recreational_consumer,0),
                            bc_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_bc_nomedical_recreational_consumer,0),
                            mb_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_mb_nomedical_recreational_consumer,0),
                            nb_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nb_nomedical_recreational_consumer,0), 
                            nl_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nl_nomedical_recreational_consumer,0), 
                            ns_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_ns_nomedical_recreational_consumer,0),
                            nt_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nt_nomedical_recreational_consumer,0),
                            nu_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nu_nomedical_recreational_consumer,0),
                            on_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_on_nomedical_recreational_consumer,0),
                            pe_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_pe_nomedical_recreational_consumer,0),
                            qc_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_qc_nomedical_recreational_consumer,0), 
                            sk_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_sk_nomedical_recreational_consumer,0), 
                            yt_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_yt_nomedical_recreational_consumer,0), 
                            total_recreational_consumer_fresh_cannabis_amount = COALESCE(fresh_cannabis_total_nomedical_recreational_consumer,0),
                            
                            ab_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_ab_nomedical_recreational_consumer_value,0),
                            bc_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_bc_nomedical_recreational_consumer_value,0),
                            mb_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_mb_nomedical_recreational_consumer_value,0),
                            nb_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_nb_nomedical_recreational_consumer_value,0), 
                            nl_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_nl_nomedical_recreational_consumer_value,0), 
                            ns_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_ns_nomedical_recreational_consumer_value,0),
                            nt_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_nt_nomedical_recreational_consumer_value,0),
                            nu_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_nu_nomedical_recreational_consumer_value,0),
                            on_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_on_nomedical_recreational_consumer_value,0),
                            pe_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_pe_nomedical_recreational_consumer_value,0),
                            qc_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_qc_nomedical_recreational_consumer_value,0), 
                            sk_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_sk_nomedical_recreational_consumer_value,0), 
                            yt_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_yt_nomedical_recreational_consumer_value,0), 
                            total_recreational_consumer_fresh_cannabis_value = COALESCE(fresh_cannabis_total_nomedical_recreational_consumer_value,0),

                            -- retailer fresh_cannabis
                            ab_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_ab_nomedical_retailer,0),
                            bc_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_bc_nomedical_retailer,0),
                            mb_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_mb_nomedical_retailer,0),
                            nb_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nb_nomedical_retailer,0), 
                            nl_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nl_nomedical_retailer,0), 
                            ns_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_ns_nomedical_retailer,0),
                            nt_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nt_nomedical_retailer,0),
                            nu_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_nu_nomedical_retailer,0),
                            on_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_on_nomedical_retailer,0),
                            pe_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_pe_nomedical_retailer,0),
                            qc_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_qc_nomedical_retailer,0), 
                            sk_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_sk_nomedical_retailer,0), 
                            yt_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_yt_nomedical_retailer,0), 
                            total_retailer_fresh_cannabis_amount = COALESCE(fresh_cannabis_total_nomedical_retailer,0),
                            
                            ab_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_ab_nomedical_retailer_value,0),
                            bc_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_bc_nomedical_retailer_value,0),
                            mb_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_mb_nomedical_retailer_value,0),
                            nb_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_nb_nomedical_retailer_value,0), 
                            nl_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_nl_nomedical_retailer_value,0), 
                            ns_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_ns_nomedical_retailer_value,0),
                            nt_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_nt_nomedical_retailer_value,0),
                            nu_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_nu_nomedical_retailer_value,0),
                            on_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_on_nomedical_retailer_value,0),
                            pe_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_pe_nomedical_retailer_value,0),
                            qc_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_qc_nomedical_retailer_value,0), 
                            sk_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_sk_nomedical_retailer_value,0), 
                            yt_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_yt_nomedical_retailer_value,0), 
                            total_retailer_fresh_cannabis_value = COALESCE(fresh_cannabis_total_nomedical_retailer_value,0),

                            -- intra industry fresh_cannabis
                            ab_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_ab_nomedical_intra_industry_unpackaged,0),
                            bc_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_bc_nomedical_intra_industry_unpackaged,0),
                            mb_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_mb_nomedical_intra_industry_unpackaged,0),
                            nb_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nb_nomedical_intra_industry_unpackaged,0), 
                            nl_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nl_nomedical_intra_industry_unpackaged,0), 
                            ns_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_ns_nomedical_intra_industry_unpackaged,0),
                            nt_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nt_nomedical_intra_industry_unpackaged,0),
                            nu_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nu_nomedical_intra_industry_unpackaged,0),
                            on_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_on_nomedical_intra_industry_unpackaged,0),
                            pe_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_pe_nomedical_intra_industry_unpackaged,0),
                            qc_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_qc_nomedical_intra_industry_unpackaged,0), 
                            sk_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_sk_nomedical_intra_industry_unpackaged,0),
                            yt_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_yt_nomedical_intra_industry_unpackaged,0), 
                            total_unpackaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_total_nomedical_intra_industry_unpackaged,0),
                            
                            ab_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_ab_nomedical_intra_industry_unpackaged_value,0),
                            bc_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_bc_nomedical_intra_industry_unpackaged_value,0),
                            mb_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_mb_nomedical_intra_industry_unpackaged_value,0),
                            nb_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nb_nomedical_intra_industry_unpackaged_value,0), 
                            nl_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nl_nomedical_intra_industry_unpackaged_value,0), 
                            ns_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_ns_nomedical_intra_industry_unpackaged_value,0),
                            nt_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nt_nomedical_intra_industry_unpackaged_value,0),
                            nu_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nu_nomedical_intra_industry_unpackaged_value,0),
                            on_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_on_nomedical_intra_industry_unpackaged_value,0),
                            pe_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_pe_nomedical_intra_industry_unpackaged_value,0),
                            qc_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_qc_nomedical_intra_industry_unpackaged_value,0), 
                            sk_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_sk_nomedical_intra_industry_unpackaged_value,0),
                            yt_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_yt_nomedical_intra_industry_unpackaged_value,0), 
                            total_unpackaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_total_nomedical_intra_industry_unpackaged_value,0),

                            ab_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_ab_nomedical_intra_industry_packaged,0),
                            bc_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_bc_nomedical_intra_industry_packaged,0),
                            mb_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_mb_nomedical_intra_industry_packaged,0),
                            nb_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nb_nomedical_intra_industry_packaged,0), 
                            nl_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nl_nomedical_intra_industry_packaged,0), 
                            ns_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_ns_nomedical_intra_industry_packaged,0),
                            nt_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nt_nomedical_intra_industry_packaged,0),
                            nu_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_nu_nomedical_intra_industry_packaged,0),
                            on_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_on_nomedical_intra_industry_packaged,0),
                            pe_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_pe_nomedical_intra_industry_packaged,0),
                            qc_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_qc_nomedical_intra_industry_packaged,0), 
                            sk_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_sk_nomedical_intra_industry_packaged,0),
                            yt_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_yt_nomedical_intra_industry_packaged,0), 
                            total_packaged_intra_industry_fresh_cannabis_weight = COALESCE(fresh_cannabis_total_nomedical_intra_industry_packaged,0),
                            
                            ab_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_ab_nomedical_intra_industry_packaged_value,0),
                            bc_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_bc_nomedical_intra_industry_packaged_value,0),
                            mb_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_mb_nomedical_intra_industry_packaged_value,0),
                            nb_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nb_nomedical_intra_industry_packaged_value,0), 
                            nl_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nl_nomedical_intra_industry_packaged_value,0), 
                            ns_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_ns_nomedical_intra_industry_packaged_value,0),
                            nt_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nt_nomedical_intra_industry_packaged_value,0),
                            nu_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_nu_nomedical_intra_industry_packaged_value,0),
                            on_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_on_nomedical_intra_industry_packaged_value,0),
                            pe_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_pe_nomedical_intra_industry_packaged_value,0),
                            qc_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_qc_nomedical_intra_industry_packaged_value,0), 
                            sk_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_sk_nomedical_intra_industry_packaged_value,0),
                            yt_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_yt_nomedical_intra_industry_packaged_value,0), 
                            total_packaged_intra_industry_fresh_cannabis_value = COALESCE(fresh_cannabis_total_nomedical_intra_industry_packaged_value,0),

                            -- distributor dried_cannabis
                            ab_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_ab_nomedical_distributor,0),
                            bc_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_bc_nomedical_distributor,0),
                            mb_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_mb_nomedical_distributor,0),
                            nb_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_nb_nomedical_distributor,0), 
                            nl_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_nl_nomedical_distributor,0), 
                            ns_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_ns_nomedical_distributor,0),
                            nt_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_nt_nomedical_distributor,0),
                            nu_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_nu_nomedical_distributor,0),
                            on_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_on_nomedical_distributor,0),
                            pe_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_pe_nomedical_distributor,0),
                            qc_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_qc_nomedical_distributor,0), 
                            sk_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_sk_nomedical_distributor,0), 
                            yt_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_yt_nomedical_distributor,0), 
                            total_distributor_dried_cannabis_amount = COALESCE(dried_cannabis_total_nomedical_distributor,0),
                            
                            ab_distributor_dried_cannabis_value = COALESCE(dried_cannabis_ab_nomedical_distributor_value,0),
                            bc_distributor_dried_cannabis_value = COALESCE(dried_cannabis_bc_nomedical_distributor_value,0),
                            mb_distributor_dried_cannabis_value = COALESCE(dried_cannabis_mb_nomedical_distributor_value,0),
                            nb_distributor_dried_cannabis_value = COALESCE(dried_cannabis_nb_nomedical_distributor_value,0), 
                            nl_distributor_dried_cannabis_value = COALESCE(dried_cannabis_nl_nomedical_distributor_value,0), 
                            ns_distributor_dried_cannabis_value = COALESCE(dried_cannabis_ns_nomedical_distributor_value,0),
                            nt_distributor_dried_cannabis_value = COALESCE(dried_cannabis_nt_nomedical_distributor_value,0),
                            nu_distributor_dried_cannabis_value = COALESCE(dried_cannabis_nu_nomedical_distributor_value,0),
                            on_distributor_dried_cannabis_value = COALESCE(dried_cannabis_on_nomedical_distributor_value,0),
                            pe_distributor_dried_cannabis_value = COALESCE(dried_cannabis_pe_nomedical_distributor_value,0),
                            qc_distributor_dried_cannabis_value = COALESCE(dried_cannabis_qc_nomedical_distributor_value,0), 
                            sk_distributor_dried_cannabis_value = COALESCE(dried_cannabis_sk_nomedical_distributor_value,0), 
                            yt_distributor_dried_cannabis_value = COALESCE(dried_cannabis_yt_nomedical_distributor_value,0), 
                            total_distributor_dried_cannabis_value = COALESCE(dried_cannabis_total_nomedical_distributor_value,0),

                            -- recreational consumer dried_cannabis
                            ab_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_ab_nomedical_recreational_consumer,0),
                            bc_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_bc_nomedical_recreational_consumer,0),
                            mb_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_mb_nomedical_recreational_consumer,0),
                            nb_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_nb_nomedical_recreational_consumer,0), 
                            nl_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_nl_nomedical_recreational_consumer,0), 
                            ns_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_ns_nomedical_recreational_consumer,0),
                            nt_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_nt_nomedical_recreational_consumer,0),
                            nu_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_nu_nomedical_recreational_consumer,0),
                            on_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_on_nomedical_recreational_consumer,0),
                            pe_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_pe_nomedical_recreational_consumer,0),
                            qc_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_qc_nomedical_recreational_consumer,0), 
                            sk_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_sk_nomedical_recreational_consumer,0), 
                            yt_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_yt_nomedical_recreational_consumer,0), 
                            total_recreational_consumer_dried_cannabis_amount = COALESCE(dried_cannabis_total_nomedical_recreational_consumer,0),
                            
                            ab_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_ab_nomedical_recreational_consumer_value,0),
                            bc_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_bc_nomedical_recreational_consumer_value,0),
                            mb_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_mb_nomedical_recreational_consumer_value,0),
                            nb_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_nb_nomedical_recreational_consumer_value,0), 
                            nl_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_nl_nomedical_recreational_consumer_value,0), 
                            ns_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_ns_nomedical_recreational_consumer_value,0),
                            nt_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_nt_nomedical_recreational_consumer_value,0),
                            nu_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_nu_nomedical_recreational_consumer_value,0),
                            on_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_on_nomedical_recreational_consumer_value,0),
                            pe_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_pe_nomedical_recreational_consumer_value,0),
                            qc_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_qc_nomedical_recreational_consumer_value,0), 
                            sk_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_sk_nomedical_recreational_consumer_value,0), 
                            yt_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_yt_nomedical_recreational_consumer_value,0), 
                            total_recreational_consumer_dried_cannabis_value = COALESCE(dried_cannabis_total_nomedical_recreational_consumer_value,0),

                            -- retailer dried_cannabis
                            ab_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_ab_nomedical_retailer,0),
                            bc_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_bc_nomedical_retailer,0),
                            mb_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_mb_nomedical_retailer,0),
                            nb_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_nb_nomedical_retailer,0), 
                            nl_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_nl_nomedical_retailer,0), 
                            ns_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_ns_nomedical_retailer,0),
                            nt_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_nt_nomedical_retailer,0),
                            nu_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_nu_nomedical_retailer,0),
                            on_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_on_nomedical_retailer,0),
                            pe_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_pe_nomedical_retailer,0),
                            qc_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_qc_nomedical_retailer,0), 
                            sk_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_sk_nomedical_retailer,0), 
                            yt_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_yt_nomedical_retailer,0), 
                            total_retailer_dried_cannabis_amount = COALESCE(dried_cannabis_total_nomedical_retailer,0),
                            
                            ab_retailer_dried_cannabis_value = COALESCE(dried_cannabis_ab_nomedical_retailer_value,0),
                            bc_retailer_dried_cannabis_value = COALESCE(dried_cannabis_bc_nomedical_retailer_value,0),
                            mb_retailer_dried_cannabis_value = COALESCE(dried_cannabis_mb_nomedical_retailer_value,0),
                            nb_retailer_dried_cannabis_value = COALESCE(dried_cannabis_nb_nomedical_retailer_value,0), 
                            nl_retailer_dried_cannabis_value = COALESCE(dried_cannabis_nl_nomedical_retailer_value,0), 
                            ns_retailer_dried_cannabis_value = COALESCE(dried_cannabis_ns_nomedical_retailer_value,0),
                            nt_retailer_dried_cannabis_value = COALESCE(dried_cannabis_nt_nomedical_retailer_value,0),
                            nu_retailer_dried_cannabis_value = COALESCE(dried_cannabis_nu_nomedical_retailer_value,0),
                            on_retailer_dried_cannabis_value = COALESCE(dried_cannabis_on_nomedical_retailer_value,0),
                            pe_retailer_dried_cannabis_value = COALESCE(dried_cannabis_pe_nomedical_retailer_value,0),
                            qc_retailer_dried_cannabis_value = COALESCE(dried_cannabis_qc_nomedical_retailer_value,0), 
                            sk_retailer_dried_cannabis_value = COALESCE(dried_cannabis_sk_nomedical_retailer_value,0), 
                            yt_retailer_dried_cannabis_value = COALESCE(dried_cannabis_yt_nomedical_retailer_value,0), 
                            total_retailer_dried_cannabis_value = COALESCE(dried_cannabis_total_nomedical_retailer_value,0),

                            -- intra industry dried_cannabis
                            ab_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_ab_nomedical_intra_industry_unpackaged,0),
                            bc_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_bc_nomedical_intra_industry_unpackaged,0),
                            mb_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_mb_nomedical_intra_industry_unpackaged,0),
                            nb_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nb_nomedical_intra_industry_unpackaged,0), 
                            nl_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nl_nomedical_intra_industry_unpackaged,0), 
                            ns_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_ns_nomedical_intra_industry_unpackaged,0),
                            nt_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nt_nomedical_intra_industry_unpackaged,0),
                            nu_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nu_nomedical_intra_industry_unpackaged,0),
                            on_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_on_nomedical_intra_industry_unpackaged,0),
                            pe_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_pe_nomedical_intra_industry_unpackaged,0),
                            qc_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_qc_nomedical_intra_industry_unpackaged,0), 
                            sk_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_sk_nomedical_intra_industry_unpackaged,0),
                            yt_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_yt_nomedical_intra_industry_unpackaged,0), 
                            total_unpackaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_total_nomedical_intra_industry_unpackaged,0),
                            
                            ab_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_ab_nomedical_intra_industry_unpackaged_value,0),
                            bc_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_bc_nomedical_intra_industry_unpackaged_value,0),
                            mb_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_mb_nomedical_intra_industry_unpackaged_value,0),
                            nb_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nb_nomedical_intra_industry_unpackaged_value,0), 
                            nl_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nl_nomedical_intra_industry_unpackaged_value,0), 
                            ns_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_ns_nomedical_intra_industry_unpackaged_value,0),
                            nt_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nt_nomedical_intra_industry_unpackaged_value,0),
                            nu_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nu_nomedical_intra_industry_unpackaged_value,0),
                            on_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_on_nomedical_intra_industry_unpackaged_value,0),
                            pe_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_pe_nomedical_intra_industry_unpackaged_value,0),
                            qc_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_qc_nomedical_intra_industry_unpackaged_value,0), 
                            sk_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_sk_nomedical_intra_industry_unpackaged_value,0),
                            yt_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_yt_nomedical_intra_industry_unpackaged_value,0), 
                            total_unpackaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_total_nomedical_intra_industry_unpackaged_value,0),

                            ab_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_ab_nomedical_intra_industry_packaged,0),
                            bc_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_bc_nomedical_intra_industry_packaged,0),
                            mb_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_mb_nomedical_intra_industry_packaged,0),
                            nb_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nb_nomedical_intra_industry_packaged,0), 
                            nl_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nl_nomedical_intra_industry_packaged,0), 
                            ns_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_ns_nomedical_intra_industry_packaged,0),
                            nt_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nt_nomedical_intra_industry_packaged,0),
                            nu_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_nu_nomedical_intra_industry_packaged,0),
                            on_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_on_nomedical_intra_industry_packaged,0),
                            pe_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_pe_nomedical_intra_industry_packaged,0),
                            qc_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_qc_nomedical_intra_industry_packaged,0), 
                            sk_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_sk_nomedical_intra_industry_packaged,0),
                            yt_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_yt_nomedical_intra_industry_packaged,0), 
                            total_packaged_intra_industry_dried_cannabis_weight = COALESCE(dried_cannabis_total_nomedical_intra_industry_packaged,0),
                            
                            ab_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_ab_nomedical_intra_industry_packaged_value,0),
                            bc_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_bc_nomedical_intra_industry_packaged_value,0),
                            mb_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_mb_nomedical_intra_industry_packaged_value,0),
                            nb_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nb_nomedical_intra_industry_packaged_value,0), 
                            nl_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nl_nomedical_intra_industry_packaged_value,0), 
                            ns_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_ns_nomedical_intra_industry_packaged_value,0),
                            nt_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nt_nomedical_intra_industry_packaged_value,0),
                            nu_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_nu_nomedical_intra_industry_packaged_value,0),
                            on_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_on_nomedical_intra_industry_packaged_value,0),
                            pe_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_pe_nomedical_intra_industry_packaged_value,0),
                            qc_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_qc_nomedical_intra_industry_packaged_value,0), 
                            sk_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_sk_nomedical_intra_industry_packaged_value,0),
                            yt_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_yt_nomedical_intra_industry_packaged_value,0), 
                            total_packaged_intra_industry_dried_cannabis_value = COALESCE(dried_cannabis_total_nomedical_intra_industry_packaged_value,0),

                            -- distributor extracts
                            ab_distributor_extracts_amount = COALESCE(extracts_ab_nomedical_distributor,0),
                            bc_distributor_extracts_amount = COALESCE(extracts_bc_nomedical_distributor,0),
                            mb_distributor_extracts_amount = COALESCE(extracts_mb_nomedical_distributor,0),
                            nb_distributor_extracts_amount = COALESCE(extracts_nb_nomedical_distributor,0), 
                            nl_distributor_extracts_amount = COALESCE(extracts_nl_nomedical_distributor,0), 
                            ns_distributor_extracts_amount = COALESCE(extracts_ns_nomedical_distributor,0),
                            nt_distributor_extracts_amount = COALESCE(extracts_nt_nomedical_distributor,0),
                            nu_distributor_extracts_amount = COALESCE(extracts_nu_nomedical_distributor,0),
                            on_distributor_extracts_amount = COALESCE(extracts_on_nomedical_distributor,0),
                            pe_distributor_extracts_amount = COALESCE(extracts_pe_nomedical_distributor,0),
                            qc_distributor_extracts_amount = COALESCE(extracts_qc_nomedical_distributor,0), 
                            sk_distributor_extracts_amount = COALESCE(extracts_sk_nomedical_distributor,0), 
                            yt_distributor_extracts_amount = COALESCE(extracts_yt_nomedical_distributor,0), 
                            total_distributor_extracts_amount = COALESCE(extracts_total_nomedical_distributor,0),
                            
                            ab_distributor_extracts_value = COALESCE(extracts_ab_nomedical_distributor_value,0),
                            bc_distributor_extracts_value = COALESCE(extracts_bc_nomedical_distributor_value,0),
                            mb_distributor_extracts_value = COALESCE(extracts_mb_nomedical_distributor_value,0),
                            nb_distributor_extracts_value = COALESCE(extracts_nb_nomedical_distributor_value,0), 
                            nl_distributor_extracts_value = COALESCE(extracts_nl_nomedical_distributor_value,0), 
                            ns_distributor_extracts_value = COALESCE(extracts_ns_nomedical_distributor_value,0),
                            nt_distributor_extracts_value = COALESCE(extracts_nt_nomedical_distributor_value,0),
                            nu_distributor_extracts_value = COALESCE(extracts_nu_nomedical_distributor_value,0),
                            on_distributor_extracts_value = COALESCE(extracts_on_nomedical_distributor_value,0),
                            pe_distributor_extracts_value = COALESCE(extracts_pe_nomedical_distributor_value,0),
                            qc_distributor_extracts_value = COALESCE(extracts_qc_nomedical_distributor_value,0), 
                            sk_distributor_extracts_value = COALESCE(extracts_sk_nomedical_distributor_value,0), 
                            yt_distributor_extracts_value = COALESCE(extracts_yt_nomedical_distributor_value,0), 
                            total_distributor_extracts_value = COALESCE(extracts_total_nomedical_distributor_value,0),

                            -- recreational consumer extracts
                            ab_recreational_consumer_extracts_amount = COALESCE(extracts_ab_nomedical_recreational_consumer,0),
                            bc_recreational_consumer_extracts_amount = COALESCE(extracts_bc_nomedical_recreational_consumer,0),
                            mb_recreational_consumer_extracts_amount = COALESCE(extracts_mb_nomedical_recreational_consumer,0),
                            nb_recreational_consumer_extracts_amount = COALESCE(extracts_nb_nomedical_recreational_consumer,0), 
                            nl_recreational_consumer_extracts_amount = COALESCE(extracts_nl_nomedical_recreational_consumer,0), 
                            ns_recreational_consumer_extracts_amount = COALESCE(extracts_ns_nomedical_recreational_consumer,0),
                            nt_recreational_consumer_extracts_amount = COALESCE(extracts_nt_nomedical_recreational_consumer,0),
                            nu_recreational_consumer_extracts_amount = COALESCE(extracts_nu_nomedical_recreational_consumer,0),
                            on_recreational_consumer_extracts_amount = COALESCE(extracts_on_nomedical_recreational_consumer,0),
                            pe_recreational_consumer_extracts_amount = COALESCE(extracts_pe_nomedical_recreational_consumer,0),
                            qc_recreational_consumer_extracts_amount = COALESCE(extracts_qc_nomedical_recreational_consumer,0), 
                            sk_recreational_consumer_extracts_amount = COALESCE(extracts_sk_nomedical_recreational_consumer,0), 
                            yt_recreational_consumer_extracts_amount = COALESCE(extracts_yt_nomedical_recreational_consumer,0), 
                            total_recreational_consumer_extracts_amount = COALESCE(extracts_total_nomedical_recreational_consumer,0),
                            
                            ab_recreational_consumer_extracts_value = COALESCE(extracts_ab_nomedical_recreational_consumer_value,0),
                            bc_recreational_consumer_extracts_value = COALESCE(extracts_bc_nomedical_recreational_consumer_value,0),
                            mb_recreational_consumer_extracts_value = COALESCE(extracts_mb_nomedical_recreational_consumer_value,0),
                            nb_recreational_consumer_extracts_value = COALESCE(extracts_nb_nomedical_recreational_consumer_value,0), 
                            nl_recreational_consumer_extracts_value = COALESCE(extracts_nl_nomedical_recreational_consumer_value,0), 
                            ns_recreational_consumer_extracts_value = COALESCE(extracts_ns_nomedical_recreational_consumer_value,0),
                            nt_recreational_consumer_extracts_value = COALESCE(extracts_nt_nomedical_recreational_consumer_value,0),
                            nu_recreational_consumer_extracts_value = COALESCE(extracts_nu_nomedical_recreational_consumer_value,0),
                            on_recreational_consumer_extracts_value = COALESCE(extracts_on_nomedical_recreational_consumer_value,0),
                            pe_recreational_consumer_extracts_value = COALESCE(extracts_pe_nomedical_recreational_consumer_value,0),
                            qc_recreational_consumer_extracts_value = COALESCE(extracts_qc_nomedical_recreational_consumer_value,0), 
                            sk_recreational_consumer_extracts_value = COALESCE(extracts_sk_nomedical_recreational_consumer_value,0), 
                            yt_recreational_consumer_extracts_value = COALESCE(extracts_yt_nomedical_recreational_consumer_value,0), 
                            total_recreational_consumer_extracts_value = COALESCE(extracts_total_nomedical_recreational_consumer_value,0),

                            -- retailer extracts
                            ab_retailer_extracts_amount = COALESCE(extracts_ab_nomedical_retailer,0),
                            bc_retailer_extracts_amount = COALESCE(extracts_bc_nomedical_retailer,0),
                            mb_retailer_extracts_amount = COALESCE(extracts_mb_nomedical_retailer,0),
                            nb_retailer_extracts_amount = COALESCE(extracts_nb_nomedical_retailer,0), 
                            nl_retailer_extracts_amount = COALESCE(extracts_nl_nomedical_retailer,0), 
                            ns_retailer_extracts_amount = COALESCE(extracts_ns_nomedical_retailer,0),
                            nt_retailer_extracts_amount = COALESCE(extracts_nt_nomedical_retailer,0),
                            nu_retailer_extracts_amount = COALESCE(extracts_nu_nomedical_retailer,0),
                            on_retailer_extracts_amount = COALESCE(extracts_on_nomedical_retailer,0),
                            pe_retailer_extracts_amount = COALESCE(extracts_pe_nomedical_retailer,0),
                            qc_retailer_extracts_amount = COALESCE(extracts_qc_nomedical_retailer,0), 
                            sk_retailer_extracts_amount = COALESCE(extracts_sk_nomedical_retailer,0), 
                            yt_retailer_extracts_amount = COALESCE(extracts_yt_nomedical_retailer,0), 
                            total_retailer_extracts_amount = COALESCE(extracts_total_nomedical_retailer,0),
                            
                            ab_retailer_extracts_value = COALESCE(extracts_ab_nomedical_retailer_value,0),
                            bc_retailer_extracts_value = COALESCE(extracts_bc_nomedical_retailer_value,0),
                            mb_retailer_extracts_value = COALESCE(extracts_mb_nomedical_retailer_value,0),
                            nb_retailer_extracts_value = COALESCE(extracts_nb_nomedical_retailer_value,0), 
                            nl_retailer_extracts_value = COALESCE(extracts_nl_nomedical_retailer_value,0), 
                            ns_retailer_extracts_value = COALESCE(extracts_ns_nomedical_retailer_value,0),
                            nt_retailer_extracts_value = COALESCE(extracts_nt_nomedical_retailer_value,0),
                            nu_retailer_extracts_value = COALESCE(extracts_nu_nomedical_retailer_value,0),
                            on_retailer_extracts_value = COALESCE(extracts_on_nomedical_retailer_value,0),
                            pe_retailer_extracts_value = COALESCE(extracts_pe_nomedical_retailer_value,0),
                            qc_retailer_extracts_value = COALESCE(extracts_qc_nomedical_retailer_value,0), 
                            sk_retailer_extracts_value = COALESCE(extracts_sk_nomedical_retailer_value,0), 
                            yt_retailer_extracts_value = COALESCE(extracts_yt_nomedical_retailer_value,0), 
                            total_retailer_extracts_value = COALESCE(extracts_total_nomedical_retailer_value,0),

                            -- intra industry extracts
                            ab_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_ab_nomedical_intra_industry_unpackaged,0),
                            bc_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_bc_nomedical_intra_industry_unpackaged,0),
                            mb_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_mb_nomedical_intra_industry_unpackaged,0),
                            nb_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_nb_nomedical_intra_industry_unpackaged,0), 
                            nl_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_nl_nomedical_intra_industry_unpackaged,0), 
                            ns_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_ns_nomedical_intra_industry_unpackaged,0),
                            nt_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_nt_nomedical_intra_industry_unpackaged,0),
                            nu_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_nu_nomedical_intra_industry_unpackaged,0),
                            on_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_on_nomedical_intra_industry_unpackaged,0),
                            pe_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_pe_nomedical_intra_industry_unpackaged,0),
                            qc_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_qc_nomedical_intra_industry_unpackaged,0), 
                            sk_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_sk_nomedical_intra_industry_unpackaged,0),
                            yt_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_yt_nomedical_intra_industry_unpackaged,0), 
                            total_unpackaged_intra_industry_extracts_weight = COALESCE(extracts_total_nomedical_intra_industry_unpackaged,0),
                            
                            ab_unpackaged_intra_industry_extracts_value = COALESCE(extracts_ab_nomedical_intra_industry_unpackaged_value,0),
                            bc_unpackaged_intra_industry_extracts_value = COALESCE(extracts_bc_nomedical_intra_industry_unpackaged_value,0),
                            mb_unpackaged_intra_industry_extracts_value = COALESCE(extracts_mb_nomedical_intra_industry_unpackaged_value,0),
                            nb_unpackaged_intra_industry_extracts_value = COALESCE(extracts_nb_nomedical_intra_industry_unpackaged_value,0), 
                            nl_unpackaged_intra_industry_extracts_value = COALESCE(extracts_nl_nomedical_intra_industry_unpackaged_value,0), 
                            ns_unpackaged_intra_industry_extracts_value = COALESCE(extracts_ns_nomedical_intra_industry_unpackaged_value,0),
                            nt_unpackaged_intra_industry_extracts_value = COALESCE(extracts_nt_nomedical_intra_industry_unpackaged_value,0),
                            nu_unpackaged_intra_industry_extracts_value = COALESCE(extracts_nu_nomedical_intra_industry_unpackaged_value,0),
                            on_unpackaged_intra_industry_extracts_value = COALESCE(extracts_on_nomedical_intra_industry_unpackaged_value,0),
                            pe_unpackaged_intra_industry_extracts_value = COALESCE(extracts_pe_nomedical_intra_industry_unpackaged_value,0),
                            qc_unpackaged_intra_industry_extracts_value = COALESCE(extracts_qc_nomedical_intra_industry_unpackaged_value,0), 
                            sk_unpackaged_intra_industry_extracts_value = COALESCE(extracts_sk_nomedical_intra_industry_unpackaged_value,0),
                            yt_unpackaged_intra_industry_extracts_value = COALESCE(extracts_yt_nomedical_intra_industry_unpackaged_value,0), 
                            total_unpackaged_intra_industry_extracts_value = COALESCE(extracts_total_nomedical_intra_industry_unpackaged_value,0),

                            ab_packaged_intra_industry_extracts_weight = COALESCE(extracts_ab_nomedical_intra_industry_packaged,0),
                            bc_packaged_intra_industry_extracts_weight = COALESCE(extracts_bc_nomedical_intra_industry_packaged,0),
                            mb_packaged_intra_industry_extracts_weight = COALESCE(extracts_mb_nomedical_intra_industry_packaged,0),
                            nb_packaged_intra_industry_extracts_weight = COALESCE(extracts_nb_nomedical_intra_industry_packaged,0), 
                            nl_packaged_intra_industry_extracts_weight = COALESCE(extracts_nl_nomedical_intra_industry_packaged,0), 
                            ns_packaged_intra_industry_extracts_weight = COALESCE(extracts_ns_nomedical_intra_industry_packaged,0),
                            nt_packaged_intra_industry_extracts_weight = COALESCE(extracts_nt_nomedical_intra_industry_packaged,0),
                            nu_packaged_intra_industry_extracts_weight = COALESCE(extracts_nu_nomedical_intra_industry_packaged,0),
                            on_packaged_intra_industry_extracts_weight = COALESCE(extracts_on_nomedical_intra_industry_packaged,0),
                            pe_packaged_intra_industry_extracts_weight = COALESCE(extracts_pe_nomedical_intra_industry_packaged,0),
                            qc_packaged_intra_industry_extracts_weight = COALESCE(extracts_qc_nomedical_intra_industry_packaged,0), 
                            sk_packaged_intra_industry_extracts_weight = COALESCE(extracts_sk_nomedical_intra_industry_packaged,0),
                            yt_packaged_intra_industry_extracts_weight = COALESCE(extracts_yt_nomedical_intra_industry_packaged,0), 
                            total_packaged_intra_industry_extracts_weight = COALESCE(extracts_total_nomedical_intra_industry_packaged,0),
                            
                            ab_packaged_intra_industry_extracts_value = COALESCE(extracts_ab_nomedical_intra_industry_packaged_value,0),
                            bc_packaged_intra_industry_extracts_value = COALESCE(extracts_bc_nomedical_intra_industry_packaged_value,0),
                            mb_packaged_intra_industry_extracts_value = COALESCE(extracts_mb_nomedical_intra_industry_packaged_value,0),
                            nb_packaged_intra_industry_extracts_value = COALESCE(extracts_nb_nomedical_intra_industry_packaged_value,0), 
                            nl_packaged_intra_industry_extracts_value = COALESCE(extracts_nl_nomedical_intra_industry_packaged_value,0), 
                            ns_packaged_intra_industry_extracts_value = COALESCE(extracts_ns_nomedical_intra_industry_packaged_value,0),
                            nt_packaged_intra_industry_extracts_value = COALESCE(extracts_nt_nomedical_intra_industry_packaged_value,0),
                            nu_packaged_intra_industry_extracts_value = COALESCE(extracts_nu_nomedical_intra_industry_packaged_value,0),
                            on_packaged_intra_industry_extracts_value = COALESCE(extracts_on_nomedical_intra_industry_packaged_value,0),
                            pe_packaged_intra_industry_extracts_value = COALESCE(extracts_pe_nomedical_intra_industry_packaged_value,0),
                            qc_packaged_intra_industry_extracts_value = COALESCE(extracts_qc_nomedical_intra_industry_packaged_value,0), 
                            sk_packaged_intra_industry_extracts_value = COALESCE(extracts_sk_nomedical_intra_industry_packaged_value,0),
                            yt_packaged_intra_industry_extracts_value = COALESCE(extracts_yt_nomedical_intra_industry_packaged_value,0), 
                            total_packaged_intra_industry_extracts_value = COALESCE(extracts_total_nomedical_intra_industry_packaged_value,0)
                            
                        FROM (
                            SELECT
                            -- seeds distributor
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as seeds_ab_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as seeds_bc_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as seeds_mb_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as seeds_nb_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as seeds_nl_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as seeds_ns_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as seeds_nt_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as seeds_nu_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as seeds_on_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as seeds_pe_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as seeds_qc_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as seeds_sk_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as seeds_yt_nomedical_distributor,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.type = 'nonmedical_distributor') as seeds_total_nomedical_distributor,
                            
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as seeds_ab_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as seeds_bc_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as seeds_mb_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as seeds_nb_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as seeds_nl_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as seeds_ns_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as seeds_nt_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as seeds_nu_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as seeds_on_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as seeds_pe_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as seeds_qc_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as seeds_sk_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as seeds_yt_nomedical_distributor_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.type = 'nonmedical_distributor') as seeds_total_nomedical_distributor_value,

                            -- seeds recreational consumer
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_ab_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as seeds_bc_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_mb_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nb_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nl_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as seeds_ns_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nt_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nu_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as seeds_on_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as seeds_pe_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as seeds_qc_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as seeds_sk_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as seeds_yt_nomedical_recreational_consumer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as seeds_total_nomedical_recreational_consumer,
                            
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_ab_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as seeds_bc_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_mb_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nb_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nl_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as seeds_ns_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nt_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as seeds_nu_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as seeds_on_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as seeds_pe_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as seeds_qc_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as seeds_sk_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as seeds_yt_nomedical_recreational_consumer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as seeds_total_nomedical_recreational_consumer_value,

                            -- seeds retailer
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as seeds_ab_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as seeds_bc_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as seeds_mb_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as seeds_nb_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as seeds_nl_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as seeds_ns_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as seeds_nt_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as seeds_nu_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as seeds_on_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as seeds_pe_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as seeds_qc_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as seeds_sk_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as seeds_yt_nomedical_retailer,
                            SUM(T3.seeds_qty) FILTER (WHERE T3.type = 'nonmedical_retailer') as seeds_total_nomedical_retailer,
                            
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as seeds_ab_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as seeds_bc_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as seeds_mb_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as seeds_nb_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as seeds_nl_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as seeds_ns_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as seeds_nt_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as seeds_nu_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as seeds_on_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as seeds_pe_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as seeds_qc_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as seeds_sk_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as seeds_yt_nomedical_retailer_value,
                            SUM(T3.seeds_qty_value) FILTER (WHERE T3.type = 'nonmedical_retailer') as seeds_total_nomedical_retailer_value,

                            -- plants distributor
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as plants_ab_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as plants_bc_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as plants_mb_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as plants_nb_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as plants_nl_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as plants_ns_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as plants_nt_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as plants_nu_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as plants_on_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as plants_pe_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as plants_qc_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as plants_sk_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as plants_yt_nomedical_distributor,
                            SUM(T3.plants_qty) FILTER (WHERE T3.type = 'nonmedical_distributor') as plants_total_nomedical_distributor,
                            
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as plants_ab_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as plants_bc_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as plants_mb_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as plants_nb_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as plants_nl_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as plants_ns_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as plants_nt_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as plants_nu_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as plants_on_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as plants_pe_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as plants_qc_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as plants_sk_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as plants_yt_nomedical_distributor_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.type = 'nonmedical_distributor') as plants_total_nomedical_distributor_value,

                            -- plants recreational consumer
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as plants_ab_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as plants_bc_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as plants_mb_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as plants_nb_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as plants_nl_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as plants_ns_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as plants_nt_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as plants_nu_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as plants_on_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as plants_pe_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as plants_qc_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as plants_sk_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as plants_yt_nomedical_recreational_consumer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as plants_total_nomedical_recreational_consumer,
                            
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as plants_ab_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as plants_bc_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as plants_mb_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as plants_nb_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as plants_nl_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as plants_ns_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as plants_nt_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as plants_nu_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as plants_on_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as plants_pe_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as plants_qc_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as plants_sk_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as plants_yt_nomedical_recreational_consumer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as plants_total_nomedical_recreational_consumer_value,

                            -- plants retailer
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as plants_ab_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as plants_bc_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as plants_mb_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as plants_nb_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as plants_nl_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as plants_ns_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as plants_nt_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as plants_nu_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as plants_on_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as plants_pe_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as plants_qc_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as plants_sk_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as plants_yt_nomedical_retailer,
                            SUM(T3.plants_qty) FILTER (WHERE T3.type = 'nonmedical_retailer') as plants_total_nomedical_retailer,
                            
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as plants_ab_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as plants_bc_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as plants_mb_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as plants_nb_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as plants_nl_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as plants_ns_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as plants_nt_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as plants_nu_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as plants_on_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as plants_pe_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as plants_qc_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as plants_sk_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as plants_yt_nomedical_retailer_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.type = 'nonmedical_retailer') as plants_total_nomedical_retailer_value,

                            -- plants intra industry
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_ab_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_bc_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_mb_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nb_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nl_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_ns_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nt_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nu_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_on_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_pe_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_qc_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_sk_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_yt_nomedical_intra_industry_unpackaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_total_nomedical_intra_industry_unpackaged,
                        
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_ab_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_bc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_mb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nl_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_ns_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_nu_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_on_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_pe_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_qc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_sk_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_yt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as plants_total_nomedical_intra_industry_unpackaged_value,

                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_ab_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_bc_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_mb_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nb_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nl_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_ns_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nt_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nu_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_on_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_pe_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_qc_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_sk_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_yt_nomedical_intra_industry_packaged,
                            SUM(T3.plants_qty) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_total_nomedical_intra_industry_packaged,
                            
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_ab_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_bc_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_mb_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nb_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nl_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_ns_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nt_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_nu_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_on_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_pe_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_qc_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_sk_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_yt_nomedical_intra_industry_packaged_value,
                            SUM(T3.plants_qty_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as plants_total_nomedical_intra_industry_packaged_value,

                            -- fresh_cannabis distributor
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_ab_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_bc_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_mb_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nb_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nl_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_ns_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nt_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nu_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_on_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_pe_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_qc_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_sk_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_yt_nomedical_distributor,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_distributor') as fresh_cannabis_total_nomedical_distributor,
                            
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_ab_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_bc_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_mb_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nb_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nl_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_ns_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nt_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_nu_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_on_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_pe_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_qc_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_sk_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as fresh_cannabis_yt_nomedical_distributor_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_distributor') as fresh_cannabis_total_nomedical_distributor_value,

                            -- fresh_cannabis recreational consumer
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_ab_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_bc_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_mb_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nb_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nl_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_ns_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nt_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nu_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_on_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_pe_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_qc_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_sk_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_yt_nomedical_recreational_consumer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_total_nomedical_recreational_consumer,
                            
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_ab_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_bc_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_mb_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nb_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nl_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_ns_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nt_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_nu_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_on_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_pe_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_qc_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_sk_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_yt_nomedical_recreational_consumer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as fresh_cannabis_total_nomedical_recreational_consumer_value,

                            -- fresh_cannabis retailer
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_ab_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_bc_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_mb_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nb_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nl_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_ns_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nt_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nu_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_on_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_pe_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_qc_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_sk_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_yt_nomedical_retailer,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_retailer') as fresh_cannabis_total_nomedical_retailer,
                            
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_ab_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_bc_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_mb_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nb_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nl_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_ns_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nt_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_nu_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_on_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_pe_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_qc_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_sk_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as fresh_cannabis_yt_nomedical_retailer_value,
                            SUM(T3.fresh_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_retailer') as fresh_cannabis_total_nomedical_retailer_value,

                            -- fresh_cannabis intra industry
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_ab_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_bc_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_mb_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nb_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nl_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_ns_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nt_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nu_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_on_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_pe_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_qc_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_sk_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_yt_nomedical_intra_industry_unpackaged,
                            SUM(T3.fresh_cannabis_weight) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_total_nomedical_intra_industry_unpackaged,
                            
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_ab_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_bc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_mb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nl_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_ns_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_nu_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_on_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_pe_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_qc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_sk_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_yt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as fresh_cannabis_total_nomedical_intra_industry_unpackaged_value,

                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged' AND T3.sku_type = 'packaged') as fresh_cannabis_ab_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_bc_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_mb_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nb_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nl_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_ns_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nt_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nu_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_on_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_pe_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_qc_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_sk_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_yt_nomedical_intra_industry_packaged,
                            SUM(T3.fresh_cannabis_qty) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_total_nomedical_intra_industry_packaged,
                            
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_ab_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_bc_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_mb_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nb_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nl_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_ns_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nt_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_nu_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_on_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_pe_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_qc_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_sk_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_yt_nomedical_intra_industry_packaged_value,
                            SUM(T3.fresh_cannabis_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as fresh_cannabis_total_nomedical_intra_industry_packaged_value,

                            -- dried cannabis distributor
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_ab_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as dried_cannabis_bc_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_mb_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nb_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nl_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as dried_cannabis_ns_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nt_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nu_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as dried_cannabis_on_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as dried_cannabis_pe_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as dried_cannabis_qc_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as dried_cannabis_sk_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as dried_cannabis_yt_nomedical_distributor,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_distributor') as dried_cannabis_total_nomedical_distributor,
                            
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_ab_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as dried_cannabis_bc_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_mb_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nb_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nl_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as dried_cannabis_ns_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nt_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as dried_cannabis_nu_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as dried_cannabis_on_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as dried_cannabis_pe_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as dried_cannabis_qc_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as dried_cannabis_sk_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as dried_cannabis_yt_nomedical_distributor_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_distributor') as dried_cannabis_total_nomedical_distributor_value,

                            -- dried cannabis recreational consumer
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_ab_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_bc_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_mb_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nb_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nl_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_ns_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nt_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nu_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_on_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_pe_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_qc_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_sk_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_yt_nomedical_recreational_consumer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_total_nomedical_recreational_consumer,
                            
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_ab_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_bc_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_mb_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nb_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nl_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_ns_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nt_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_nu_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_on_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_pe_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_qc_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_sk_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_yt_nomedical_recreational_consumer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as dried_cannabis_total_nomedical_recreational_consumer_value,

                            -- dried_cannabis retailer
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_ab_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as dried_cannabis_bc_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_mb_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nb_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nl_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as dried_cannabis_ns_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nt_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nu_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as dried_cannabis_on_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as dried_cannabis_pe_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as dried_cannabis_qc_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as dried_cannabis_sk_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as dried_cannabis_yt_nomedical_retailer,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.type = 'nonmedical_retailer') as dried_cannabis_total_nomedical_retailer,
                            
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_ab_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as dried_cannabis_bc_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_mb_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nb_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nl_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as dried_cannabis_ns_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nt_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as dried_cannabis_nu_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as dried_cannabis_on_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as dried_cannabis_pe_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as dried_cannabis_qc_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as dried_cannabis_sk_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as dried_cannabis_yt_nomedical_retailer_value,
                            SUM(T3.dried_cannabis_qty_value) FILTER (WHERE T3.type = 'nonmedical_retailer') as dried_cannabis_total_nomedical_retailer_value,

                            -- dried_cannabis intra industry
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_ab_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_bc_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_mb_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nb_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nl_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_ns_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nt_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nu_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_on_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_pe_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_qc_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_sk_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_yt_nomedical_intra_industry_unpackaged,
                            SUM(T3.dried_cannabis_weight) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_total_nomedical_intra_industry_unpackaged,
                            
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_ab_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_bc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_mb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nl_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_ns_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_nu_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_on_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_pe_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_qc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_sk_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_yt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as dried_cannabis_total_nomedical_intra_industry_unpackaged_value,

                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_ab_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_bc_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_mb_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nb_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nl_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_ns_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nt_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nu_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_on_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_pe_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_qc_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_sk_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_yt_nomedical_intra_industry_packaged,
                            SUM(T3.dried_cannabis_qty) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_total_nomedical_intra_industry_packaged,
                            
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_ab_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_bc_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_mb_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nb_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nl_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_ns_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nt_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_nu_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_on_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_pe_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_qc_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_sk_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_yt_nomedical_intra_industry_packaged_value,
                            SUM(T3.dried_cannabis_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as dried_cannabis_total_nomedical_intra_industry_packaged_value,

                            -- extracts distributor
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as extracts_ab_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as extracts_bc_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as extracts_mb_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as extracts_nb_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as extracts_nl_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as extracts_ns_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as extracts_nt_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as extracts_nu_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as extracts_on_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as extracts_pe_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as extracts_qc_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as extracts_sk_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as extracts_yt_nomedical_distributor,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.type = 'nonmedical_distributor') as extracts_total_nomedical_distributor,
                            
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_distributor') as extracts_ab_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_distributor') as extracts_bc_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_distributor') as extracts_mb_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_distributor') as extracts_nb_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_distributor') as extracts_nl_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_distributor') as extracts_ns_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_distributor') as extracts_nt_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_distributor') as extracts_nu_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_distributor') as extracts_on_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_distributor') as extracts_pe_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_distributor') as extracts_qc_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_distributor') as extracts_sk_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_distributor') as extracts_yt_nomedical_distributor_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.type = 'nonmedical_distributor') as extracts_total_nomedical_distributor_value,

                            -- dried cannabis recreational consumer
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_ab_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as extracts_bc_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_mb_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nb_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nl_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as extracts_ns_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nt_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nu_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as extracts_on_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as extracts_pe_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as extracts_qc_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as extracts_sk_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as extracts_yt_nomedical_recreational_consumer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as extracts_total_nomedical_recreational_consumer,

                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_ab_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_recreational_consumer') as extracts_bc_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_mb_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nb_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nl_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_recreational_consumer') as extracts_ns_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nt_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_recreational_consumer') as extracts_nu_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_recreational_consumer') as extracts_on_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_recreational_consumer') as extracts_pe_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_recreational_consumer') as extracts_qc_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_recreational_consumer') as extracts_sk_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_recreational_consumer') as extracts_yt_nomedical_recreational_consumer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.type = 'nonmedical_recreational_consumer') as extracts_total_nomedical_recreational_consumer_value,

                            -- extracts retailer
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as extracts_ab_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as extracts_bc_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as extracts_mb_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as extracts_nb_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as extracts_nl_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as extracts_ns_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as extracts_nt_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as extracts_nu_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as extracts_on_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as extracts_pe_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as extracts_qc_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as extracts_sk_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as extracts_yt_nomedical_retailer,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.type = 'nonmedical_retailer') as extracts_total_nomedical_retailer,

                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'nonmedical_retailer') as extracts_ab_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'nonmedical_retailer') as extracts_bc_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'nonmedical_retailer') as extracts_mb_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'nonmedical_retailer') as extracts_nb_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'nonmedical_retailer') as extracts_nl_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'nonmedical_retailer') as extracts_ns_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'nonmedical_retailer') as extracts_nt_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'nonmedical_retailer') as extracts_nu_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'nonmedical_retailer') as extracts_on_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'nonmedical_retailer') as extracts_pe_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'nonmedical_retailer') as extracts_qc_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'nonmedical_retailer') as extracts_sk_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'nonmedical_retailer') as extracts_yt_nomedical_retailer_value,
                            SUM(T3.extracts_qty_value) FILTER (WHERE T3.type = 'nonmedical_retailer') as extracts_total_nomedical_retailer_value,

                            -- extracts intra industry
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_ab_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_bc_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_mb_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nb_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nl_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_ns_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nt_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nu_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_on_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_pe_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_qc_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_sk_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_yt_nomedical_intra_industry_unpackaged,
                            SUM(T3.extracts_weight) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_total_nomedical_intra_industry_unpackaged,
                            
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_ab_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_bc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_mb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nb_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nl_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_ns_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_nu_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_on_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_pe_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_qc_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_sk_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_yt_nomedical_intra_industry_unpackaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'unpackaged') as extracts_total_nomedical_intra_industry_unpackaged_value,

                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_ab_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_bc_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_mb_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nb_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nl_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_ns_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nt_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nu_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_on_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_pe_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_qc_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_sk_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_yt_nomedical_intra_industry_packaged,
                            SUM(T3.extracts_qty) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_total_nomedical_intra_industry_packaged,
                            
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'AB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_ab_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'BC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_bc_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'MB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_mb_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NB' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nb_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NL' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nl_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NS' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_ns_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nt_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'NU' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_nu_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'ON' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_on_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'PE' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_pe_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'QC' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_qc_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'SK' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_sk_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.province = 'YT' AND T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_yt_nomedical_intra_industry_packaged_value,
                            SUM(T3.extracts_weight_value) FILTER (WHERE T3.type = 'intra_industry' AND T3.sku_type = 'packaged') as extracts_total_nomedical_intra_industry_packaged_value
                        FROM (
                                SELECT
                                    SUM(T2.seeds_qty) as seeds_qty,
                                    SUM(T2.plants_qty) as plants_qty,
                                    SUM(T2.fresh_cannabis_qty) as fresh_cannabis_qty,
                                    SUM(T2.dried_cannabis_qty) as dried_cannabis_qty,
                                    SUM(T2.extracts_qty) as extracts_qty,
                                    SUM(T2.fresh_cannabis_weight)/1000 as fresh_cannabis_weight,
                                    SUM(T2.dried_cannabis_weight)/1000 as dried_cannabis_weight,
                                    SUM(T2.extracts_weight)/1000 as extracts_weight,

                                    SUM(seeds_qty_value) AS seeds_qty_value,
                                    SUM(plants_qty_value) AS plants_qty_value,
                                    SUM(fresh_cannabis_qty_value) AS fresh_cannabis_qty_value,
                                    SUM(dried_cannabis_qty_value) AS dried_cannabis_qty_value,
                                    SUM(extracts_qty_value) AS extracts_qty_value,
                                    SUM(fresh_cannabis_weight_value) AS fresh_cannabis_weight_value,
                                    SUM(dried_cannabis_weight_value) AS dried_cannabis_weight_value,
                                    SUM(extracts_weight_value) AS extracts_weight_value,

                                    T2.province,
                                    T2.type,
                                    SUM(T2.total),
                                    T2.sku_type
                                FROM(
                                    SELECT T0.*,
                                            CASE
                                                WHEN T0.seeds_qty > 0 THEN T0.total
                                                ELSE 0
                                            END AS seeds_qty_value,
                                            CASE
                                                WHEN T0.plants_qty > 0 THEN T0.total
                                                ELSE 0
                                            END AS plants_qty_value,
                                            CASE
                                                WHEN T0.fresh_cannabis_qty > 0 THEN T0.total
                                                ELSE 0
                                            END AS fresh_cannabis_qty_value,
                                            CASE
                                                WHEN T0.dried_cannabis_qty > 0 THEN T0.total
                                                ELSE 0
                                            END AS dried_cannabis_qty_value,
                                            CASE
                                                WHEN T0.extracts_qty > 0 THEN T0.total
                                                ELSE 0
                                            END AS extracts_qty_value,
                                            CASE
                                                WHEN T0.fresh_cannabis_weight > 0 THEN T0.total
                                                ELSE 0
                                            END AS fresh_cannabis_weight_value,
                                            CASE
                                                WHEN T0.dried_cannabis_weight > 0 THEN T0.total
                                                ELSE 0
                                            END AS dried_cannabis_weight_value,
                                            CASE
                                                WHEN T0.extracts_weight> 0 THEN T0.total
                                                ELSE 0
                                            END AS extracts_weight_value	
                                    FROM (
                                        SELECT
                                            CASE
                                                WHEN (f).seeds > 0 THEN T1.quantity
                                                ELSE 0
                                                END AS seeds_qty,
                                            CASE
                                                WHEN (f).plants > 0 THEN T1.quantity
                                                ELSE 0
                                                END AS plants_qty,
                                            CASE
                                                WHEN (f).gwet > 0 THEN T1.quantity
                                                ELSE 0
                                                END AS fresh_cannabis_qty,
                                            CASE
                                                WHEN ((f).dry + (f).cured) > 0 THEN T1.quantity
                                                ELSE 0
                                                END AS dried_cannabis_qty,
                                            CASE
                                                WHEN ((f).crude + (f).distilled) > 0 THEN T1.quantity
                                                ELSE 0
                                            END AS extracts_qty,
                                            (f).gwet AS fresh_cannabis_weight,
                                            ((f).dry + (f).cured) AS dried_cannabis_weight,
                                            ((f).crude + (f).distilled) AS extracts_weight,
                                            T1.*,
                                            CASE
                                                WHEN T1.account_type = 'patient' THEN 'medical_consumer'
                                                WHEN T1.account_type = 'retailer' THEN 'nonmedical_retailer'
                                                WHEN T1.account_type = 'distributor' THEN 'nonmedical_distributor'                               
                                                WHEN T1.account_type in ('licence holder', 'researcher') THEN 'intra_industry'
                                                WHEN T1.account_type = 'recreational consumer' THEN 'nonmedical_recreational_consumer'
                                            END AS type
                                        FROM (
                                            SELECT f_serialize_stats_fields_accounts(oi.ordered_stats) AS f,
                                                oi.quantity, o.shipping_address->>'province' AS province,
                                                TRIM(REPLACE(CAST(crm.account_type AS VARCHAR), '"', '')) as account_type,
                                                oi.price + oi.provincial_tax + oi.shipping_value - oi.discount as total,
                                                o.id, 
                                                COALESCE(oi.sku_type, 'unpackaged') as sku_type
                                            FROM orders AS o
                                                INNER JOIN (
                                                    SELECT order_items.*, sku.data->>'type' as sku_type FROM order_items as order_items
                                                    INNER JOIN skus as sku ON order_items.sku_id = sku.id
                                                    LEFT JOIN (SELECT * FROM activities WHERE activities.name='order_cancel_item') AS activities ON order_items.id=CAST(activities.data->>'order_item_id' as INTEGER)
                                                    WHERE activities.data->>'order_item_id' IS null) AS oi ON oi.order_id = o.id
                                                INNER JOIN crm_accounts AS crm ON crm.id = o.crm_account_id
                                                INNER JOIN (
                                                        SELECT 
                                                            id,
                                                            shipping_address,
                                                            order_received_date,
                                                            ordered_stats,
                                                            organization_id,
                                                            order_type,
                                                            status
                                                        FROM orders WHERE status='approved' AND
                                                            organization_id = org_id AND
                                                            LEFT(data->>'payment_date',10) between initial_date and final_date
                                                            AND status = 'approved'

                                                        UNION ALL

                                                        SELECT
                                                            b.id,
                                                            b.shipping_address,
                                                            b.order_received_date,
                                                            b.ordered_stats,
                                                            b.organization_id,
                                                            b.order_type,
                                                            b.status
                                                        FROM (SELECT * FROM orders WHERE status='cancelled' AND LEFT(data->>'payment_date',10) between initial_date and final_date) AS b
                                                        INNER JOIN (SELECT *
                                                            from activities
                                                            WHERE
                                                                name = 'order_update_status' AND
                                                                data->>'to_status' = 'cancelled' AND
                                                                TO_CHAR(timestamp,'YYYY-MM-DD') > final_date
                                                                ) AS a ON b.id = CAST(a.data->>'order_id' AS INTEGER)
                                                ) AS order_status ON order_status.id = o.id

                                        ) AS T1
                                    ) AS T0
                                ) AS T2
                                GROUP BY T2.province, T2.type, T2.sku_type

                            ) AS T3
                        ) AS T4
                        WHERE id = report_id;

                            
                        END;$$;


ALTER FUNCTION public.f_hc_report_sales(report_id integer, initial_date character varying, final_date character varying, org_id integer) OWNER TO postgres;

--
-- TOC entry 294 (class 1255 OID 18995)
-- Name: f_inventories_latest_stats_stage(character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_inventories_latest_stats_stage(final_date character varying) RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, type character varying, variety character varying, data jsonb, stats jsonb, attributes jsonb, latest_quantity numeric, latest_unit character varying, latest_stage character varying)
    LANGUAGE plpgsql
    AS $$
                        BEGIN
                        /* this function gets the latest stats and stage of every inventory, returns the inventory properties + latest_quantity + latest_unit + latest_stage
                        we mainly need this to know what was the values in a certain period
                        say that we have an inventory that has 10 plants in august, but in september 10 plants is detroyed and its stats become 0, so if we want the report of aug
                        it will be not accurate based on its stats, so that's why we rely on the inventory_adjustment and update_stage activities to get the latest stats and stage in the period required. */
                        RETURN QUERY
                            SELECT 
                                inv.*,
                                CAST(act_stats.data->>'quantity' AS DECIMAL) AS latest_quantity,
                                CAST(act_stats.data->>'unit' AS VARCHAR) AS latest_unit,
                                CAST(act_stage.data->>'to_stage' AS VARCHAR) AS latest_stage
                            FROM inventories AS inv 
                            INNER JOIN (	  
                                SELECT 
                                    CAST(a_stats.data->>'inventory_id' AS bigint) AS inventory_id,
                                    MAX(a_stats.id) AS id
                                FROM activities AS a_stats
                                WHERE 
                                    a_stats.name = 'inventory_adjustment' AND
                                    CAST(a_stats.data->>'quantity' AS DECIMAL) >= 0	AND
                                    TO_CHAR(a_stats.timestamp,'YYYY-MM-DD') <= final_date
                                GROUP BY a_stats.data->>'inventory_id'
                            ) AS t2 ON t2.inventory_id = inv.id
                            INNER JOIN activities AS act_stats ON act_stats.id = t2.id
                            LEFT JOIN (	  
                            SELECT 
                                    CAST(a_stage.data->>'inventory_id' AS bigint) AS inventory_id,
                                    MAX(a_stage.id) AS id
                                FROM activities AS a_stage
                                WHERE 
                                a_stage.name = 'update_stage' AND
                                TO_CHAR(a_stage.timestamp,'YYYY-MM-DD') <= final_date
                                GROUP BY a_stage.data->>'inventory_id'
                                
                            ) AS t1 ON t1.inventory_id = inv.id
                            LEFT JOIN activities AS act_stage ON act_stage.id = t1.id;
                        
                        END;
                        $$;


ALTER FUNCTION public.f_inventories_latest_stats_stage(final_date character varying) OWNER TO postgres;

--
-- TOC entry 299 (class 1255 OID 18985)
-- Name: f_serialize_stats_fields(numeric, character varying, character varying, character varying, jsonb, jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT package_type character varying) RETURNS record
    LANGUAGE plpgsql
    AS $$
                        DECLARE
                            plants DECIMAL;
                            dry DECIMAL;
                            cured DECIMAL;
                            distilled DECIMAL;
                            crude DECIMAL;
                        BEGIN
                        --raise notice 'quantity: %', quantity;
                        
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
                        $$;


ALTER FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, type character varying, data jsonb, attributes jsonb, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT fresh_cannabis_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT package_type character varying) OWNER TO postgres;

--
-- TOC entry 289 (class 1255 OID 19362)
-- Name: f_serialize_stats_fields_accounts(jsonb); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_serialize_stats_fields_accounts(stats jsonb, OUT seeds numeric, OUT plants numeric, OUT gwet numeric, OUT dry numeric, OUT cured numeric, OUT distilled numeric, OUT crude numeric) RETURNS record
    LANGUAGE plpgsql
    AS $$
        BEGIN
            seeds := COALESCE(CAST(stats->>'seeds' AS DECIMAL),0);
            plants := COALESCE(CAST(stats->>'plants' AS DECIMAL),0);
            gwet := COALESCE(CAST(stats->>'g-wet' AS DECIMAL),0);
            plants := COALESCE(CAST(stats->>'plants' AS DECIMAL),0); 
            dry := COALESCE(CAST(stats->'g-dry'->>'dry' AS DECIMAL),0);
            cured := COALESCE(CAST(stats->'g-dry'->>'cured' AS DECIMAL),0);
            distilled := COALESCE(CAST(stats->'g-oil'->>'distilled' AS DECIMAL),0);
            crude := COALESCE(CAST(stats->'g-oil'->>'crude' AS DECIMAL),0);
        END;
        $$;


ALTER FUNCTION public.f_serialize_stats_fields_accounts(stats jsonb, OUT seeds numeric, OUT plants numeric, OUT gwet numeric, OUT dry numeric, OUT cured numeric, OUT distilled numeric, OUT crude numeric) OWNER TO postgres;

--
-- TOC entry 298 (class 1255 OID 19000)
-- Name: f_test_report_result(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.f_test_report_result(report_id integer) RETURNS text[]
    LANGUAGE plpgsql
    AS $$
            DECLARE 
                return_values TEXT[] := ARRAY[]::TEXT[];
                opening_value DECIMAL;
                adition_value DECIMAL;
                reduction_value DECIMAL;
                closing_value DECIMAL;
                text_value varchar;
                var1 DECIMAL;
                var2 DECIMAL;
                var3 DECIMAL;
            BEGIN

                -- unpackage seeds
                SELECT 
                    --opening
                    unpackaged_seed_opening_inventory,
                    --adition
                    (unpackaged_seed_produced+
                    unpackaged_seed_received_domestic+
                    unpackaged_seed_received_imported+
                    unpackaged_seed_received_returned),
                    --reduction
                    (unpackaged_seed_destroyed +
                    unpackaged_seed_shipped_analytical_testers +		
                    unpackaged_seed_processed),
                    --closing
                    unpackaged_seed_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                

                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Seeds calulation is incorrect';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;  
                
                
                -- unpackage vegetative plants
                SELECT 
                
                    --opening
                    unpackaged_vegetative_plants_opening_inventory,
                    --adition
                    (unpackaged_vegetative_plants_produced+
                    unpackaged_vegetative_plants_received_domestic+
                    unpackaged_vegetative_plants_received_imported+
                    unpackaged_vegetative_plants_received_returned+
					unpackaged_vegetative_plants_other_additions),
                    --reduction
                    (unpackaged_vegetative_plants_processed+
                    unpackaged_vegetative_plants_packaged_label+
                    unpackaged_vegetative_plants_destroyed+
                    unpackaged_vegetative_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_vegetative_cannabis_plants_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Vegetative Cannabis Plants calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;  
                
                
                -- unpackage whole plants
                SELECT 	
                    --opening
                    unpackaged_whole_cannabis_plants_opening_inventory,
                    --adition
                    (unpackaged_whole_cannabis_plants_produced+
                    unpackaged_whole_cannabis_plants_received_domestic+
                    unpackaged_whole_cannabis_plants_received_imported+
                    unpackaged_whole_cannabis_plants_received_returned),
                    --reduction
                    (unpackaged_whole_cannabis_plants_processed+
                    unpackaged_whole_cannabis_plants_packaged_label+
                    unpackaged_whole_cannabis_plants_destroyed+
                    unpackaged_whole_cannabis_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_whole_cannabis_plants_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Whole Cannabis Plants calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;  
                
                -- unpackaged fresh cannabis
                SELECT 	
                    --opening
                    unpackaged_fresh_cannabis_opening_inventory,
                    --adition
                    (unpackaged_fresh_cannabis_produced+
                    unpackaged_fresh_cannabis_received_domestic+
                    unpackaged_fresh_cannabis_received_imported+
                    unpackaged_fresh_cannabis_received_returned),
                    --reduction
                    (unpackaged_fresh_cannabis_processed+
                    unpackaged_fresh_cannabis_packaged_label+
                    unpackaged_fresh_cannabis_adjustment_loss+
                    unpackaged_fresh_cannabis_destroyed+
                    unpackaged_fresh_shipped_analytical_testers+
                    unpackaged_fresh_shipped_cultivators_processors),
                    --closing
                    unpackaged_fresh_cannabis_closing_inventory
                FROM 
                    health_canada_report
                --where id = report_id
                where id = 12
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Fresh Cannabis calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
                
                
                -- unpackaged dried cannabis
                SELECT 	
                    --opening
                    unpackaged_dried_cannabis_opening_inventory,
                    --adition
                    (unpackaged_dried_cannabis_produced+
                    unpackaged_dried_cannabis_received_domestic+
                    unpackaged_dried_cannabis_received_imported+
                    unpackaged_dried_cannabis_received_returned),
                    --reduction
                    (unpackaged_dried_cannabis_processed+
                    unpackaged_dried_cannabis_packaged_label+
                    unpackaged_dried_cannabis_adjustment_loss+
                    unpackaged_dried_cannabis_destroyed+
                    unpackaged_dried_shipped_analytical_testers+
                    unpackaged_dried_shipped_cultivators_processors),
                    --closing
                    unpackaged_dried_cannabis_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Dried Cannabis calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
                
                
                -- unpackaged extracts cannabis
                SELECT 	
                    --opening
                    unpackaged_extracts_opening_inventory,
                    --adition
                    (unpackaged_extracts_produced+
                    unpackaged_extracts_received_domestic+
                    unpackaged_extracts_received_imported+
                    unpackaged_extracts_received_returned),
                    --reduction
                    (unpackaged_extracts_packaged_label+
                    unpackaged_extracts_adjustment_loss+
                    unpackaged_extracts_destroyed+
                    unpackaged_extracts_shipped_analytical_testers+
                    unpackaged_extracts_shipped_cultivators_processors),
                    --closing
                    unpackaged_extracts_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Unpackaged Extracts Injested (oil) calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                
                
                -- Packaged seeds
                SELECT 	
                    --opening
                    packaged_seed_opening_inventory,
                    --adition
                    (packaged_seed_received_domestic+
                    packaged_seed_received_returned+
                    packaged_seed_quantity_packaged),
                    --reduction
                    (packaged_seed_destroyed+
                    packaged_seed_shipped_domestic),
                    --closing
                    packaged_seed_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Pacakged Seeds calulation is incorrect. Closing inventory should be'||cast(closing_value as varchar);
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                
                
                
                -- Packaged vegetative plants
                SELECT 	
                    --opening
                    packaged_vegetative_plants_opening_inventory,
                    --adition
                    (packaged_vegetative_plants_received_domestic+
                    packaged_vegetative_plants_received_returned+
                    packaged_vegetative_plants_quantity_packaged),
                    --reduction
                    (packaged_vegetative_plants_destroyed+
                    packaged_vegetative_plants_shipped_domestic),
                    --closing
                    packaged_vegetative_cannabis_plants_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Packaged Vegetative Canabbis Plants calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                
                -- Packaged fresh cannabis
                SELECT 	
                    --opening
                    packaged_fresh_cannabis_opening_inventory,
                    --adition
                    (packaged_fresh_cannabis_received_domestic+
                    packaged_fresh_cannabis_received_returned+
                    packaged_fresh_cannabis_quantity_packaged),
                    --reduction
                    (packaged_fresh_cannabis_destroyed+
                    packaged_fresh_cannabis_shipped_domestic),
                    --closing
                    packaged_fresh_cannabis_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Packaged Fresh Cannabis calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                
                -- Packaged dried cannabis
                SELECT 	
                    --opening
                    packaged_dried_cannabis_opening_inventory,
                    --adition
                    (packaged_dried_cannabis_received_domestic+
                    packaged_dried_cannabis_received_returned+
                    packaged_dried_cannabis_quantity_packaged),
                    --reduction
                    (packaged_dried_cannabis_destroyed+
                    packaged_dried_cannabis_shipped_domestic),
                    --closing
                    packaged_dried_cannabis_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Packaged Dried Cannabis calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                
                
                -- Packaged extracts cannabis
                SELECT 	
                    --opening
                    packaged_extracts_opening_inventory,
                    --adition
                    (packaged_extracts_received_domestic+
                    packaged_extracts_received_returned+
                    packaged_extracts_quantity_packaged),
                    --reduction
                    (packaged_extracts_destroyed+
                    packaged_extracts_shipped_domestic),
                    --closing
                    packaged_extracts_closing_inventory
                FROM 
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
                
                IF NOT (round(opening_value,3) +round(adition_value,3)) - round(reduction_value,3) = round(closing_value,3) THEN
                    text_value := 'Packaged Extracts Injested (oil) calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF; 
                


            /*

            drop function f_test_result_report(integer)

            select f_hc_report('04', '2020', 1, 13)

            select r.unpackaged_fresh_shipped_cultivators_processors from health_canada_report r

            select f_test_report_result(12)

            
             SELECT 	
                    --opening
                    unpackaged_fresh_cannabis_opening_inventory,
                    --adition
                    (unpackaged_fresh_cannabis_produced+
                    unpackaged_fresh_cannabis_received_domestic+
                    unpackaged_fresh_cannabis_received_imported+
                    unpackaged_fresh_cannabis_received_returned),
                    --reduction
                    (unpackaged_fresh_cannabis_processed+
                    unpackaged_fresh_cannabis_packaged_label+
                    unpackaged_fresh_cannabis_adjustment_loss+
                    unpackaged_fresh_cannabis_destroyed+
                    unpackaged_fresh_shipped_analytical_testers),
                    --closing
                    unpackaged_fresh_cannabis_closing_inventory
                FROM 
                    health_canada_report
                where id = 12
                
            */
                
                RETURN return_values;
            END ;

            $$;


ALTER FUNCTION public.f_test_report_result(report_id integer) OWNER TO postgres;

--
-- TOC entry 274 (class 1255 OID 16389)
-- Name: jsonb_merge_data(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.jsonb_merge_data() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
NEW.data = coalesce(OLD.data || NEW.data);
RETURN NEW;
END
$$;


ALTER FUNCTION public.jsonb_merge_data() OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 186 (class 1259 OID 16390)
-- Name: activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activities (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb NOT NULL
);


ALTER TABLE public.activities OWNER TO postgres;

--
-- TOC entry 187 (class 1259 OID 16397)
-- Name: activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activities_id_seq OWNER TO postgres;

--
-- TOC entry 3660 (class 0 OID 0)
-- Dependencies: 187
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activities_id_seq OWNED BY public.activities.id;


--
-- TOC entry 188 (class 1259 OID 16399)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: migration_runner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO migration_runner;

--
-- TOC entry 266 (class 1259 OID 19944)
-- Name: audit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_id_seq OWNER TO postgres;

--
-- TOC entry 268 (class 1259 OID 19948)
-- Name: audit; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit (
    id bigint DEFAULT nextval('public.audit_id_seq'::regclass) NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    requested_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    date_request timestamp with time zone NOT NULL,
    type character varying NOT NULL,
    description character varying NOT NULL,
    service_desk_ticket jsonb DEFAULT '{}'::jsonb,
    data jsonb DEFAULT '{"status": "completed"}'::jsonb
);


ALTER TABLE public.audit OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 19946)
-- Name: audit_detail_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_detail_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_detail_id_seq OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 19975)
-- Name: audit_detail; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_detail (
    id bigint DEFAULT nextval('public.audit_detail_id_seq'::regclass) NOT NULL,
    organization_id integer NOT NULL,
    audit_id integer NOT NULL,
    type character varying NOT NULL,
    table_name character varying NOT NULL,
    "where" character varying NOT NULL,
    new_values jsonb NOT NULL,
    old_values jsonb NOT NULL,
    rows_affected integer NOT NULL
);


ALTER TABLE public.audit_detail OWNER TO postgres;

--
-- TOC entry 189 (class 1259 OID 16402)
-- Name: capa_actions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.capa_actions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.capa_actions_id_seq OWNER TO postgres;

--
-- TOC entry 190 (class 1259 OID 16404)
-- Name: capa_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.capa_actions (
    id bigint DEFAULT nextval('public.capa_actions_id_seq'::regclass) NOT NULL,
    capa_id bigint NOT NULL,
    description character varying NOT NULL,
    comment character varying,
    status character varying DEFAULT 'awaiting approval'::character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    staff_assigned character varying,
    due_date timestamp with time zone,
    result character varying
);


ALTER TABLE public.capa_actions OWNER TO postgres;

--
-- TOC entry 191 (class 1259 OID 16414)
-- Name: capa_links_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.capa_links_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.capa_links_id_seq OWNER TO postgres;

--
-- TOC entry 192 (class 1259 OID 16416)
-- Name: capa_links; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.capa_links (
    id bigint DEFAULT nextval('public.capa_links_id_seq'::regclass) NOT NULL,
    capa_id bigint NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    status character varying DEFAULT 'enabled'::character varying NOT NULL,
    link_id bigint NOT NULL,
    link_type character varying NOT NULL
);


ALTER TABLE public.capa_links OWNER TO postgres;

--
-- TOC entry 193 (class 1259 OID 16426)
-- Name: capas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.capas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.capas_id_seq OWNER TO postgres;

--
-- TOC entry 194 (class 1259 OID 16428)
-- Name: capas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.capas (
    id bigint DEFAULT nextval('public.capas_id_seq'::regclass) NOT NULL,
    description character varying NOT NULL,
    status character varying DEFAULT 'reported'::character varying NOT NULL,
    actions_approved integer DEFAULT 0 NOT NULL,
    actions_closed integer DEFAULT 0 NOT NULL,
    actions_total integer DEFAULT 0 NOT NULL,
    reported_by character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.capas OWNER TO postgres;

--
-- TOC entry 195 (class 1259 OID 16439)
-- Name: consumable_classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consumable_classes (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    type character varying NOT NULL,
    subtype character varying,
    unit character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    status character varying NOT NULL
);


ALTER TABLE public.consumable_classes OWNER TO postgres;

--
-- TOC entry 196 (class 1259 OID 16447)
-- Name: consumable_classes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.consumable_classes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.consumable_classes_id_seq OWNER TO postgres;

--
-- TOC entry 3673 (class 0 OID 0)
-- Dependencies: 196
-- Name: consumable_classes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.consumable_classes_id_seq OWNED BY public.consumable_classes.id;


--
-- TOC entry 197 (class 1259 OID 16449)
-- Name: consumable_lots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.consumable_lots (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    status character varying NOT NULL,
    expiration_date timestamp with time zone,
    class_id integer NOT NULL,
    current_qty numeric NOT NULL,
    initial_qty numeric NOT NULL,
    unit character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.consumable_lots OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 16457)
-- Name: consumable_lots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.consumable_lots_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.consumable_lots_id_seq OWNER TO postgres;

--
-- TOC entry 3676 (class 0 OID 0)
-- Dependencies: 198
-- Name: consumable_lots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.consumable_lots_id_seq OWNED BY public.consumable_lots.id;


--
-- TOC entry 199 (class 1259 OID 16459)
-- Name: crm_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crm_accounts (
    id integer NOT NULL,
    created_by integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    name character varying NOT NULL,
    organization_id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL,
    account_type character varying
);


ALTER TABLE public.crm_accounts OWNER TO postgres;

--
-- TOC entry 200 (class 1259 OID 16469)
-- Name: crm_account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.crm_account_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.crm_account_id_seq OWNER TO postgres;

--
-- TOC entry 3679 (class 0 OID 0)
-- Dependencies: 200
-- Name: crm_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.crm_account_id_seq OWNED BY public.crm_accounts.id;


--
-- TOC entry 239 (class 1259 OID 18628)
-- Name: sop_departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sop_departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sop_departments_id_seq OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 18630)
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id bigint DEFAULT nextval('public.sop_departments_id_seq'::regclass) NOT NULL,
    name character varying NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    status character varying DEFAULT 'enabled'::character varying NOT NULL
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 19814)
-- Name: deviation_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deviation_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deviation_reports_id_seq OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 19816)
-- Name: deviation_reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deviation_reports (
    id bigint DEFAULT nextval('public.deviation_reports_id_seq'::regclass) NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    status character varying NOT NULL,
    effective_date timestamp with time zone NOT NULL,
    relates_to character varying[] NOT NULL,
    potential_impact character varying[] NOT NULL,
    impact_details text,
    planned_reason text,
    additional_details text,
    investigation_details text,
    root_cause text,
    data jsonb DEFAULT '{}'::jsonb,
    attributes jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.deviation_reports OWNER TO postgres;

--
-- TOC entry 258 (class 1259 OID 19839)
-- Name: deviation_reports_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deviation_reports_assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deviation_reports_assignments_id_seq OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 19841)
-- Name: deviation_reports_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deviation_reports_assignments (
    id bigint DEFAULT nextval('public.deviation_reports_assignments_id_seq'::regclass) NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    deviation_reports_id bigint NOT NULL,
    user_id bigint NOT NULL,
    type character varying NOT NULL,
    status character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.deviation_reports_assignments OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 16471)
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    external_id character varying,
    stats jsonb DEFAULT '{}'::jsonb NOT NULL,
    sub_type character varying,
    room character varying,
    default_unit_type character varying,
    attributes jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 16480)
-- Name: equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equipment_id_seq OWNER TO postgres;

--
-- TOC entry 3688 (class 0 OID 0)
-- Dependencies: 202
-- Name: equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_id_seq OWNED BY public.equipment.id;


--
-- TOC entry 252 (class 1259 OID 18854)
-- Name: health_canada_report_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.health_canada_report_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 99999999999999999
    CACHE 1;


ALTER TABLE public.health_canada_report_seq OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 18856)
-- Name: health_canada_report; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.health_canada_report (
    id bigint DEFAULT nextval('public.health_canada_report_seq'::regclass) NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    report_period_year character varying NOT NULL,
    report_period_month character varying NOT NULL,
    province character varying,
    type character varying,
    company_name character varying,
    site_id character varying,
    city character varying,
    postal_code character varying,
    license_id character varying,
    total_buildings_area numeric DEFAULT 0,
    licensed_growing_area numeric DEFAULT 0,
    licensed_processing_area numeric DEFAULT 0,
    licensed_outdoor_growing_area numeric DEFAULT 0,
    unpackaged_seed_opening_inventory numeric DEFAULT 0,
    unpackaged_vegetative_plants_opening_inventory numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_opening_inventory numeric DEFAULT 0,
    unpackaged_fresh_cannabis_opening_inventory numeric DEFAULT 0,
    unpackaged_dried_cannabis_opening_inventory numeric DEFAULT 0,
    unpackaged_extracts_opening_inventory numeric DEFAULT 0,
    packaged_seed_opening_inventory numeric DEFAULT 0,
    packaged_vegetative_plants_opening_inventory numeric DEFAULT 0,
    packaged_fresh_cannabis_opening_inventory numeric DEFAULT 0,
    packaged_dried_cannabis_opening_inventory numeric DEFAULT 0,
    packaged_extracts_opening_inventory numeric DEFAULT 0,
    unpackaged_seed_closing_inventory numeric DEFAULT 0,
    unpackaged_vegetative_cannabis_plants_closing_inventory numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_closing_inventory numeric DEFAULT 0,
    unpackaged_fresh_cannabis_closing_inventory numeric DEFAULT 0,
    unpackaged_dried_cannabis_closing_inventory numeric DEFAULT 0,
    unpackaged_extracts_closing_inventory numeric DEFAULT 0,
    packaged_seed_closing_inventory numeric DEFAULT 0,
    packaged_vegetative_cannabis_plants_closing_inventory numeric DEFAULT 0,
    packaged_fresh_cannabis_closing_inventory numeric DEFAULT 0,
    packaged_dried_cannabis_closing_inventory numeric DEFAULT 0,
    packaged_extracts_closing_inventory numeric DEFAULT 0,
    packaged_seed_closing_inventory_weight numeric DEFAULT 0,
    packaged_fresh_cannabis_closing_inventory_weight numeric DEFAULT 0,
    packaged_dried_cannabis_closing_inventory_weight numeric DEFAULT 0,
    packaged_extracts_closing_inventory_weight numeric DEFAULT 0,
    unpackaged_seed_received_domestic numeric DEFAULT 0,
    unpackaged_vegetative_plants_received_domestic numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_received_domestic numeric DEFAULT 0,
    unpackaged_fresh_cannabis_received_domestic numeric DEFAULT 0,
    unpackaged_dried_cannabis_received_domestic numeric DEFAULT 0,
    unpackaged_extracts_received_domestic numeric DEFAULT 0,
    unpackaged_seed_received_imported numeric DEFAULT 0,
    unpackaged_vegetative_plants_received_imported numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_received_imported numeric DEFAULT 0,
    unpackaged_fresh_cannabis_received_imported numeric DEFAULT 0,
    unpackaged_dried_cannabis_received_imported numeric DEFAULT 0,
    unpackaged_extracts_received_imported numeric DEFAULT 0,
    unpackaged_seed_received_returned numeric DEFAULT 0,
    unpackaged_vegetative_plants_received_returned numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_received_returned numeric DEFAULT 0,
    unpackaged_fresh_cannabis_received_returned numeric DEFAULT 0,
    unpackaged_dried_cannabis_received_returned numeric DEFAULT 0,
    unpackaged_extracts_received_returned numeric DEFAULT 0,
    packaged_seed_received_domestic numeric DEFAULT 0,
    packaged_vegetative_plants_received_domestic numeric DEFAULT 0,
    packaged_fresh_cannabis_received_domestic numeric DEFAULT 0,
    packaged_dried_cannabis_received_domestic numeric DEFAULT 0,
    packaged_extracts_received_domestic numeric DEFAULT 0,
    packaged_seed_received_returned numeric DEFAULT 0,
    packaged_vegetative_plants_received_returned numeric DEFAULT 0,
    packaged_fresh_cannabis_received_returned numeric DEFAULT 0,
    packaged_dried_cannabis_received_returned numeric DEFAULT 0,
    packaged_extracts_received_returned numeric DEFAULT 0,
    unpackaged_seed_packaged_label numeric DEFAULT 0,
    unpackaged_vegetative_plants_packaged_label numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_packaged_label numeric DEFAULT 0,
    unpackaged_fresh_cannabis_packaged_label numeric DEFAULT 0,
    unpackaged_dried_cannabis_packaged_label numeric DEFAULT 0,
    unpackaged_extracts_packaged_label numeric DEFAULT 0,
    packaged_seed_quantity_packaged numeric DEFAULT 0,
    packaged_vegetative_plants_quantity_packaged numeric DEFAULT 0,
    packaged_fresh_cannabis_quantity_packaged numeric DEFAULT 0,
    packaged_dried_cannabis_quantity_packaged numeric DEFAULT 0,
    packaged_extracts_quantity_packaged numeric DEFAULT 0,
    unpackaged_vegetative_plants_adjustment_loss numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_adjustment_loss numeric DEFAULT 0,
    unpackaged_fresh_cannabis_adjustment_loss numeric DEFAULT 0,
    unpackaged_dried_cannabis_adjustment_loss numeric DEFAULT 0,
    unpackaged_extracts_adjustment_loss numeric DEFAULT 0,
    unpackaged_seed_destroyed numeric DEFAULT 0,
    unpackaged_vegetative_plants_destroyed numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_destroyed numeric DEFAULT 0,
    unpackaged_fresh_cannabis_destroyed numeric DEFAULT 0,
    unpackaged_dried_cannabis_destroyed numeric DEFAULT 0,
    unpackaged_extracts_destroyed numeric DEFAULT 0,
    packaged_seed_destroyed numeric DEFAULT 0,
    packaged_vegetative_plants_destroyed numeric DEFAULT 0,
    packaged_fresh_cannabis_destroyed numeric DEFAULT 0,
    packaged_dried_cannabis_destroyed numeric DEFAULT 0,
    packaged_extracts_destroyed numeric DEFAULT 0,
    unpackaged_seed_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_vegetative_plants_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_fresh_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_dried_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_extracts_shipped_analytical_testers numeric DEFAULT 0,
    unpackaged_seed_produced numeric DEFAULT 0,
    unpackaged_vegetative_plants_produced numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_produced numeric DEFAULT 0,
    unpackaged_fresh_cannabis_produced numeric DEFAULT 0,
    unpackaged_dried_cannabis_produced numeric DEFAULT 0,
    unpackaged_extracts_produced numeric DEFAULT 0,
    unpackaged_seed_processed numeric DEFAULT 0,
    unpackaged_vegetative_plants_processed numeric DEFAULT 0,
    unpackaged_whole_cannabis_plants_processed numeric DEFAULT 0,
    unpackaged_fresh_cannabis_processed numeric DEFAULT 0,
    unpackaged_dried_cannabis_processed numeric DEFAULT 0,
    packaged_seed_shipped_domestic numeric DEFAULT 0,
    packaged_vegetative_plants_shipped_domestic numeric DEFAULT 0,
    packaged_fresh_cannabis_shipped_domestic numeric DEFAULT 0,
    packaged_dried_cannabis_shipped_domestic numeric DEFAULT 0,
    packaged_extracts_shipped_domestic numeric DEFAULT 0,
    unpackaged_vegetative_plants_other_additions numeric DEFAULT 0,
    ab_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    bc_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    mb_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    nb_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    nl_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    ns_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    nt_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    nu_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    on_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    pe_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    qc_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    sk_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    yt_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    total_unpackaged_intra_industry_seeds_weight numeric DEFAULT 0,
    ab_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    bc_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    mb_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nb_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nl_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    ns_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nt_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nu_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    on_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    pe_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    qc_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    sk_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    yt_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    total_unpackaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    ab_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    bc_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    mb_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    nb_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    nl_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    ns_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    nt_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    nu_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    on_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    pe_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    qc_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    sk_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    yt_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    total_unpackaged_intra_industry_fresh_cannabis_weight numeric DEFAULT 0,
    ab_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    bc_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    mb_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    nb_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    nl_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    ns_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    nt_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    nu_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    on_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    pe_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    qc_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    sk_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    yt_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    total_unpackaged_intra_industry_dried_cannabis_weight numeric DEFAULT 0,
    ab_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    bc_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    mb_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    nb_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    nl_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    ns_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    nt_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    nu_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    on_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    pe_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    qc_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    sk_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    yt_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    total_unpackaged_intra_industry_extracts_weight numeric DEFAULT 0,
    ab_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    bc_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    mb_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    nb_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    nl_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    ns_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    nt_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    nu_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    on_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    pe_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    qc_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    sk_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    yt_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    total_packaged_intra_industry_seeds_amount numeric DEFAULT 0,
    ab_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    bc_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    mb_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nb_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nl_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    ns_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nt_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    nu_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    on_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    pe_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    qc_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    sk_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    yt_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    total_packaged_intra_industry_veg_plants_amount numeric DEFAULT 0,
    ab_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    bc_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    mb_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    nb_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    nl_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    ns_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    nt_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    nu_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    on_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    pe_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    qc_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    sk_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    yt_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    total_packaged_intra_industry_fresh_cannabis_amount numeric DEFAULT 0,
    ab_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    bc_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    mb_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    nb_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    nl_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    ns_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    nt_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    nu_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    on_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    pe_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    qc_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    sk_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    yt_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    total_packaged_intra_industry_dried_cannabis_amount numeric DEFAULT 0,
    ab_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    bc_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    mb_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    nb_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    nl_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    ns_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    nt_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    nu_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    on_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    pe_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    qc_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    sk_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    yt_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    total_packaged_intra_industry_extracts_amount numeric DEFAULT 0,
    ab_retailer_seeds_amount numeric DEFAULT 0,
    bc_retailer_seeds_amount numeric DEFAULT 0,
    mb_retailer_seeds_amount numeric DEFAULT 0,
    nb_retailer_seeds_amount numeric DEFAULT 0,
    nl_retailer_seeds_amount numeric DEFAULT 0,
    ns_retailer_seeds_amount numeric DEFAULT 0,
    nt_retailer_seeds_amount numeric DEFAULT 0,
    nu_retailer_seeds_amount numeric DEFAULT 0,
    on_retailer_seeds_amount numeric DEFAULT 0,
    pe_retailer_seeds_amount numeric DEFAULT 0,
    qc_retailer_seeds_amount numeric DEFAULT 0,
    sk_retailer_seeds_amount numeric DEFAULT 0,
    yt_retailer_seeds_amount numeric DEFAULT 0,
    total_retailer_seeds_amount numeric DEFAULT 0,
    ab_retailer_veg_plants_amount numeric DEFAULT 0,
    bc_retailer_veg_plants_amount numeric DEFAULT 0,
    mb_retailer_veg_plants_amount numeric DEFAULT 0,
    nb_retailer_veg_plants_amount numeric DEFAULT 0,
    nl_retailer_veg_plants_amount numeric DEFAULT 0,
    ns_retailer_veg_plants_amount numeric DEFAULT 0,
    nt_retailer_veg_plants_amount numeric DEFAULT 0,
    nu_retailer_veg_plants_amount numeric DEFAULT 0,
    on_retailer_veg_plants_amount numeric DEFAULT 0,
    pe_retailer_veg_plants_amount numeric DEFAULT 0,
    qc_retailer_veg_plants_amount numeric DEFAULT 0,
    sk_retailer_veg_plants_amount numeric DEFAULT 0,
    yt_retailer_veg_plants_amount numeric DEFAULT 0,
    total_retailer_veg_plants_amount numeric DEFAULT 0,
    ab_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    bc_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    mb_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    nb_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    nl_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    ns_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    nt_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    nu_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    on_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    pe_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    qc_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    sk_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    yt_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    total_retailer_fresh_cannabis_amount numeric DEFAULT 0,
    ab_retailer_dried_cannabis_amount numeric DEFAULT 0,
    bc_retailer_dried_cannabis_amount numeric DEFAULT 0,
    mb_retailer_dried_cannabis_amount numeric DEFAULT 0,
    nb_retailer_dried_cannabis_amount numeric DEFAULT 0,
    nl_retailer_dried_cannabis_amount numeric DEFAULT 0,
    ns_retailer_dried_cannabis_amount numeric DEFAULT 0,
    nt_retailer_dried_cannabis_amount numeric DEFAULT 0,
    nu_retailer_dried_cannabis_amount numeric DEFAULT 0,
    on_retailer_dried_cannabis_amount numeric DEFAULT 0,
    pe_retailer_dried_cannabis_amount numeric DEFAULT 0,
    qc_retailer_dried_cannabis_amount numeric DEFAULT 0,
    sk_retailer_dried_cannabis_amount numeric DEFAULT 0,
    yt_retailer_dried_cannabis_amount numeric DEFAULT 0,
    total_retailer_dried_cannabis_amount numeric DEFAULT 0,
    ab_retailer_extracts_amount numeric DEFAULT 0,
    bc_retailer_extracts_amount numeric DEFAULT 0,
    mb_retailer_extracts_amount numeric DEFAULT 0,
    nb_retailer_extracts_amount numeric DEFAULT 0,
    nl_retailer_extracts_amount numeric DEFAULT 0,
    ns_retailer_extracts_amount numeric DEFAULT 0,
    nt_retailer_extracts_amount numeric DEFAULT 0,
    nu_retailer_extracts_amount numeric DEFAULT 0,
    on_retailer_extracts_amount numeric DEFAULT 0,
    pe_retailer_extracts_amount numeric DEFAULT 0,
    qc_retailer_extracts_amount numeric DEFAULT 0,
    sk_retailer_extracts_amount numeric DEFAULT 0,
    yt_retailer_extracts_amount numeric DEFAULT 0,
    total_retailer_extracts_amount numeric DEFAULT 0,
    ab_distributor_seeds_amount numeric DEFAULT 0,
    bc_distributor_seeds_amount numeric DEFAULT 0,
    mb_distributor_seeds_amount numeric DEFAULT 0,
    nb_distributor_seeds_amount numeric DEFAULT 0,
    nl_distributor_seeds_amount numeric DEFAULT 0,
    ns_distributor_seeds_amount numeric DEFAULT 0,
    nt_distributor_seeds_amount numeric DEFAULT 0,
    nu_distributor_seeds_amount numeric DEFAULT 0,
    on_distributor_seeds_amount numeric DEFAULT 0,
    pe_distributor_seeds_amount numeric DEFAULT 0,
    qc_distributor_seeds_amount numeric DEFAULT 0,
    sk_distributor_seeds_amount numeric DEFAULT 0,
    yt_distributor_seeds_amount numeric DEFAULT 0,
    total_distributor_seeds_amount numeric DEFAULT 0,
    ab_distributor_veg_plants_amount numeric DEFAULT 0,
    bc_distributor_veg_plants_amount numeric DEFAULT 0,
    mb_distributor_veg_plants_amount numeric DEFAULT 0,
    nb_distributor_veg_plants_amount numeric DEFAULT 0,
    nl_distributor_veg_plants_amount numeric DEFAULT 0,
    ns_distributor_veg_plants_amount numeric DEFAULT 0,
    nt_distributor_veg_plants_amount numeric DEFAULT 0,
    nu_distributor_veg_plants_amount numeric DEFAULT 0,
    on_distributor_veg_plants_amount numeric DEFAULT 0,
    pe_distributor_veg_plants_amount numeric DEFAULT 0,
    qc_distributor_veg_plants_amount numeric DEFAULT 0,
    sk_distributor_veg_plants_amount numeric DEFAULT 0,
    yt_distributor_veg_plants_amount numeric DEFAULT 0,
    total_distributor_veg_plants_amount numeric DEFAULT 0,
    ab_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    bc_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    mb_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    nb_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    nl_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    ns_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    nt_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    nu_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    on_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    pe_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    qc_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    sk_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    yt_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    total_distributor_fresh_cannabis_amount numeric DEFAULT 0,
    ab_distributor_dried_cannabis_amount numeric DEFAULT 0,
    bc_distributor_dried_cannabis_amount numeric DEFAULT 0,
    mb_distributor_dried_cannabis_amount numeric DEFAULT 0,
    nb_distributor_dried_cannabis_amount numeric DEFAULT 0,
    nl_distributor_dried_cannabis_amount numeric DEFAULT 0,
    ns_distributor_dried_cannabis_amount numeric DEFAULT 0,
    nt_distributor_dried_cannabis_amount numeric DEFAULT 0,
    nu_distributor_dried_cannabis_amount numeric DEFAULT 0,
    on_distributor_dried_cannabis_amount numeric DEFAULT 0,
    pe_distributor_dried_cannabis_amount numeric DEFAULT 0,
    qc_distributor_dried_cannabis_amount numeric DEFAULT 0,
    sk_distributor_dried_cannabis_amount numeric DEFAULT 0,
    yt_distributor_dried_cannabis_amount numeric DEFAULT 0,
    total_distributor_dried_cannabis_amount numeric DEFAULT 0,
    ab_distributor_extracts_amount numeric DEFAULT 0,
    bc_distributor_extracts_amount numeric DEFAULT 0,
    mb_distributor_extracts_amount numeric DEFAULT 0,
    nb_distributor_extracts_amount numeric DEFAULT 0,
    nl_distributor_extracts_amount numeric DEFAULT 0,
    ns_distributor_extracts_amount numeric DEFAULT 0,
    nt_distributor_extracts_amount numeric DEFAULT 0,
    nu_distributor_extracts_amount numeric DEFAULT 0,
    on_distributor_extracts_amount numeric DEFAULT 0,
    pe_distributor_extracts_amount numeric DEFAULT 0,
    qc_distributor_extracts_amount numeric DEFAULT 0,
    sk_distributor_extracts_amount numeric DEFAULT 0,
    yt_distributor_extracts_amount numeric DEFAULT 0,
    total_distributor_extracts_amount numeric DEFAULT 0,
    ab_recreational_consumer_seeds_amount numeric DEFAULT 0,
    bc_recreational_consumer_seeds_amount numeric DEFAULT 0,
    mb_recreational_consumer_seeds_amount numeric DEFAULT 0,
    nb_recreational_consumer_seeds_amount numeric DEFAULT 0,
    nl_recreational_consumer_seeds_amount numeric DEFAULT 0,
    ns_recreational_consumer_seeds_amount numeric DEFAULT 0,
    nt_recreational_consumer_seeds_amount numeric DEFAULT 0,
    nu_recreational_consumer_seeds_amount numeric DEFAULT 0,
    on_recreational_consumer_seeds_amount numeric DEFAULT 0,
    pe_recreational_consumer_seeds_amount numeric DEFAULT 0,
    qc_recreational_consumer_seeds_amount numeric DEFAULT 0,
    sk_recreational_consumer_seeds_amount numeric DEFAULT 0,
    yt_recreational_consumer_seeds_amount numeric DEFAULT 0,
    total_recreational_consumer_seeds_amount numeric DEFAULT 0,
    ab_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    bc_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    mb_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    nb_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    nl_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    ns_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    nt_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    nu_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    on_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    pe_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    qc_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    sk_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    yt_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    total_recreational_consumer_veg_plants_amount numeric DEFAULT 0,
    ab_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    bc_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    mb_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    nb_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    nl_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    ns_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    nt_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    nu_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    on_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    pe_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    qc_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    sk_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    yt_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    total_recreational_consumer_fresh_cannabis_amount numeric DEFAULT 0,
    ab_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    bc_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    mb_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    nb_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    nl_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    ns_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    nt_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    nu_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    on_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    pe_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    qc_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    sk_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    yt_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    total_recreational_consumer_dried_cannabis_amount numeric DEFAULT 0,
    ab_recreational_consumer_extracts_amount numeric DEFAULT 0,
    bc_recreational_consumer_extracts_amount numeric DEFAULT 0,
    mb_recreational_consumer_extracts_amount numeric DEFAULT 0,
    nb_recreational_consumer_extracts_amount numeric DEFAULT 0,
    nl_recreational_consumer_extracts_amount numeric DEFAULT 0,
    ns_recreational_consumer_extracts_amount numeric DEFAULT 0,
    nt_recreational_consumer_extracts_amount numeric DEFAULT 0,
    nu_recreational_consumer_extracts_amount numeric DEFAULT 0,
    on_recreational_consumer_extracts_amount numeric DEFAULT 0,
    pe_recreational_consumer_extracts_amount numeric DEFAULT 0,
    qc_recreational_consumer_extracts_amount numeric DEFAULT 0,
    sk_recreational_consumer_extracts_amount numeric DEFAULT 0,
    yt_recreational_consumer_extracts_amount numeric DEFAULT 0,
    total_recreational_consumer_extracts_amount numeric DEFAULT 0,
    ab_distributor_seeds_value numeric(14,2) DEFAULT 0,
    bc_distributor_seeds_value numeric(14,2) DEFAULT 0,
    mb_distributor_seeds_value numeric(14,2) DEFAULT 0,
    nb_distributor_seeds_value numeric(14,2) DEFAULT 0,
    nl_distributor_seeds_value numeric(14,2) DEFAULT 0,
    ns_distributor_seeds_value numeric(14,2) DEFAULT 0,
    nt_distributor_seeds_value numeric(14,2) DEFAULT 0,
    nu_distributor_seeds_value numeric(14,2) DEFAULT 0,
    on_distributor_seeds_value numeric(14,2) DEFAULT 0,
    pe_distributor_seeds_value numeric(14,2) DEFAULT 0,
    qc_distributor_seeds_value numeric(14,2) DEFAULT 0,
    sk_distributor_seeds_value numeric(14,2) DEFAULT 0,
    yt_distributor_seeds_value numeric(14,2) DEFAULT 0,
    total_distributor_seeds_value numeric(14,2) DEFAULT 0,
    ab_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    bc_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    mb_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    nb_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    nl_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    ns_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    nt_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    nu_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    on_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    pe_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    qc_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    sk_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    yt_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    total_recreational_consumer_seeds_value numeric(14,2) DEFAULT 0,
    ab_retailer_seeds_value numeric(14,2) DEFAULT 0,
    bc_retailer_seeds_value numeric(14,2) DEFAULT 0,
    mb_retailer_seeds_value numeric(14,2) DEFAULT 0,
    nb_retailer_seeds_value numeric(14,2) DEFAULT 0,
    nl_retailer_seeds_value numeric(14,2) DEFAULT 0,
    ns_retailer_seeds_value numeric(14,2) DEFAULT 0,
    nt_retailer_seeds_value numeric(14,2) DEFAULT 0,
    nu_retailer_seeds_value numeric(14,2) DEFAULT 0,
    on_retailer_seeds_value numeric(14,2) DEFAULT 0,
    pe_retailer_seeds_value numeric(14,2) DEFAULT 0,
    qc_retailer_seeds_value numeric(14,2) DEFAULT 0,
    sk_retailer_seeds_value numeric(14,2) DEFAULT 0,
    yt_retailer_seeds_value numeric(14,2) DEFAULT 0,
    total_retailer_seeds_value numeric(14,2) DEFAULT 0,
    ab_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    bc_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    mb_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    nb_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    nl_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    ns_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    nt_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    nu_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    on_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    pe_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    qc_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    sk_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    yt_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    total_distributor_veg_plants_value numeric(14,2) DEFAULT 0,
    ab_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    bc_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    mb_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    nb_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    nl_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    ns_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    nt_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    nu_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    on_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    pe_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    qc_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    sk_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    yt_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    total_recreational_consumer_veg_plants_value numeric(14,2) DEFAULT 0,
    ab_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    bc_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    mb_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    nb_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    nl_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    ns_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    nt_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    nu_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    on_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    pe_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    qc_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    sk_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    yt_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    total_retailer_veg_plants_value numeric(14,2) DEFAULT 0,
    ab_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    mb_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    bc_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nb_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nl_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    ns_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nt_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nu_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    on_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    pe_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    qc_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    sk_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    yt_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    total_unpackaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    ab_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    bc_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    mb_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nb_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nl_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ns_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nt_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nu_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    on_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    pe_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    qc_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    sk_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    yt_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    total_distributor_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ab_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    bc_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    mb_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nb_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nl_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ns_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nt_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nu_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    on_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    pe_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    qc_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    sk_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    yt_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    total_recreational_consumer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ab_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    bc_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    mb_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nb_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nl_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ns_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nt_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nu_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    on_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    pe_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    qc_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    sk_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    yt_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    total_retailer_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ab_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    bc_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    mb_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nb_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nl_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ns_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nt_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nu_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    on_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    pe_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    qc_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    sk_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    yt_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    total_unpackaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ab_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    bc_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    mb_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nb_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nl_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ns_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nt_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nu_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    on_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    pe_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    qc_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    sk_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    yt_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    total_distributor_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ab_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    bc_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    mb_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nb_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nl_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ns_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nt_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nu_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    on_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    pe_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    qc_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    sk_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    yt_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    total_recreational_consumer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ab_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    bc_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    mb_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nb_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nl_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ns_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nt_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nu_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    on_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    pe_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    qc_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    sk_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    yt_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    total_retailer_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ab_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    bc_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    mb_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nb_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nl_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ns_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nt_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nu_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    on_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    pe_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    qc_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    sk_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    yt_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    total_unpackaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ab_distributor_extracts_value numeric(14,2) DEFAULT 0,
    bc_distributor_extracts_value numeric(14,2) DEFAULT 0,
    mb_distributor_extracts_value numeric(14,2) DEFAULT 0,
    nb_distributor_extracts_value numeric(14,2) DEFAULT 0,
    nl_distributor_extracts_value numeric(14,2) DEFAULT 0,
    ns_distributor_extracts_value numeric(14,2) DEFAULT 0,
    nt_distributor_extracts_value numeric(14,2) DEFAULT 0,
    nu_distributor_extracts_value numeric(14,2) DEFAULT 0,
    on_distributor_extracts_value numeric(14,2) DEFAULT 0,
    pe_distributor_extracts_value numeric(14,2) DEFAULT 0,
    qc_distributor_extracts_value numeric(14,2) DEFAULT 0,
    sk_distributor_extracts_value numeric(14,2) DEFAULT 0,
    yt_distributor_extracts_value numeric(14,2) DEFAULT 0,
    total_distributor_extracts_value numeric(14,2) DEFAULT 0,
    ab_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    bc_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    mb_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    nb_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    nl_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    ns_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    nt_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    nu_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    on_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    pe_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    qc_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    sk_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    yt_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    total_recreational_consumer_extracts_value numeric(14,2) DEFAULT 0,
    ab_retailer_extracts_value numeric(14,2) DEFAULT 0,
    bc_retailer_extracts_value numeric(14,2) DEFAULT 0,
    mb_retailer_extracts_value numeric(14,2) DEFAULT 0,
    nb_retailer_extracts_value numeric(14,2) DEFAULT 0,
    nl_retailer_extracts_value numeric(14,2) DEFAULT 0,
    ns_retailer_extracts_value numeric(14,2) DEFAULT 0,
    nt_retailer_extracts_value numeric(14,2) DEFAULT 0,
    nu_retailer_extracts_value numeric(14,2) DEFAULT 0,
    on_retailer_extracts_value numeric(14,2) DEFAULT 0,
    pe_retailer_extracts_value numeric(14,2) DEFAULT 0,
    qc_retailer_extracts_value numeric(14,2) DEFAULT 0,
    sk_retailer_extracts_value numeric(14,2) DEFAULT 0,
    yt_retailer_extracts_value numeric(14,2) DEFAULT 0,
    total_retailer_extracts_value numeric(14,2) DEFAULT 0,
    ab_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    bc_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    mb_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nb_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nl_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    ns_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nt_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nu_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    on_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    pe_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    qc_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    sk_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    yt_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    total_unpackaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_veg_plants_value numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_fresh_cannabis_weight numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_fresh_cannabis_value numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_dried_cannabis_weight numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_dried_cannabis_value numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_extracts_weight numeric(14,2) DEFAULT 0,
    ab_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    bc_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    mb_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nb_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nl_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    ns_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nt_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    nu_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    on_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    pe_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    qc_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    sk_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    yt_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    total_packaged_intra_industry_extracts_value numeric(14,2) DEFAULT 0,
    unpackaged_seed_reductions_shipped_returned numeric DEFAULT 0,
    unpackaged_vegetative_plants_reductions_shipped_returned numeric DEFAULT 0,
    unpackaged_fresh_cannabis_reductions_shipped_returned numeric DEFAULT 0,
    unpackaged_dried_cannabis_reductions_shipped_returned numeric DEFAULT 0,
    unpackaged_extracts_reductions_shipped_returned numeric DEFAULT 0,
    unpackaged_seed_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    unpackaged_vegetative_plants_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    unpackaged_whole_cannabis_plants_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    unpackaged_fresh_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    unpackaged_dried_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    unpackaged_extracts_shipped_cultivators_processors numeric(14,2) DEFAULT 0
);


ALTER TABLE public.health_canada_report OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 16482)
-- Name: inventories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventories (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    type character varying NOT NULL,
    variety character varying NOT NULL,
    data jsonb,
    stats jsonb DEFAULT '{}'::jsonb,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL
);


ALTER TABLE public.inventories OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 16491)
-- Name: inventories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inventories_id_seq OWNER TO postgres;

--
-- TOC entry 3693 (class 0 OID 0)
-- Dependencies: 204
-- Name: inventories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventories_id_seq OWNED BY public.inventories.id;


--
-- TOC entry 270 (class 1259 OID 19998)
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.invoices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.invoices_id_seq OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 20000)
-- Name: invoices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.invoices (
    id bigint DEFAULT nextval('public.invoices_id_seq'::regclass) NOT NULL,
    order_id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone,
    data jsonb DEFAULT '{}'::jsonb,
    attributes jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.invoices OWNER TO postgres;

--
-- TOC entry 205 (class 1259 OID 16493)
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_items_id_seq OWNER TO postgres;

--
-- TOC entry 206 (class 1259 OID 16495)
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    id bigint DEFAULT nextval('public.order_items_id_seq'::regclass) NOT NULL,
    sku_id bigint NOT NULL,
    sku_name character varying NOT NULL,
    order_id bigint NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    created_by integer NOT NULL,
    shipment_id bigint,
    organization_id integer NOT NULL,
    ordered_stats jsonb DEFAULT '{}'::jsonb,
    variety character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    shipped_stats jsonb DEFAULT '{}'::jsonb NOT NULL,
    status character varying,
    quantity integer,
    filled integer,
    price numeric(14,2) DEFAULT 0,
    excise_tax numeric(14,2) DEFAULT 0,
    provincial_tax numeric(14,2) DEFAULT 0,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL,
    discount numeric(14,2) DEFAULT 0,
    shipping_value numeric(14,2) DEFAULT 0
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- TOC entry 207 (class 1259 OID 16506)
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO postgres;

--
-- TOC entry 208 (class 1259 OID 16508)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    id bigint DEFAULT nextval('public.orders_id_seq'::regclass) NOT NULL,
    crm_account_id integer,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    description character varying,
    order_type character varying,
    order_received_date character varying,
    order_placed_by character varying,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    shipping_address jsonb DEFAULT '{}'::jsonb,
    ordered_stats jsonb DEFAULT '{}'::jsonb NOT NULL,
    shipped_stats jsonb DEFAULT '{}'::jsonb NOT NULL,
    status character varying,
    shipping_status character varying,
    due_date character varying,
    sub_total numeric(14,2) DEFAULT 0,
    provincial_tax numeric(14,2) DEFAULT 0,
    excise_tax numeric(14,2) DEFAULT 0,
    discount_percent numeric(14,2) DEFAULT 0,
    discount numeric(14,2) DEFAULT 0,
    shipping_value numeric(14,2) DEFAULT 0,
    total numeric(14,2) DEFAULT 0,
    include_tax boolean DEFAULT true
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- TOC entry 209 (class 1259 OID 16520)
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    name character varying NOT NULL,
    id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 16527)
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organizations_id_seq OWNER TO postgres;

--
-- TOC entry 3702 (class 0 OID 0)
-- Dependencies: 210
-- Name: organizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organizations_id_seq OWNED BY public.organizations.id;


--
-- TOC entry 233 (class 1259 OID 18566)
-- Name: recalls_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recalls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.recalls_id_seq OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 18568)
-- Name: recalls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recalls (
    id bigint DEFAULT nextval('public.recalls_id_seq'::regclass) NOT NULL,
    description character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    active_date timestamp with time zone,
    end_date timestamp with time zone,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    lot_ids jsonb DEFAULT '[]'::jsonb NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    contact_user integer NOT NULL
);


ALTER TABLE public.recalls OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 16538)
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    name character varying NOT NULL,
    data jsonb,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 16545)
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rooms_id_seq OWNER TO postgres;

--
-- TOC entry 3707 (class 0 OID 0)
-- Dependencies: 212
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- TOC entry 213 (class 1259 OID 16547)
-- Name: rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rules (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    description character varying,
    activity character varying NOT NULL,
    conditions jsonb NOT NULL,
    data jsonb
);


ALTER TABLE public.rules OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 16554)
-- Name: rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rules_id_seq OWNER TO postgres;

--
-- TOC entry 3710 (class 0 OID 0)
-- Dependencies: 214
-- Name: rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rules_id_seq OWNED BY public.rules.id;


--
-- TOC entry 264 (class 1259 OID 19922)
-- Name: sensor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sensor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sensor_id_seq OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 19924)
-- Name: sensors_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sensors_data (
    id integer DEFAULT nextval('public.sensor_id_seq'::regclass) NOT NULL,
    sensor_reading character varying NOT NULL,
    sensor_id integer NOT NULL,
    data jsonb,
    organization_id integer,
    created_by integer,
    "timestamp" timestamp with time zone DEFAULT now(),
    sensor_type character varying,
    reading_timestamp timestamp with time zone
);


ALTER TABLE public.sensors_data OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16556)
-- Name: shipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shipment_id_seq OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16558)
-- Name: shipments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shipments (
    id bigint DEFAULT nextval('public.shipment_id_seq'::regclass) NOT NULL,
    tracking_number character varying,
    shipped_date timestamp with time zone,
    delivered_date timestamp with time zone,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    shipping_address jsonb DEFAULT '{}'::jsonb,
    crm_account_id integer,
    status character varying,
    data jsonb DEFAULT '{}'::jsonb,
    attributes jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.shipments OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 18685)
-- Name: signatures_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.signatures_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.signatures_id_seq OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 18687)
-- Name: signatures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.signatures (
    id bigint DEFAULT nextval('public.signatures_id_seq'::regclass) NOT NULL,
    field character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    signed_by integer NOT NULL,
    organization_id integer NOT NULL,
    activity_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.signatures OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16568)
-- Name: skus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skus (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    variety character varying NOT NULL,
    cannabis_class character varying,
    target_qty double precision NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL,
    target_qty_unit character varying NOT NULL,
    sales_class character varying,
    price numeric(14,2) DEFAULT 0,
    current_inventory integer DEFAULT 0
);


ALTER TABLE public.skus OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16577)
-- Name: skus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.skus_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.skus_id_seq OWNER TO postgres;

--
-- TOC entry 3719 (class 0 OID 0)
-- Dependencies: 218
-- Name: skus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.skus_id_seq OWNED BY public.skus.id;


--
-- TOC entry 242 (class 1259 OID 18664)
-- Name: sop_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sop_assignments (
    assigned_by_id bigint NOT NULL,
    assigned_to_id bigint NOT NULL,
    sop_version_id bigint NOT NULL,
    status character varying DEFAULT 'enabled'::character varying NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    signature_status character varying DEFAULT 'unsigned'::character varying NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    id bigint NOT NULL,
    organization_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.sop_assignments OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 18831)
-- Name: sop_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sop_assignments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sop_assignments_id_seq OWNER TO postgres;

--
-- TOC entry 3722 (class 0 OID 0)
-- Dependencies: 250
-- Name: sop_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sop_assignments_id_seq OWNED BY public.sop_assignments.id;


--
-- TOC entry 237 (class 1259 OID 18601)
-- Name: sop_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sop_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sop_versions_id_seq OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 18603)
-- Name: sop_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sop_versions (
    id bigint DEFAULT nextval('public.sop_versions_id_seq'::regclass) NOT NULL,
    sop_id bigint NOT NULL,
    description character varying NOT NULL,
    revision_description character varying,
    revision_reason character varying,
    approved_date timestamp with time zone,
    effective_date timestamp with time zone,
    review_due_date timestamp with time zone,
    review_approval_date timestamp with time zone,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL
);


ALTER TABLE public.sop_versions OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 18649)
-- Name: sop_versions_departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sop_versions_departments (
    sop_version_id bigint NOT NULL,
    department_id bigint NOT NULL,
    id bigint NOT NULL,
    organization_id integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.sop_versions_departments OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 18844)
-- Name: sop_versions_departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sop_versions_departments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sop_versions_departments_id_seq OWNER TO postgres;

--
-- TOC entry 3727 (class 0 OID 0)
-- Dependencies: 251
-- Name: sop_versions_departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sop_versions_departments_id_seq OWNED BY public.sop_versions_departments.id;


--
-- TOC entry 235 (class 1259 OID 18590)
-- Name: sops_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sops_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sops_id_seq OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 18592)
-- Name: sops; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sops (
    id bigint DEFAULT nextval('public.sops_id_seq'::regclass) NOT NULL,
    name character varying NOT NULL,
    status character varying DEFAULT 'enabled'::character varying NOT NULL,
    organization_id integer NOT NULL
);


ALTER TABLE public.sops OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 20057)
-- Name: srfax; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.srfax (
    id integer NOT NULL,
    file_name character varying NOT NULL,
    receive_status character varying,
    epoch_time character varying,
    date character varying,
    caller_id character varying,
    remote_id character varying,
    pages integer,
    size bigint,
    viewed_status character varying,
    pdf_content text
);


ALTER TABLE public.srfax OWNER TO postgres;

--
-- TOC entry 272 (class 1259 OID 20055)
-- Name: srfax_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.srfax_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.srfax_id_seq OWNER TO postgres;

--
-- TOC entry 3732 (class 0 OID 0)
-- Dependencies: 272
-- Name: srfax_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.srfax_id_seq OWNED BY public.srfax.id;


--
-- TOC entry 254 (class 1259 OID 19411)
-- Name: taxes_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxes_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 99999999999999999
    CACHE 1;


ALTER TABLE public.taxes_seq OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 19413)
-- Name: taxes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxes (
    id bigint DEFAULT nextval('public.taxes_seq'::regclass) NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer NOT NULL,
    organization_id integer NOT NULL,
    country character varying NOT NULL,
    province character varying NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.taxes OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16579)
-- Name: taxonomies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxonomies (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb
);


ALTER TABLE public.taxonomies OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16586)
-- Name: taxonomies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxonomies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomies_id_seq OWNER TO postgres;

--
-- TOC entry 3736 (class 0 OID 0)
-- Dependencies: 220
-- Name: taxonomies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taxonomies_id_seq OWNED BY public.taxonomies.id;


--
-- TOC entry 221 (class 1259 OID 16588)
-- Name: taxonomy_options; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.taxonomy_options (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    name character varying NOT NULL,
    data jsonb,
    taxonomy_id integer NOT NULL
);


ALTER TABLE public.taxonomy_options OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16595)
-- Name: taxonomy_options_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.taxonomy_options_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.taxonomy_options_id_seq OWNER TO postgres;

--
-- TOC entry 3739 (class 0 OID 0)
-- Dependencies: 222
-- Name: taxonomy_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.taxonomy_options_id_seq OWNED BY public.taxonomy_options.id;


--
-- TOC entry 223 (class 1259 OID 16597)
-- Name: transaction_allocations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transaction_allocations (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    amount numeric(14,2) NOT NULL,
    transaction_id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    description character varying,
    type character varying
);


ALTER TABLE public.transaction_allocations OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16606)
-- Name: transaction_allocations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transaction_allocations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transaction_allocations_id_seq OWNER TO postgres;

--
-- TOC entry 3742 (class 0 OID 0)
-- Dependencies: 224
-- Name: transaction_allocations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transaction_allocations_id_seq OWNED BY public.transaction_allocations.id;


--
-- TOC entry 225 (class 1259 OID 16608)
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    description character varying,
    total_amount numeric(14,2) NOT NULL,
    data jsonb DEFAULT '{}'::jsonb,
    crm_account_id integer,
    purchase_order character varying
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16616)
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_id_seq OWNER TO postgres;

--
-- TOC entry 3745 (class 0 OID 0)
-- Dependencies: 226
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- TOC entry 227 (class 1259 OID 16618)
-- Name: uploads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.uploads (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    name character varying NOT NULL,
    content_type character varying NOT NULL,
    upload_exists boolean DEFAULT false NOT NULL,
    data jsonb,
    created_by integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.uploads OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16626)
-- Name: uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.uploads_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.uploads_id_seq OWNER TO postgres;

--
-- TOC entry 3748 (class 0 OID 0)
-- Dependencies: 228
-- Name: uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.uploads_id_seq OWNED BY public.uploads.id;


--
-- TOC entry 229 (class 1259 OID 16628)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying NOT NULL,
    organization_id integer NOT NULL,
    auth0_id character varying,
    enabled boolean NOT NULL,
    created_by integer,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    data jsonb,
    email character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16635)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 3751 (class 0 OID 0)
-- Dependencies: 230
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 260 (class 1259 OID 19873)
-- Name: vw_deviation_reports_with_assignments; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_deviation_reports_with_assignments AS
SELECT
    NULL::json AS assignments,
    NULL::bigint AS id,
    NULL::integer AS created_by,
    NULL::integer AS organization_id,
    NULL::timestamp with time zone AS "timestamp",
    NULL::character varying AS name,
    NULL::character varying AS type,
    NULL::character varying AS status,
    NULL::timestamp with time zone AS effective_date,
    NULL::character varying[] AS relates_to,
    NULL::character varying[] AS potential_impact,
    NULL::text AS impact_details,
    NULL::text AS planned_reason,
    NULL::text AS additional_details,
    NULL::text AS investigation_details,
    NULL::text AS root_cause,
    NULL::jsonb AS data,
    NULL::jsonb AS attributes;


ALTER TABLE public.vw_deviation_reports_with_assignments OWNER TO postgres;

--
-- TOC entry 261 (class 1259 OID 19896)
-- Name: vw_mother_with_mother_batch_id; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_mother_with_mother_batch_id AS
 SELECT (act.data ->> 'to_inventory_id'::text) AS mother_batch_id,
    inv.id,
    inv.organization_id,
    inv.created_by,
    inv."timestamp",
    inv.name,
    inv.type,
    inv.variety,
    inv.data,
    inv.stats,
    inv.attributes
   FROM (public.inventories inv
     LEFT JOIN public.activities act ON ((((inv.id)::numeric = ((act.data ->> 'from_inventory_id'::text))::numeric) AND (inv.organization_id = act.organization_id) AND ((act.name)::text = 'transfer_mother_plants_to_mother_batch'::text))))
  WHERE ((inv.type)::text = 'mother'::text);


ALTER TABLE public.vw_mother_with_mother_batch_id OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 18759)
-- Name: vw_sop_versions; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sop_versions AS
 SELECT sv.id,
    sv.sop_id,
    sv.description,
    sv.revision_description,
    sv.revision_reason,
    sv.approved_date,
    sv.effective_date,
    sv.review_due_date,
    sv.review_approval_date,
    sv."timestamp",
    sv.created_by,
    sv.organization_id,
    s.name,
    s.status,
    d.name AS department,
    row_number() OVER (PARTITION BY sv.sop_id ORDER BY sv.id) AS version_number
   FROM (((public.sop_versions sv
     LEFT JOIN public.sops s ON ((sv.sop_id = s.id)))
     LEFT JOIN public.sop_versions_departments svd ON ((sv.id = svd.sop_version_id)))
     LEFT JOIN public.departments d ON ((svd.department_id = d.id)));


ALTER TABLE public.vw_sop_versions OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 18826)
-- Name: vw_sop_assignments; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sop_assignments AS
 SELECT s.id,
    s.name,
    sv.id AS version_id,
    sv."timestamp",
    sv.organization_id,
    sa.signature_status,
    sa.data,
    sa.status,
    sa."timestamp" AS assignment_date,
    sa.assigned_by_id,
    sa.assigned_to_id,
    u1.name AS assigned_by,
    u2.name AS assigned_to,
    d.name AS department,
    sva.version_number
   FROM (((((((public.sop_versions sv
     LEFT JOIN public.sops s ON ((s.id = sv.sop_id)))
     LEFT JOIN public.sop_versions_departments svd ON ((sv.id = svd.sop_version_id)))
     LEFT JOIN public.departments d ON ((svd.department_id = d.id)))
     RIGHT JOIN public.sop_assignments sa ON ((sv.id = sa.sop_version_id)))
     LEFT JOIN public.users u1 ON ((u1.id = sa.assigned_by_id)))
     LEFT JOIN public.users u2 ON ((u2.id = sa.assigned_to_id)))
     LEFT JOIN public.vw_sop_versions sva ON ((sva.id = sv.id)));


ALTER TABLE public.vw_sop_assignments OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 18754)
-- Name: vw_sops; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sops AS
 SELECT sv1.id AS version_id,
    sv1."timestamp",
    sv1.description,
    sv1.approved_date,
    sv1.effective_date,
    sv1.organization_id,
    sv2.version_number,
    s.id,
    s.status,
    s.name,
    d.name AS department
   FROM ((((public.sop_versions sv1
     JOIN ( SELECT count(sop_versions.id) AS version_number,
            max(sop_versions.id) AS max_id,
            sop_versions.sop_id
           FROM public.sop_versions
          GROUP BY sop_versions.sop_id) sv2 ON ((sv1.id = sv2.max_id)))
     LEFT JOIN public.sops s ON ((s.id = sv1.sop_id)))
     LEFT JOIN public.sop_versions_departments svd ON ((sv1.id = svd.sop_version_id)))
     LEFT JOIN public.departments d ON ((svd.department_id = d.id)));


ALTER TABLE public.vw_sops OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 18795)
-- Name: vw_sop_logs; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sop_logs AS
 SELECT s.id,
    s.version_number,
    s.name,
    s.department,
    a.name AS activity,
    u.name AS "user",
    a."timestamp",
    a.organization_id
   FROM ((public.vw_sops s
     LEFT JOIN public.activities a ON (((s.version_id = ((a.data ->> 'sop_version_id'::text))::integer) OR (s.id = ((a.data ->> 'sop_id'::text))::integer))))
     LEFT JOIN public.users u ON ((u.id = a.created_by)))
  ORDER BY a."timestamp" DESC;


ALTER TABLE public.vw_sop_logs OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 18800)
-- Name: vw_sop_notifications; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_sop_notifications AS
 SELECT a.id,
    s.sop_id,
    s.version_number AS sop_version_number,
    s.name AS sop_name,
    u1.name AS assigned_by,
    a."timestamp",
    a.organization_id,
    u2.name AS assigned_to
   FROM (((public.activities a
     LEFT JOIN public.users u1 ON ((u1.id = ((a.data ->> 'assigned_by_id'::text))::integer)))
     LEFT JOIN public.users u2 ON ((u2.id = ((a.data ->> 'assigned_to_id'::text))::integer)))
     LEFT JOIN public.vw_sop_versions s ON ((s.id = ((a.data ->> 'sop_version_id'::text))::integer)))
  WHERE ((a.name)::text = 'sop_assign_user'::text);


ALTER TABLE public.vw_sop_notifications OWNER TO postgres;

--
-- TOC entry 262 (class 1259 OID 19905)
-- Name: webhook_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.webhook_subscriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.webhook_subscriptions_id_seq OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 19907)
-- Name: webhook_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.webhook_subscriptions (
    id integer DEFAULT nextval('public.webhook_subscriptions_id_seq'::regclass) NOT NULL,
    event character varying NOT NULL,
    url character varying NOT NULL,
    name character varying,
    created_by integer,
    organization_id integer,
    "timestamp" timestamp with time zone DEFAULT now()
);


ALTER TABLE public.webhook_subscriptions OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16637)
-- Name: sensors; Type: TABLE; Schema: sensor_data; Owner: postgres
--

CREATE TABLE sensor_data.sensors (
    id integer NOT NULL,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    database_id integer NOT NULL,
    external_id character varying NOT NULL,
    organization_id integer NOT NULL
);


ALTER TABLE sensor_data.sensors OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16645)
-- Name: sensors_id_seq; Type: SEQUENCE; Schema: sensor_data; Owner: postgres
--

CREATE SEQUENCE sensor_data.sensors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE sensor_data.sensors_id_seq OWNER TO postgres;

--
-- TOC entry 3763 (class 0 OID 0)
-- Dependencies: 232
-- Name: sensors_id_seq; Type: SEQUENCE OWNED BY; Schema: sensor_data; Owner: postgres
--

ALTER SEQUENCE sensor_data.sensors_id_seq OWNED BY sensor_data.sensors.id;


--
-- TOC entry 2332 (class 2604 OID 16647)
-- Name: activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities ALTER COLUMN id SET DEFAULT nextval('public.activities_id_seq'::regclass);


--
-- TOC entry 2349 (class 2604 OID 16648)
-- Name: consumable_classes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_classes ALTER COLUMN id SET DEFAULT nextval('public.consumable_classes_id_seq'::regclass);


--
-- TOC entry 2352 (class 2604 OID 16649)
-- Name: consumable_lots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_lots ALTER COLUMN id SET DEFAULT nextval('public.consumable_lots_id_seq'::regclass);


--
-- TOC entry 2355 (class 2604 OID 16650)
-- Name: crm_accounts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_accounts ALTER COLUMN id SET DEFAULT nextval('public.crm_account_id_seq'::regclass);


--
-- TOC entry 2359 (class 2604 OID 16651)
-- Name: equipment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN id SET DEFAULT nextval('public.equipment_id_seq'::regclass);


--
-- TOC entry 2364 (class 2604 OID 16652)
-- Name: inventories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories ALTER COLUMN id SET DEFAULT nextval('public.inventories_id_seq'::regclass);


--
-- TOC entry 2393 (class 2604 OID 16653)
-- Name: organizations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations ALTER COLUMN id SET DEFAULT nextval('public.organizations_id_seq'::regclass);


--
-- TOC entry 2395 (class 2604 OID 16655)
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- TOC entry 2397 (class 2604 OID 16656)
-- Name: rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules ALTER COLUMN id SET DEFAULT nextval('public.rules_id_seq'::regclass);


--
-- TOC entry 2404 (class 2604 OID 16657)
-- Name: skus id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skus ALTER COLUMN id SET DEFAULT nextval('public.skus_id_seq'::regclass);


--
-- TOC entry 2444 (class 2604 OID 18833)
-- Name: sop_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_assignments ALTER COLUMN id SET DEFAULT nextval('public.sop_assignments_id_seq'::regclass);


--
-- TOC entry 2438 (class 2604 OID 18846)
-- Name: sop_versions_departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions_departments ALTER COLUMN id SET DEFAULT nextval('public.sop_versions_departments_id_seq'::regclass);


--
-- TOC entry 3307 (class 2604 OID 20060)
-- Name: srfax id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.srfax ALTER COLUMN id SET DEFAULT nextval('public.srfax_id_seq'::regclass);


--
-- TOC entry 2410 (class 2604 OID 16658)
-- Name: taxonomies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies ALTER COLUMN id SET DEFAULT nextval('public.taxonomies_id_seq'::regclass);


--
-- TOC entry 2412 (class 2604 OID 16659)
-- Name: taxonomy_options id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options ALTER COLUMN id SET DEFAULT nextval('public.taxonomy_options_id_seq'::regclass);


--
-- TOC entry 2414 (class 2604 OID 16660)
-- Name: transaction_allocations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_allocations ALTER COLUMN id SET DEFAULT nextval('public.transaction_allocations_id_seq'::regclass);


--
-- TOC entry 2417 (class 2604 OID 16661)
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- TOC entry 2420 (class 2604 OID 16662)
-- Name: uploads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads ALTER COLUMN id SET DEFAULT nextval('public.uploads_id_seq'::regclass);


--
-- TOC entry 2423 (class 2604 OID 16663)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 2425 (class 2604 OID 16664)
-- Name: sensors id; Type: DEFAULT; Schema: sensor_data; Owner: postgres
--

ALTER TABLE ONLY sensor_data.sensors ALTER COLUMN id SET DEFAULT nextval('sensor_data.sensors_id_seq'::regclass);


--
-- TOC entry 3310 (class 2606 OID 16666)
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- TOC entry 3312 (class 2606 OID 16668)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: migration_runner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 3406 (class 2606 OID 19983)
-- Name: audit_detail audit_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_detail
    ADD CONSTRAINT audit_detail_pkey PRIMARY KEY (id);


--
-- TOC entry 3404 (class 2606 OID 19959)
-- Name: audit audit_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit
    ADD CONSTRAINT audit_pkey PRIMARY KEY (id);


--
-- TOC entry 3314 (class 2606 OID 16670)
-- Name: capa_actions capa_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_actions
    ADD CONSTRAINT capa_actions_pkey PRIMARY KEY (id);


--
-- TOC entry 3316 (class 2606 OID 16672)
-- Name: capa_links capa_links_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_links
    ADD CONSTRAINT capa_links_pkey PRIMARY KEY (id);


--
-- TOC entry 3318 (class 2606 OID 16674)
-- Name: capas capas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capas
    ADD CONSTRAINT capas_pkey PRIMARY KEY (id);


--
-- TOC entry 3320 (class 2606 OID 16676)
-- Name: consumable_classes consumable_classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_classes
    ADD CONSTRAINT consumable_classes_pkey PRIMARY KEY (id);


--
-- TOC entry 3322 (class 2606 OID 16678)
-- Name: consumable_lots consumable_lots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_lots
    ADD CONSTRAINT consumable_lots_pkey PRIMARY KEY (id);


--
-- TOC entry 3324 (class 2606 OID 16680)
-- Name: crm_accounts crm_account_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_accounts
    ADD CONSTRAINT crm_account_pkey PRIMARY KEY (id);


--
-- TOC entry 3398 (class 2606 OID 19851)
-- Name: deviation_reports_assignments deviation_reports_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports_assignments
    ADD CONSTRAINT deviation_reports_assignments_pkey PRIMARY KEY (id);


--
-- TOC entry 3396 (class 2606 OID 19827)
-- Name: deviation_reports deviation_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports
    ADD CONSTRAINT deviation_reports_pkey PRIMARY KEY (id);


--
-- TOC entry 3326 (class 2606 OID 16682)
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (id);


--
-- TOC entry 3392 (class 2606 OID 18974)
-- Name: health_canada_report hcr_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_canada_report
    ADD CONSTRAINT hcr_pkey PRIMARY KEY (id);


--
-- TOC entry 3332 (class 2606 OID 16684)
-- Name: inventories inventories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_pkey PRIMARY KEY (id);


--
-- TOC entry 3408 (class 2606 OID 20010)
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- TOC entry 3335 (class 2606 OID 16686)
-- Name: order_items order_rows_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_rows_pkey PRIMARY KEY (id);


--
-- TOC entry 3337 (class 2606 OID 16688)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- TOC entry 3340 (class 2606 OID 16690)
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- TOC entry 3378 (class 2606 OID 18579)
-- Name: recalls recalls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recalls
    ADD CONSTRAINT recalls_pkey PRIMARY KEY (id);


--
-- TOC entry 3344 (class 2606 OID 16694)
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- TOC entry 3349 (class 2606 OID 16696)
-- Name: rules rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (id);


--
-- TOC entry 3402 (class 2606 OID 19933)
-- Name: sensors_data sensor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensors_data
    ADD CONSTRAINT sensor_pkey PRIMARY KEY (id);


--
-- TOC entry 3351 (class 2606 OID 16698)
-- Name: shipments shipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipment_pkey PRIMARY KEY (id);


--
-- TOC entry 3390 (class 2606 OID 18697)
-- Name: signatures signatures_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signatures
    ADD CONSTRAINT signatures_pkey PRIMARY KEY (id);


--
-- TOC entry 3353 (class 2606 OID 16700)
-- Name: skus skus_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_pkey PRIMARY KEY (id);


--
-- TOC entry 3388 (class 2606 OID 18836)
-- Name: sop_assignments sop_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_assignments
    ADD CONSTRAINT sop_assignments_pkey PRIMARY KEY (id);


--
-- TOC entry 3384 (class 2606 OID 18638)
-- Name: departments sop_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT sop_departments_pkey PRIMARY KEY (id);


--
-- TOC entry 3386 (class 2606 OID 18849)
-- Name: sop_versions_departments sop_versions_departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions_departments
    ADD CONSTRAINT sop_versions_departments_pkey PRIMARY KEY (id);


--
-- TOC entry 3382 (class 2606 OID 18612)
-- Name: sop_versions sop_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions
    ADD CONSTRAINT sop_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 3380 (class 2606 OID 18600)
-- Name: sops sops_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sops
    ADD CONSTRAINT sops_pkey PRIMARY KEY (id);


--
-- TOC entry 3410 (class 2606 OID 20065)
-- Name: srfax srfax_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.srfax
    ADD CONSTRAINT srfax_pkey PRIMARY KEY (id);


--
-- TOC entry 3394 (class 2606 OID 20068)
-- Name: taxes taxes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxes
    ADD CONSTRAINT taxes_pkey PRIMARY KEY (id);


--
-- TOC entry 3357 (class 2606 OID 16702)
-- Name: taxonomies taxonomies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_pkey PRIMARY KEY (id);


--
-- TOC entry 3362 (class 2606 OID 16704)
-- Name: taxonomy_options taxonomy_options_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_pkey PRIMARY KEY (id);


--
-- TOC entry 3366 (class 2606 OID 16706)
-- Name: transaction_allocations transaction_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_allocations
    ADD CONSTRAINT transaction_allocations_pkey PRIMARY KEY (id);


--
-- TOC entry 3368 (class 2606 OID 16708)
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- TOC entry 3328 (class 2606 OID 16710)
-- Name: equipment unique_external_id_per_type_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT unique_external_id_per_type_per_org UNIQUE (external_id, type, organization_id);


--
-- TOC entry 3364 (class 2606 OID 16712)
-- Name: taxonomy_options unique_option_per_taxonomy; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT unique_option_per_taxonomy UNIQUE (taxonomy_id, name);


--
-- TOC entry 3342 (class 2606 OID 16716)
-- Name: organizations unique_organization_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT unique_organization_name UNIQUE (name);


--
-- TOC entry 3346 (class 2606 OID 16718)
-- Name: rooms unique_room_name_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT unique_room_name_per_org UNIQUE (organization_id, name);


--
-- TOC entry 3359 (class 2606 OID 16720)
-- Name: taxonomies unique_taxonomies_per_org; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT unique_taxonomies_per_org UNIQUE (organization_id, name);


--
-- TOC entry 3371 (class 2606 OID 16722)
-- Name: uploads uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT uploads_pkey PRIMARY KEY (id);


--
-- TOC entry 3375 (class 2606 OID 16724)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3400 (class 2606 OID 19916)
-- Name: webhook_subscriptions webhook_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_subscriptions
    ADD CONSTRAINT webhook_subscriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 3308 (class 1259 OID 16725)
-- Name: activities_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX activities_data ON public.activities USING gin (data);


--
-- TOC entry 3354 (class 1259 OID 16726)
-- Name: fki_taxonomies_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_taxonomies_org ON public.taxonomies USING btree (organization_id);


--
-- TOC entry 3355 (class 1259 OID 16727)
-- Name: fki_taxonomies_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_taxonomies_user ON public.taxonomies USING btree (created_by);


--
-- TOC entry 3372 (class 1259 OID 16729)
-- Name: fki_users_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX fki_users_org ON public.users USING btree (organization_id);


--
-- TOC entry 3329 (class 1259 OID 16730)
-- Name: inventories_attributes; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_attributes ON public.inventories USING gin (attributes);


--
-- TOC entry 3330 (class 1259 OID 16731)
-- Name: inventories_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_data ON public.inventories USING gin (data);


--
-- TOC entry 3333 (class 1259 OID 16732)
-- Name: inventories_stats; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX inventories_stats ON public.inventories USING gin (stats);


--
-- TOC entry 3338 (class 1259 OID 16733)
-- Name: organizations_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX organizations_data ON public.organizations USING gin (data);


--
-- TOC entry 3347 (class 1259 OID 16735)
-- Name: rules_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX rules_data ON public.rules USING gin (data);


--
-- TOC entry 3360 (class 1259 OID 16736)
-- Name: taxonomy_options_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX taxonomy_options_data ON public.taxonomy_options USING gin (data);


--
-- TOC entry 3369 (class 1259 OID 16737)
-- Name: uploads_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX uploads_data ON public.uploads USING gin (data);


--
-- TOC entry 3373 (class 1259 OID 16738)
-- Name: users_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX users_data ON public.users USING gin (data);


--
-- TOC entry 3376 (class 1259 OID 16739)
-- Name: users_unique_lower_email_per_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX users_unique_lower_email_per_org ON public.users USING btree (lower((email)::text), organization_id);


--
-- TOC entry 3646 (class 2618 OID 19876)
-- Name: vw_deviation_reports_with_assignments _RETURN; Type: RULE; Schema: public; Owner: postgres
--

CREATE OR REPLACE VIEW public.vw_deviation_reports_with_assignments AS
 SELECT ( SELECT json_agg(json_build_object('id', inner_dr.id, 'user_id', inner_dr.user_id, 'user_name', u.name, 'email', u.email, 'type', inner_dr.type, 'status', inner_dr.status)) AS json_agg
           FROM (public.deviation_reports_assignments inner_dr
             LEFT JOIN public.users u ON ((u.id = inner_dr.user_id)))
          WHERE (inner_dr.deviation_reports_id = dr.id)) AS assignments,
    dr.id,
    dr.created_by,
    dr.organization_id,
    dr."timestamp",
    dr.name,
    dr.type,
    dr.status,
    dr.effective_date,
    dr.relates_to,
    dr.potential_impact,
    dr.impact_details,
    dr.planned_reason,
    dr.additional_details,
    dr.investigation_details,
    dr.root_cause,
    dr.data,
    dr.attributes
   FROM (public.deviation_reports dr
     LEFT JOIN public.deviation_reports_assignments da ON ((dr.id = da.deviation_reports_id)))
  GROUP BY dr.id;


--
-- TOC entry 3498 (class 2620 OID 16740)
-- Name: activities activities_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER activities_update_merge_data BEFORE UPDATE ON public.activities FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3499 (class 2620 OID 16741)
-- Name: capa_actions capa_actions_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER capa_actions_update_merge_data BEFORE UPDATE ON public.capa_actions FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3500 (class 2620 OID 16742)
-- Name: capa_links capa_links_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER capa_links_update_merge_data BEFORE UPDATE ON public.capa_links FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3501 (class 2620 OID 16743)
-- Name: capas capas_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER capas_update_merge_data BEFORE UPDATE ON public.capas FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3502 (class 2620 OID 16744)
-- Name: consumable_classes consumable_classes_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER consumable_classes_update_merge_data BEFORE UPDATE ON public.consumable_classes FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3503 (class 2620 OID 16745)
-- Name: consumable_lots consumable_lots_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER consumable_lots_update_merge_data BEFORE UPDATE ON public.consumable_lots FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3504 (class 2620 OID 16746)
-- Name: crm_accounts crm_account_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER crm_account_update_merge_data BEFORE UPDATE ON public.crm_accounts FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3523 (class 2620 OID 19872)
-- Name: deviation_reports_assignments deviation_reports_assignments_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER deviation_reports_assignments_update_merge_data BEFORE UPDATE ON public.deviation_reports_assignments FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3522 (class 2620 OID 19838)
-- Name: deviation_reports deviation_reports_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER deviation_reports_update_merge_data BEFORE UPDATE ON public.deviation_reports FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3505 (class 2620 OID 16747)
-- Name: equipment equipment_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER equipment_update_merge_data BEFORE UPDATE ON public.equipment FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3506 (class 2620 OID 16748)
-- Name: inventories inventories_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER inventories_update_merge_data BEFORE UPDATE ON public.inventories FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3507 (class 2620 OID 16749)
-- Name: order_items order_rows_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER order_rows_update_merge_data BEFORE UPDATE ON public.order_items FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3508 (class 2620 OID 16750)
-- Name: orders orders_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER orders_update_merge_data BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3509 (class 2620 OID 16751)
-- Name: organizations organizations_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER organizations_update_merge_data BEFORE UPDATE ON public.organizations FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3520 (class 2620 OID 18684)
-- Name: recalls recalls_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER recalls_update_merge_data BEFORE UPDATE ON public.recalls FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3510 (class 2620 OID 16753)
-- Name: rooms rooms_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER rooms_update_merge_data BEFORE UPDATE ON public.rooms FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3511 (class 2620 OID 16754)
-- Name: rules rules_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER rules_update_merge_data BEFORE UPDATE ON public.rules FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3512 (class 2620 OID 16755)
-- Name: shipments shipments_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER shipments_update_merge_data BEFORE UPDATE ON public.shipments FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3521 (class 2620 OID 18718)
-- Name: signatures signatures_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER signatures_update_merge_data BEFORE UPDATE ON public.signatures FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3513 (class 2620 OID 16756)
-- Name: skus skus_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER skus_update_merge_data BEFORE UPDATE ON public.skus FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3514 (class 2620 OID 16757)
-- Name: taxonomies taxonomies_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER taxonomies_update_merge_data BEFORE UPDATE ON public.taxonomies FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3515 (class 2620 OID 16758)
-- Name: taxonomy_options taxonomy_options_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER taxonomy_options_update_merge_data BEFORE UPDATE ON public.taxonomy_options FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3516 (class 2620 OID 16759)
-- Name: transaction_allocations transaction_allocations_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER transaction_allocations_update_merge_data BEFORE UPDATE ON public.transaction_allocations FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3517 (class 2620 OID 16760)
-- Name: transactions transactions_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER transactions_update_merge_data BEFORE UPDATE ON public.transactions FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3518 (class 2620 OID 16761)
-- Name: uploads uploads_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER uploads_update_merge_data BEFORE UPDATE ON public.uploads FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3519 (class 2620 OID 16762)
-- Name: users users_update_merge_data; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER users_update_merge_data BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE PROCEDURE public.jsonb_merge_data();


--
-- TOC entry 3411 (class 2606 OID 16763)
-- Name: activities activity_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activity_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3491 (class 2606 OID 19960)
-- Name: audit activity_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit
    ADD CONSTRAINT activity_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3494 (class 2606 OID 19984)
-- Name: audit_detail activity_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_detail
    ADD CONSTRAINT activity_org FOREIGN KEY (audit_id) REFERENCES public.audit(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3412 (class 2606 OID 16768)
-- Name: activities activity_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activities
    ADD CONSTRAINT activity_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3492 (class 2606 OID 19965)
-- Name: audit activity_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit
    ADD CONSTRAINT activity_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3413 (class 2606 OID 16773)
-- Name: capa_actions capa_actions_capa; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_actions
    ADD CONSTRAINT capa_actions_capa FOREIGN KEY (capa_id) REFERENCES public.capas(id);


--
-- TOC entry 3414 (class 2606 OID 16778)
-- Name: capa_actions capa_actions_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_actions
    ADD CONSTRAINT capa_actions_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3415 (class 2606 OID 16783)
-- Name: capa_actions capa_actions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_actions
    ADD CONSTRAINT capa_actions_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3416 (class 2606 OID 16793)
-- Name: capa_links capa_links_capa; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_links
    ADD CONSTRAINT capa_links_capa FOREIGN KEY (capa_id) REFERENCES public.capas(id);


--
-- TOC entry 3417 (class 2606 OID 16808)
-- Name: capa_links capa_links_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_links
    ADD CONSTRAINT capa_links_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3418 (class 2606 OID 16813)
-- Name: capa_links capa_links_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capa_links
    ADD CONSTRAINT capa_links_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3419 (class 2606 OID 16818)
-- Name: capas capas_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capas
    ADD CONSTRAINT capas_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3420 (class 2606 OID 16823)
-- Name: capas capas_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capas
    ADD CONSTRAINT capas_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3421 (class 2606 OID 16828)
-- Name: consumable_classes consumable_classes_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_classes
    ADD CONSTRAINT consumable_classes_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3422 (class 2606 OID 16833)
-- Name: consumable_classes consumable_classes_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_classes
    ADD CONSTRAINT consumable_classes_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3423 (class 2606 OID 16838)
-- Name: consumable_lots consumable_lots_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_lots
    ADD CONSTRAINT consumable_lots_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3424 (class 2606 OID 16843)
-- Name: consumable_lots consumable_lots_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_lots
    ADD CONSTRAINT consumable_lots_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3425 (class 2606 OID 16848)
-- Name: consumable_lots consumables_class; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.consumable_lots
    ADD CONSTRAINT consumables_class FOREIGN KEY (class_id) REFERENCES public.consumable_classes(id);


--
-- TOC entry 3426 (class 2606 OID 16853)
-- Name: crm_accounts crm_account_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_accounts
    ADD CONSTRAINT crm_account_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3427 (class 2606 OID 16858)
-- Name: crm_accounts crm_account_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crm_accounts
    ADD CONSTRAINT crm_account_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3487 (class 2606 OID 19867)
-- Name: deviation_reports_assignments deviation_reports_assignments_assigned_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports_assignments
    ADD CONSTRAINT deviation_reports_assignments_assigned_user FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3486 (class 2606 OID 19862)
-- Name: deviation_reports_assignments deviation_reports_assignments_deviation_reports; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports_assignments
    ADD CONSTRAINT deviation_reports_assignments_deviation_reports FOREIGN KEY (deviation_reports_id) REFERENCES public.deviation_reports(id);


--
-- TOC entry 3484 (class 2606 OID 19852)
-- Name: deviation_reports_assignments deviation_reports_assignments_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports_assignments
    ADD CONSTRAINT deviation_reports_assignments_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3485 (class 2606 OID 19857)
-- Name: deviation_reports_assignments deviation_reports_assignments_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports_assignments
    ADD CONSTRAINT deviation_reports_assignments_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3482 (class 2606 OID 19828)
-- Name: deviation_reports deviation_reports_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports
    ADD CONSTRAINT deviation_reports_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3483 (class 2606 OID 19833)
-- Name: deviation_reports deviation_reports_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deviation_reports
    ADD CONSTRAINT deviation_reports_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3428 (class 2606 OID 16863)
-- Name: equipment equipment_org_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_org_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3429 (class 2606 OID 16868)
-- Name: equipment equipment_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_user_id FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3488 (class 2606 OID 19917)
-- Name: webhook_subscriptions fk_organization; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.webhook_subscriptions
    ADD CONSTRAINT fk_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3480 (class 2606 OID 18975)
-- Name: health_canada_report hcr_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_canada_report
    ADD CONSTRAINT hcr_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3481 (class 2606 OID 18980)
-- Name: health_canada_report hcr_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.health_canada_report
    ADD CONSTRAINT hcr_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3430 (class 2606 OID 16873)
-- Name: inventories inventories_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3431 (class 2606 OID 16878)
-- Name: inventories inventories_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventories
    ADD CONSTRAINT inventories_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3495 (class 2606 OID 20011)
-- Name: invoices invoices_order; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_order FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- TOC entry 3496 (class 2606 OID 20016)
-- Name: invoices invoices_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3497 (class 2606 OID 20021)
-- Name: invoices invoices_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3432 (class 2606 OID 16883)
-- Name: order_items order_rows_order; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_rows_order FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- TOC entry 3433 (class 2606 OID 16888)
-- Name: order_items order_rows_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_rows_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3434 (class 2606 OID 16893)
-- Name: order_items order_rows_sku_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_rows_sku_id FOREIGN KEY (sku_id) REFERENCES public.skus(id);


--
-- TOC entry 3435 (class 2606 OID 16898)
-- Name: order_items order_rows_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_rows_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3436 (class 2606 OID 16903)
-- Name: order_items order_shipment; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_shipment FOREIGN KEY (shipment_id) REFERENCES public.shipments(id);


--
-- TOC entry 3437 (class 2606 OID 16908)
-- Name: orders orders_crm_account; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_crm_account FOREIGN KEY (crm_account_id) REFERENCES public.crm_accounts(id);


--
-- TOC entry 3438 (class 2606 OID 16913)
-- Name: orders orders_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3439 (class 2606 OID 16918)
-- Name: orders orders_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_users FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3489 (class 2606 OID 19934)
-- Name: sensors_data org_sensor_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensors_data
    ADD CONSTRAINT org_sensor_fk FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3464 (class 2606 OID 18585)
-- Name: recalls recalls_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recalls
    ADD CONSTRAINT recalls_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3463 (class 2606 OID 18580)
-- Name: recalls recalls_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recalls
    ADD CONSTRAINT recalls_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3493 (class 2606 OID 19970)
-- Name: audit request_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit
    ADD CONSTRAINT request_user FOREIGN KEY (requested_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3440 (class 2606 OID 16928)
-- Name: rooms rooms_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3441 (class 2606 OID 16933)
-- Name: rooms rooms_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3442 (class 2606 OID 16938)
-- Name: rules rules_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3443 (class 2606 OID 16943)
-- Name: rules rules_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3490 (class 2606 OID 19939)
-- Name: sensors_data sensor_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sensors_data
    ADD CONSTRAINT sensor_id_fk FOREIGN KEY (sensor_id) REFERENCES public.equipment(id);


--
-- TOC entry 3444 (class 2606 OID 16948)
-- Name: shipments shipment_account_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipment_account_id FOREIGN KEY (crm_account_id) REFERENCES public.crm_accounts(id);


--
-- TOC entry 3445 (class 2606 OID 16953)
-- Name: shipments shipment_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipment_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3446 (class 2606 OID 16958)
-- Name: shipments shipment_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shipments
    ADD CONSTRAINT shipment_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3479 (class 2606 OID 18713)
-- Name: signatures signatures_activity; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signatures
    ADD CONSTRAINT signatures_activity FOREIGN KEY (activity_id) REFERENCES public.activities(id);


--
-- TOC entry 3476 (class 2606 OID 18698)
-- Name: signatures signatures_created_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signatures
    ADD CONSTRAINT signatures_created_by FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3478 (class 2606 OID 18708)
-- Name: signatures signatures_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signatures
    ADD CONSTRAINT signatures_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3477 (class 2606 OID 18703)
-- Name: signatures signatures_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.signatures
    ADD CONSTRAINT signatures_user FOREIGN KEY (signed_by) REFERENCES public.users(id);


--
-- TOC entry 3447 (class 2606 OID 16963)
-- Name: skus skus_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3448 (class 2606 OID 16968)
-- Name: skus skus_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3473 (class 2606 OID 18669)
-- Name: sop_assignments sop_assignments_assigned_by_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_assignments
    ADD CONSTRAINT sop_assignments_assigned_by_id FOREIGN KEY (assigned_by_id) REFERENCES public.users(id);


--
-- TOC entry 3474 (class 2606 OID 18674)
-- Name: sop_assignments sop_assignments_assigned_to_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_assignments
    ADD CONSTRAINT sop_assignments_assigned_to_id FOREIGN KEY (assigned_to_id) REFERENCES public.users(id);


--
-- TOC entry 3475 (class 2606 OID 18679)
-- Name: sop_assignments sop_assignments_sop_version; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_assignments
    ADD CONSTRAINT sop_assignments_sop_version FOREIGN KEY (sop_version_id) REFERENCES public.sop_versions(id);


--
-- TOC entry 3468 (class 2606 OID 18623)
-- Name: sop_versions sop_versions_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions
    ADD CONSTRAINT sop_versions_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3470 (class 2606 OID 18644)
-- Name: departments sop_versions_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT sop_versions_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3466 (class 2606 OID 18613)
-- Name: sop_versions sop_versions_sop; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions
    ADD CONSTRAINT sop_versions_sop FOREIGN KEY (sop_id) REFERENCES public.sops(id);


--
-- TOC entry 3472 (class 2606 OID 18659)
-- Name: sop_versions_departments sop_versions_sop_departments_department; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions_departments
    ADD CONSTRAINT sop_versions_sop_departments_department FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- TOC entry 3471 (class 2606 OID 18654)
-- Name: sop_versions_departments sop_versions_sop_departments_version; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions_departments
    ADD CONSTRAINT sop_versions_sop_departments_version FOREIGN KEY (sop_version_id) REFERENCES public.sop_versions(id);


--
-- TOC entry 3467 (class 2606 OID 18618)
-- Name: sop_versions sop_versions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sop_versions
    ADD CONSTRAINT sop_versions_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3469 (class 2606 OID 18639)
-- Name: departments sop_versions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT sop_versions_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3465 (class 2606 OID 18777)
-- Name: sops sops_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sops
    ADD CONSTRAINT sops_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3449 (class 2606 OID 16973)
-- Name: taxonomies taxonomies_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3450 (class 2606 OID 16978)
-- Name: taxonomies taxonomies_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomies
    ADD CONSTRAINT taxonomies_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3451 (class 2606 OID 16983)
-- Name: taxonomy_options taxonomy_options_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3452 (class 2606 OID 16988)
-- Name: taxonomy_options taxonomy_options_taxonomy; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_taxonomy FOREIGN KEY (taxonomy_id) REFERENCES public.taxonomies(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3453 (class 2606 OID 16993)
-- Name: taxonomy_options taxonomy_options_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.taxonomy_options
    ADD CONSTRAINT taxonomy_options_user FOREIGN KEY (created_by) REFERENCES public.users(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3459 (class 2606 OID 18561)
-- Name: transactions transaction_account_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transaction_account_id FOREIGN KEY (crm_account_id) REFERENCES public.crm_accounts(id);


--
-- TOC entry 3454 (class 2606 OID 17008)
-- Name: transaction_allocations transaction_allocations_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_allocations
    ADD CONSTRAINT transaction_allocations_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3455 (class 2606 OID 17013)
-- Name: transaction_allocations transaction_allocations_transaction; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_allocations
    ADD CONSTRAINT transaction_allocations_transaction FOREIGN KEY (transaction_id) REFERENCES public.transactions(id);


--
-- TOC entry 3456 (class 2606 OID 17018)
-- Name: transaction_allocations transaction_allocations_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transaction_allocations
    ADD CONSTRAINT transaction_allocations_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3457 (class 2606 OID 17023)
-- Name: transactions transactions_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- TOC entry 3458 (class 2606 OID 17028)
-- Name: transactions transactions_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3460 (class 2606 OID 17033)
-- Name: uploads upload_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT upload_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3461 (class 2606 OID 17038)
-- Name: uploads upload_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploads
    ADD CONSTRAINT upload_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3462 (class 2606 OID 17043)
-- Name: users users_org; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON UPDATE RESTRICT ON DELETE RESTRICT;


--
-- TOC entry 3655 (class 0 OID 0)
-- Dependencies: 3
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--
CREATE USER dev_users;
GRANT ALL ON SCHEMA public TO dev_users;


--
-- TOC entry 3656 (class 0 OID 0)
-- Dependencies: 6
-- Name: SCHEMA sensor_data; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA sensor_data FROM postgres;
GRANT ALL ON SCHEMA sensor_data TO postgres WITH GRANT OPTION;
GRANT ALL ON SCHEMA sensor_data TO api_server WITH GRANT OPTION;


--
-- TOC entry 3658 (class 0 OID 0)
-- Dependencies: 274
-- Name: FUNCTION jsonb_merge_data(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.jsonb_merge_data() TO api_server;
GRANT ALL ON FUNCTION public.jsonb_merge_data() TO dev_users;


--
-- TOC entry 3659 (class 0 OID 0)
-- Dependencies: 186
-- Name: TABLE activities; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.activities TO api_server;
GRANT ALL ON TABLE public.activities TO dev_users;


--
-- TOC entry 3661 (class 0 OID 0)
-- Dependencies: 187
-- Name: SEQUENCE activities_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.activities_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.activities_id_seq TO dev_users;


--
-- TOC entry 3662 (class 0 OID 0)
-- Dependencies: 266
-- Name: SEQUENCE audit_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.audit_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.audit_id_seq TO dev_users;


--
-- TOC entry 3663 (class 0 OID 0)
-- Dependencies: 268
-- Name: TABLE audit; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.audit TO api_server;
GRANT ALL ON TABLE public.audit TO dev_users;


--
-- TOC entry 3664 (class 0 OID 0)
-- Dependencies: 267
-- Name: SEQUENCE audit_detail_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.audit_detail_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.audit_detail_id_seq TO dev_users;


--
-- TOC entry 3665 (class 0 OID 0)
-- Dependencies: 269
-- Name: TABLE audit_detail; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.audit_detail TO api_server;
GRANT ALL ON TABLE public.audit_detail TO dev_users;


--
-- TOC entry 3666 (class 0 OID 0)
-- Dependencies: 189
-- Name: SEQUENCE capa_actions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.capa_actions_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.capa_actions_id_seq TO api_server;


--
-- TOC entry 3667 (class 0 OID 0)
-- Dependencies: 190
-- Name: TABLE capa_actions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.capa_actions TO api_server;
GRANT ALL ON TABLE public.capa_actions TO dev_users;


--
-- TOC entry 3668 (class 0 OID 0)
-- Dependencies: 191
-- Name: SEQUENCE capa_links_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.capa_links_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.capa_links_id_seq TO api_server;


--
-- TOC entry 3669 (class 0 OID 0)
-- Dependencies: 192
-- Name: TABLE capa_links; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.capa_links TO api_server;
GRANT ALL ON TABLE public.capa_links TO dev_users;


--
-- TOC entry 3670 (class 0 OID 0)
-- Dependencies: 193
-- Name: SEQUENCE capas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.capas_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.capas_id_seq TO api_server;


--
-- TOC entry 3671 (class 0 OID 0)
-- Dependencies: 194
-- Name: TABLE capas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.capas TO api_server;
GRANT ALL ON TABLE public.capas TO dev_users;


--
-- TOC entry 3672 (class 0 OID 0)
-- Dependencies: 195
-- Name: TABLE consumable_classes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.consumable_classes TO api_server;
GRANT ALL ON TABLE public.consumable_classes TO dev_users;


--
-- TOC entry 3674 (class 0 OID 0)
-- Dependencies: 196
-- Name: SEQUENCE consumable_classes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.consumable_classes_id_seq TO dev_users;
GRANT SELECT,USAGE ON SEQUENCE public.consumable_classes_id_seq TO api_server;


--
-- TOC entry 3675 (class 0 OID 0)
-- Dependencies: 197
-- Name: TABLE consumable_lots; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.consumable_lots TO api_server;
GRANT ALL ON TABLE public.consumable_lots TO dev_users;


--
-- TOC entry 3677 (class 0 OID 0)
-- Dependencies: 198
-- Name: SEQUENCE consumable_lots_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.consumable_lots_id_seq TO dev_users;
GRANT SELECT,USAGE ON SEQUENCE public.consumable_lots_id_seq TO api_server;


--
-- TOC entry 3678 (class 0 OID 0)
-- Dependencies: 199
-- Name: TABLE crm_accounts; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.crm_accounts TO api_server;
GRANT ALL ON TABLE public.crm_accounts TO dev_users;


--
-- TOC entry 3680 (class 0 OID 0)
-- Dependencies: 200
-- Name: SEQUENCE crm_account_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.crm_account_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.crm_account_id_seq TO dev_users;


--
-- TOC entry 3681 (class 0 OID 0)
-- Dependencies: 239
-- Name: SEQUENCE sop_departments_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sop_departments_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sop_departments_id_seq TO api_server;


--
-- TOC entry 3682 (class 0 OID 0)
-- Dependencies: 240
-- Name: TABLE departments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.departments TO api_server;
GRANT ALL ON TABLE public.departments TO dev_users;


--
-- TOC entry 3683 (class 0 OID 0)
-- Dependencies: 256
-- Name: SEQUENCE deviation_reports_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.deviation_reports_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.deviation_reports_id_seq TO api_server;


--
-- TOC entry 3684 (class 0 OID 0)
-- Dependencies: 257
-- Name: TABLE deviation_reports; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.deviation_reports TO api_server;
GRANT ALL ON TABLE public.deviation_reports TO dev_users;


--
-- TOC entry 3685 (class 0 OID 0)
-- Dependencies: 258
-- Name: SEQUENCE deviation_reports_assignments_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.deviation_reports_assignments_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.deviation_reports_assignments_id_seq TO api_server;


--
-- TOC entry 3686 (class 0 OID 0)
-- Dependencies: 259
-- Name: TABLE deviation_reports_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.deviation_reports_assignments TO api_server;
GRANT ALL ON TABLE public.deviation_reports_assignments TO dev_users;


--
-- TOC entry 3687 (class 0 OID 0)
-- Dependencies: 201
-- Name: TABLE equipment; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,TRIGGER,UPDATE ON TABLE public.equipment TO api_server;
GRANT ALL ON TABLE public.equipment TO dev_users;


--
-- TOC entry 3689 (class 0 OID 0)
-- Dependencies: 202
-- Name: SEQUENCE equipment_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON SEQUENCE public.equipment_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.equipment_id_seq TO dev_users;


--
-- TOC entry 3690 (class 0 OID 0)
-- Dependencies: 252
-- Name: SEQUENCE health_canada_report_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.health_canada_report_seq TO dev_users;
GRANT ALL ON SEQUENCE public.health_canada_report_seq TO api_server;


--
-- TOC entry 3691 (class 0 OID 0)
-- Dependencies: 253
-- Name: TABLE health_canada_report; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.health_canada_report TO dev_users;
GRANT ALL ON TABLE public.health_canada_report TO api_server;


--
-- TOC entry 3692 (class 0 OID 0)
-- Dependencies: 203
-- Name: TABLE inventories; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.inventories TO api_server;
GRANT ALL ON TABLE public.inventories TO dev_users;


--
-- TOC entry 3694 (class 0 OID 0)
-- Dependencies: 204
-- Name: SEQUENCE inventories_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.inventories_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.inventories_id_seq TO dev_users;


--
-- TOC entry 3695 (class 0 OID 0)
-- Dependencies: 270
-- Name: SEQUENCE invoices_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.invoices_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.invoices_id_seq TO api_server;


--
-- TOC entry 3696 (class 0 OID 0)
-- Dependencies: 271
-- Name: TABLE invoices; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.invoices TO api_server;
GRANT ALL ON TABLE public.invoices TO dev_users;


--
-- TOC entry 3697 (class 0 OID 0)
-- Dependencies: 205
-- Name: SEQUENCE order_items_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.order_items_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.order_items_id_seq TO api_server;


--
-- TOC entry 3698 (class 0 OID 0)
-- Dependencies: 206
-- Name: TABLE order_items; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.order_items TO api_server;
GRANT ALL ON TABLE public.order_items TO dev_users;


--
-- TOC entry 3699 (class 0 OID 0)
-- Dependencies: 207
-- Name: SEQUENCE orders_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.orders_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.orders_id_seq TO api_server;


--
-- TOC entry 3700 (class 0 OID 0)
-- Dependencies: 208
-- Name: TABLE orders; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.orders TO api_server;
GRANT ALL ON TABLE public.orders TO dev_users;


--
-- TOC entry 3701 (class 0 OID 0)
-- Dependencies: 209
-- Name: TABLE organizations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.organizations TO api_server;
GRANT ALL ON TABLE public.organizations TO dev_users;


--
-- TOC entry 3703 (class 0 OID 0)
-- Dependencies: 210
-- Name: SEQUENCE organizations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.organizations_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.organizations_id_seq TO dev_users;


--
-- TOC entry 3704 (class 0 OID 0)
-- Dependencies: 233
-- Name: SEQUENCE recalls_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.recalls_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.recalls_id_seq TO api_server;


--
-- TOC entry 3705 (class 0 OID 0)
-- Dependencies: 234
-- Name: TABLE recalls; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.recalls TO api_server;
GRANT ALL ON TABLE public.recalls TO dev_users;


--
-- TOC entry 3706 (class 0 OID 0)
-- Dependencies: 211
-- Name: TABLE rooms; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.rooms TO api_server;
GRANT ALL ON TABLE public.rooms TO dev_users;


--
-- TOC entry 3708 (class 0 OID 0)
-- Dependencies: 212
-- Name: SEQUENCE rooms_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.rooms_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.rooms_id_seq TO dev_users;


--
-- TOC entry 3709 (class 0 OID 0)
-- Dependencies: 213
-- Name: TABLE rules; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.rules TO api_server;
GRANT ALL ON TABLE public.rules TO dev_users;


--
-- TOC entry 3711 (class 0 OID 0)
-- Dependencies: 214
-- Name: SEQUENCE rules_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.rules_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.rules_id_seq TO dev_users;


--
-- TOC entry 3712 (class 0 OID 0)
-- Dependencies: 264
-- Name: SEQUENCE sensor_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sensor_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sensor_id_seq TO api_server;


--
-- TOC entry 3713 (class 0 OID 0)
-- Dependencies: 265
-- Name: TABLE sensors_data; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sensors_data TO api_server;
GRANT ALL ON TABLE public.sensors_data TO dev_users;


--
-- TOC entry 3714 (class 0 OID 0)
-- Dependencies: 215
-- Name: SEQUENCE shipment_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.shipment_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.shipment_id_seq TO api_server;


--
-- TOC entry 3715 (class 0 OID 0)
-- Dependencies: 216
-- Name: TABLE shipments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.shipments TO api_server;
GRANT ALL ON TABLE public.shipments TO dev_users;


--
-- TOC entry 3716 (class 0 OID 0)
-- Dependencies: 243
-- Name: SEQUENCE signatures_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.signatures_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.signatures_id_seq TO api_server;


--
-- TOC entry 3717 (class 0 OID 0)
-- Dependencies: 244
-- Name: TABLE signatures; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.signatures TO api_server;
GRANT ALL ON TABLE public.signatures TO dev_users;


--
-- TOC entry 3718 (class 0 OID 0)
-- Dependencies: 217
-- Name: TABLE skus; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.skus TO api_server;
GRANT ALL ON TABLE public.skus TO dev_users;


--
-- TOC entry 3720 (class 0 OID 0)
-- Dependencies: 218
-- Name: SEQUENCE skus_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.skus_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.skus_id_seq TO dev_users;


--
-- TOC entry 3721 (class 0 OID 0)
-- Dependencies: 242
-- Name: TABLE sop_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sop_assignments TO api_server;
GRANT ALL ON TABLE public.sop_assignments TO dev_users;


--
-- TOC entry 3723 (class 0 OID 0)
-- Dependencies: 250
-- Name: SEQUENCE sop_assignments_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sop_assignments_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sop_assignments_id_seq TO api_server;


--
-- TOC entry 3724 (class 0 OID 0)
-- Dependencies: 237
-- Name: SEQUENCE sop_versions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sop_versions_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sop_versions_id_seq TO api_server;


--
-- TOC entry 3725 (class 0 OID 0)
-- Dependencies: 238
-- Name: TABLE sop_versions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sop_versions TO api_server;
GRANT ALL ON TABLE public.sop_versions TO dev_users;


--
-- TOC entry 3726 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE sop_versions_departments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sop_versions_departments TO api_server;
GRANT ALL ON TABLE public.sop_versions_departments TO dev_users;


--
-- TOC entry 3728 (class 0 OID 0)
-- Dependencies: 251
-- Name: SEQUENCE sop_versions_departments_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sop_versions_departments_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sop_versions_departments_id_seq TO api_server;


--
-- TOC entry 3729 (class 0 OID 0)
-- Dependencies: 235
-- Name: SEQUENCE sops_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.sops_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.sops_id_seq TO api_server;


--
-- TOC entry 3730 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE sops; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sops TO api_server;
GRANT ALL ON TABLE public.sops TO dev_users;


--
-- TOC entry 3731 (class 0 OID 0)
-- Dependencies: 273
-- Name: TABLE srfax; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.srfax TO api_server;
GRANT ALL ON TABLE public.srfax TO dev_users;


--
-- TOC entry 3733 (class 0 OID 0)
-- Dependencies: 254
-- Name: SEQUENCE taxes_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.taxes_seq TO dev_users;
GRANT ALL ON SEQUENCE public.taxes_seq TO api_server;


--
-- TOC entry 3734 (class 0 OID 0)
-- Dependencies: 255
-- Name: TABLE taxes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.taxes TO dev_users;
GRANT ALL ON TABLE public.taxes TO api_server;


--
-- TOC entry 3735 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE taxonomies; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.taxonomies TO api_server;
GRANT ALL ON TABLE public.taxonomies TO dev_users;


--
-- TOC entry 3737 (class 0 OID 0)
-- Dependencies: 220
-- Name: SEQUENCE taxonomies_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.taxonomies_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.taxonomies_id_seq TO dev_users;


--
-- TOC entry 3738 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE taxonomy_options; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.taxonomy_options TO api_server;
GRANT ALL ON TABLE public.taxonomy_options TO dev_users;


--
-- TOC entry 3740 (class 0 OID 0)
-- Dependencies: 222
-- Name: SEQUENCE taxonomy_options_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.taxonomy_options_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.taxonomy_options_id_seq TO dev_users;


--
-- TOC entry 3741 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE transaction_allocations; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.transaction_allocations TO api_server;
GRANT ALL ON TABLE public.transaction_allocations TO dev_users;


--
-- TOC entry 3743 (class 0 OID 0)
-- Dependencies: 224
-- Name: SEQUENCE transaction_allocations_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.transaction_allocations_id_seq TO dev_users;
GRANT SELECT,USAGE ON SEQUENCE public.transaction_allocations_id_seq TO api_server;


--
-- TOC entry 3744 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE transactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.transactions TO api_server;
GRANT ALL ON TABLE public.transactions TO dev_users;


--
-- TOC entry 3746 (class 0 OID 0)
-- Dependencies: 226
-- Name: SEQUENCE transactions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.transactions_id_seq TO dev_users;
GRANT SELECT,USAGE ON SEQUENCE public.transactions_id_seq TO api_server;


--
-- TOC entry 3747 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE uploads; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.uploads TO api_server;
GRANT ALL ON TABLE public.uploads TO dev_users;


--
-- TOC entry 3749 (class 0 OID 0)
-- Dependencies: 228
-- Name: SEQUENCE uploads_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.uploads_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.uploads_id_seq TO dev_users;


--
-- TOC entry 3750 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,UPDATE ON TABLE public.users TO api_server;
GRANT ALL ON TABLE public.users TO dev_users;


--
-- TOC entry 3752 (class 0 OID 0)
-- Dependencies: 230
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.users_id_seq TO api_server;
GRANT ALL ON SEQUENCE public.users_id_seq TO dev_users;


--
-- TOC entry 3753 (class 0 OID 0)
-- Dependencies: 260
-- Name: TABLE vw_deviation_reports_with_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_deviation_reports_with_assignments TO api_server;
GRANT ALL ON TABLE public.vw_deviation_reports_with_assignments TO dev_users;


--
-- TOC entry 3754 (class 0 OID 0)
-- Dependencies: 261
-- Name: TABLE vw_mother_with_mother_batch_id; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_mother_with_mother_batch_id TO api_server;
GRANT ALL ON TABLE public.vw_mother_with_mother_batch_id TO dev_users;


--
-- TOC entry 3755 (class 0 OID 0)
-- Dependencies: 246
-- Name: TABLE vw_sop_versions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_sop_versions TO api_server;
GRANT ALL ON TABLE public.vw_sop_versions TO dev_users;


--
-- TOC entry 3756 (class 0 OID 0)
-- Dependencies: 249
-- Name: TABLE vw_sop_assignments; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_sop_assignments TO api_server;
GRANT ALL ON TABLE public.vw_sop_assignments TO dev_users;


--
-- TOC entry 3757 (class 0 OID 0)
-- Dependencies: 245
-- Name: TABLE vw_sops; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_sops TO api_server;
GRANT ALL ON TABLE public.vw_sops TO dev_users;


--
-- TOC entry 3758 (class 0 OID 0)
-- Dependencies: 247
-- Name: TABLE vw_sop_logs; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_sop_logs TO api_server;
GRANT ALL ON TABLE public.vw_sop_logs TO dev_users;


--
-- TOC entry 3759 (class 0 OID 0)
-- Dependencies: 248
-- Name: TABLE vw_sop_notifications; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_sop_notifications TO api_server;
GRANT ALL ON TABLE public.vw_sop_notifications TO dev_users;


--
-- TOC entry 3760 (class 0 OID 0)
-- Dependencies: 262
-- Name: SEQUENCE webhook_subscriptions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.webhook_subscriptions_id_seq TO dev_users;
GRANT ALL ON SEQUENCE public.webhook_subscriptions_id_seq TO api_server;


--
-- TOC entry 3761 (class 0 OID 0)
-- Dependencies: 263
-- Name: TABLE webhook_subscriptions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.webhook_subscriptions TO api_server;
GRANT ALL ON TABLE public.webhook_subscriptions TO dev_users;


--
-- TOC entry 3762 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE sensors; Type: ACL; Schema: sensor_data; Owner: postgres
--

GRANT ALL ON TABLE sensor_data.sensors TO api_server WITH GRANT OPTION;
GRANT ALL ON TABLE sensor_data.sensors TO dev_users;


--
-- TOC entry 3764 (class 0 OID 0)
-- Dependencies: 232
-- Name: SEQUENCE sensors_id_seq; Type: ACL; Schema: sensor_data; Owner: postgres
--

GRANT ALL ON SEQUENCE sensor_data.sensors_id_seq TO dev_users;


-- Completed on 2022-02-18 19:58:13 UTC

--
-- PostgreSQL database dump complete
--

