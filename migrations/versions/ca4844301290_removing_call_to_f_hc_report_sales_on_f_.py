"""removing call to f_hc_report_sales on f_hc_report function

Revision ID: ca4844301290
Revises: dab98dcf4738
Create Date: 2022-09-15 17:16:52.037132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca4844301290'
down_revision = 'dab98dcf4738'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
CREATE OR REPLACE FUNCTION public.f_hc_report(month_period character varying, year_period character varying, org_id integer, create_by_id integer, OUT report_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
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
                SELECT to_timestamp(CONCAT(year_period,'-',month_period,'-01 00:00:00'), 'YYYY-MM-DD H:M:S') INTO initial_date;
                raise notice 'initial date: %%', initial_date;

                -- get the last day of the month
                SELECT to_timestamp(initial_date, 'YYYY-MM-DD H:M:S') 
                                + interval '1 month'
                                - interval '1 seconds' into final_date;
                raise notice 'final date: %%', final_date;

    

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
                raise notice 'report id: %%', report_id;

                --FUNCTIONS
                PERFORM f_hc_report_inventory(report_id, initial_date, final_date, org_id);
                --PERFORM f_hc_report_sales(report_id, initial_date, final_date, org_id);

        END;$function$
;

        """)


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
CREATE OR REPLACE FUNCTION public.f_hc_report(month_period character varying, year_period character varying, org_id integer, create_by_id integer, OUT report_id integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
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
                SELECT to_timestamp(CONCAT(year_period,'-',month_period,'-01 00:00:00'), 'YYYY-MM-DD H:M:S') INTO initial_date;
                raise notice 'initial date: %%', initial_date;

                -- get the last day of the month
                SELECT to_timestamp(initial_date, 'YYYY-MM-DD H:M:S') 
                                + interval '1 month'
                                - interval '1 seconds' into final_date;
                raise notice 'final date: %%', final_date;

    

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
                raise notice 'report id: %%', report_id;

                --FUNCTIONS
                PERFORM f_hc_report_inventory(report_id, initial_date, final_date, org_id);
                PERFORM f_hc_report_sales(report_id, initial_date, final_date, org_id);

        END;$function$
;

-- Permissions

ALTER FUNCTION public.f_hc_report(in varchar, in varchar, in int4, in int4, out int4) OWNER TO migration_runner;
GRANT ALL ON FUNCTION public.f_hc_report(in varchar, in varchar, in int4, in int4, out int4) TO migration_runner;


        """)
