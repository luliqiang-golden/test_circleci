"""adds purchased hemp HCR

Revision ID: 01510c41af44
Revises: 1322ab9d5794
Create Date: 2022-10-12 17:33:40.123372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01510c41af44'
down_revision = '1322ab9d5794'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
        
        -- public.health_canada_report definition

-- Drop table

DROP TABLE public.health_canada_report;

CREATE TABLE public.health_canada_report (
	id int8 NOT NULL DEFAULT nextval('health_canada_report_seq'::regclass),
	"timestamp" timestamptz NOT NULL DEFAULT now(),
	created_by int4 NOT NULL,
	organization_id int4 NOT NULL,
	"data" jsonb NULL DEFAULT '{}'::jsonb,
	report_period_year varchar NOT NULL,
	report_period_month varchar NOT NULL,
	province varchar NULL,
	"type" varchar NULL,
	company_name varchar NULL,
	site_id varchar NULL,
	city varchar NULL,
	postal_code varchar NULL,
	license_id varchar NULL,
	total_buildings_area numeric NULL DEFAULT 0,
	licensed_growing_area numeric NULL DEFAULT 0,
	licensed_processing_area numeric NULL DEFAULT 0,
	licensed_outdoor_growing_area numeric NULL DEFAULT 0,
	unpackaged_seed_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_opening_inventory numeric NULL DEFAULT 0,
	packaged_seed_opening_inventory numeric NULL DEFAULT 0,
	packaged_vegetative_plants_opening_inventory numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_opening_inventory numeric NULL DEFAULT 0,
	packaged_dried_cannabis_opening_inventory numeric NULL DEFAULT 0,
	packaged_extracts_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_seed_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_vegetative_cannabis_plants_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_closing_inventory numeric NULL DEFAULT 0,
	packaged_seed_closing_inventory numeric NULL DEFAULT 0,
	packaged_vegetative_cannabis_plants_closing_inventory numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_closing_inventory numeric NULL DEFAULT 0,
	packaged_dried_cannabis_closing_inventory numeric NULL DEFAULT 0,
	packaged_extracts_closing_inventory numeric NULL DEFAULT 0,
	packaged_seed_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_dried_cannabis_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_extracts_closing_inventory_weight numeric NULL DEFAULT 0,
	unpackaged_seed_received_domestic numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_received_domestic numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_received_domestic numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_received_domestic numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_received_domestic numeric NULL DEFAULT 0,
	unpackaged_seed_received_imported numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_received_imported numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_received_imported numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_received_imported numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_received_imported numeric NULL DEFAULT 0,
	unpackaged_extracts_received_imported numeric NULL DEFAULT 0,
	unpackaged_seed_received_returned numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_received_returned numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_received_returned numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_received_returned numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_received_returned numeric NULL DEFAULT 0,
	unpackaged_extracts_received_returned numeric NULL DEFAULT 0,
	packaged_seed_received_domestic numeric NULL DEFAULT 0,
	packaged_vegetative_plants_received_domestic numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_received_domestic numeric NULL DEFAULT 0,
	packaged_dried_cannabis_received_domestic numeric NULL DEFAULT 0,
	packaged_extracts_received_domestic numeric NULL DEFAULT 0,
	packaged_seed_received_returned numeric NULL DEFAULT 0,
	packaged_vegetative_plants_received_returned numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_received_returned numeric NULL DEFAULT 0,
	packaged_dried_cannabis_received_returned numeric NULL DEFAULT 0,
	packaged_extracts_received_returned numeric NULL DEFAULT 0,
	unpackaged_seed_packaged_label numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_packaged_label numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_packaged_label numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_packaged_label numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_packaged_label numeric NULL DEFAULT 0,
	unpackaged_extracts_packaged_label numeric NULL DEFAULT 0,
	packaged_seed_quantity_packaged numeric NULL DEFAULT 0,
	packaged_vegetative_plants_quantity_packaged numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_quantity_packaged numeric NULL DEFAULT 0,
	packaged_dried_cannabis_quantity_packaged numeric NULL DEFAULT 0,
	packaged_extracts_quantity_packaged numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_extracts_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_seed_destroyed numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_destroyed numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_destroyed numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_destroyed numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_destroyed numeric NULL DEFAULT 0,
	unpackaged_extracts_destroyed numeric NULL DEFAULT 0,
	packaged_seed_destroyed numeric NULL DEFAULT 0,
	packaged_vegetative_plants_destroyed numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_destroyed numeric NULL DEFAULT 0,
	packaged_dried_cannabis_destroyed numeric NULL DEFAULT 0,
	packaged_extracts_destroyed numeric NULL DEFAULT 0,
	unpackaged_seed_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_fresh_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_dried_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_extracts_shipped_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_seed_produced numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_produced numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_produced numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_produced numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_produced numeric NULL DEFAULT 0,
	unpackaged_extracts_produced numeric NULL DEFAULT 0,
	unpackaged_seed_processed numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_processed numeric NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_processed numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_processed numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_processed numeric NULL DEFAULT 0,
	packaged_seed_shipped_domestic numeric NULL DEFAULT 0,
	packaged_vegetative_plants_shipped_domestic numeric NULL DEFAULT 0,
	packaged_fresh_cannabis_shipped_domestic numeric NULL DEFAULT 0,
	packaged_dried_cannabis_shipped_domestic numeric NULL DEFAULT 0,
	packaged_extracts_shipped_domestic numeric NULL DEFAULT 0,
	packaged_edibles_solid_shipped_domestic numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_shipped_domestic numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_shipped_domestic numeric NULL DEFAULT 0,
	packaged_extracts_ingested_shipped_domestic numeric NULL DEFAULT 0,
	packaged_extracts_other_shipped_domestic numeric NULL DEFAULT 0,
	packaged_topicals_shipped_domestic numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_other_additions numeric NULL DEFAULT 0,
	unpackaged_seed_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_vegetative_plants_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_fresh_cannabis_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_dried_cannabis_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_extracts_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_extracts_other_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_topicals_reductions_shipped_returned numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_received_domestic numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_other_received_domestic numeric NULL DEFAULT 0,
	unpackaged_topicals_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_received_imported numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_received_imported numeric NULL DEFAULT 0,
	unpackaged_extracts_other_received_imported numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_received_imported numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_received_imported numeric NULL DEFAULT 0,
	unpackaged_topicals_received_imported numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_received_domestic numeric NULL DEFAULT 0,
	packaged_extracts_ingested_received_domestic numeric NULL DEFAULT 0,
	packaged_extracts_other_received_domestic numeric NULL DEFAULT 0,
	packaged_edibles_solid_received_domestic numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_received_domestic numeric NULL DEFAULT 0,
	packaged_topicals_received_domestic numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_other_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_closing_inventory numeric NULL DEFAULT 0,
	unpackaged_topicals_closing_inventory numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_closing_inventory numeric NULL DEFAULT 0,
	packaged_extracts_ingested_closing_inventory numeric NULL DEFAULT 0,
	packaged_extracts_other_closing_inventory numeric NULL DEFAULT 0,
	packaged_edibles_solid_closing_inventory numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_closing_inventory numeric NULL DEFAULT 0,
	packaged_topicals_closing_inventory numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_extracts_ingested_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_extracts_other_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_edibles_solid_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_closing_inventory_weight numeric NULL DEFAULT 0,
	packaged_topicals_inventory_closing_weight numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_extracts_other_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_topicals_opening_inventory numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_opening_inventory numeric NULL DEFAULT 0,
	packaged_extracts_ingested_opening_inventory numeric NULL DEFAULT 0,
	packaged_extracts_other_opening_inventory numeric NULL DEFAULT 0,
	packaged_edibles_solid_opening_inventory numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_opening_inventory numeric NULL DEFAULT 0,
	packaged_topicals_opening_inventory numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_processed numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_processed numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_processed numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_processed numeric NULL DEFAULT 0,
	unpackaged_extracts_other_processed numeric NULL DEFAULT 0,
	unpackaged_topicals_processed numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_produced numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_produced numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_produced numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_produced numeric NULL DEFAULT 0,
	unpackaged_extracts_other_produced numeric NULL DEFAULT 0,
	unpackaged_topicals_produced numeric NULL DEFAULT 0,
	unpackaged_pure_intermediate_reductions_other numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_extracts_other_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_topicals_adjustment_loss numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_destroyed numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_destroyed numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_destroyed numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_destroyed numeric NULL DEFAULT 0,
	unpackaged_extracts_other_destroyed numeric NULL DEFAULT 0,
	unpackaged_topicals_destroyed numeric NULL DEFAULT 0,
	packaged_edibles_solid_destroyed numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_destroyed numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_destroyed numeric NULL DEFAULT 0,
	packaged_extracts_ingested_destroyed numeric NULL DEFAULT 0,
	packaged_extracts_other_destroyed numeric NULL DEFAULT 0,
	packaged_topicals_destroyed numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_extracts_other_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_topicals_analytical_testers numeric NULL DEFAULT 0,
	unpackaged_edibles_solid_packaged_label numeric NULL DEFAULT 0,
	unpackaged_edibles_nonsolid_packaged_label numeric NULL DEFAULT 0,
	unpackaged_inhaled_packaged_label numeric NULL DEFAULT 0,
	unpackaged_ingested_packaged_label numeric NULL DEFAULT 0,
	unpackaged_other_packaged_label numeric NULL DEFAULT 0,
	unpackaged_topicals_packaged_label numeric NULL DEFAULT 0,
	packaged_edibles_solid_quantity_packaged numeric NULL DEFAULT 0,
	packaged_edibles_nonsolid_quantity_packaged numeric NULL DEFAULT 0,
	packaged_inhaled_quantity_packaged numeric NULL DEFAULT 0,
	packaged_ingested_quantity_packaged numeric NULL DEFAULT 0,
	packaged_other_quantity_packaged numeric NULL DEFAULT 0,
	packaged_topicals_quantity_packaged numeric NULL DEFAULT 0,
	packaged_extracts_inhaled_quantity_packaged numeric NULL DEFAULT 0,
	packaged_extracts_ingested_quantity_packaged numeric NULL DEFAULT 0,
	packaged_extracts_other_quantity_packaged numeric NULL DEFAULT 0,
	unpackaged_extracts_inhaled_packaged_label numeric NULL DEFAULT 0,
	unpackaged_extracts_ingested_packaged_label numeric NULL DEFAULT 0,
	unpackaged_extracts_other_packaged_label numeric NULL DEFAULT 0,
	packaged_topicals_closing_inventory_weight numeric NULL DEFAULT 0,
	unpackaged_other_shipped_analytical_testers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_produced numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_opening_inventory numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_closing_inventory numeric(14, 3) NULL DEFAULT 0,
	unpackaged_seed_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_vegetative_plants_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_fresh_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_dried_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_ingested_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_ingested_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_seeds_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_seeds_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_vegetative_cannabis_plants_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_vegetative_cannabis_plants_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_fresh_cannabis_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_fresh_cannabis_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_dried_cannabis_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_dried_cannabis_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_solids_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_solids_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_solids_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_solids_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_nonsolids_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_nonsolids_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_nonsolids_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_edibles_nonsolids_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_inhaled_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_inhaled_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_inhaled_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_inhaled_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_ingested_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_ingested_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_other_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_other_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_other_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_other_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_topicals_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_topicals_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_topicals_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_topicals_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_other_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_seed_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_vegetative_plants_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_whole_cannabis_plants_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_fresh_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_dried_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_extracts_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_opening_inventory numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_received_domestic numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_received_imported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_received_other numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_processed numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_packaged_label numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_shipped_analytical_testers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_shipped_researchers numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_shipped_cultivators_processors numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_shipped_exported numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_shipped_exported_value numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_reductions_shipped_returned numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_adjustment_loss numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_destroyed numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_closing_inventory numeric(14, 3) NULL DEFAULT 0,
	unpackaged_purchased_hemp_closing_inventory_value numeric(14, 3) NULL DEFAULT 0,
	CONSTRAINT hcr_pkey PRIMARY KEY (id)
);


-- public.health_canada_report foreign keys

ALTER TABLE public.health_canada_report ADD CONSTRAINT hcr_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id);
ALTER TABLE public.health_canada_report ADD CONSTRAINT hcr_user FOREIGN KEY (created_by) REFERENCES public.users(id);








do $$
DECLARE
row record;
taxonomy_id numeric;
begin 
for row in (SELECT id FROM organizations) loop
taxonomy_id := (SELECT id FROM taxonomies where name = 'stats' and organization_id = row.id);
IF(taxonomy_id IS NOT NULL) THEN
INSERT INTO public.taxonomy_options (organization_id, created_by, "timestamp", "name", "data", taxonomy_id) VALUES(row.id, 1, '2022-09-23 11:02:01.469', 'purchasedHemp', '{"type": "standard", "parent": "", "stages": ["planning"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "purchased hemp", "cannabisClass": "purchased hemp", "reportSection": "purchased_hemp", "isFinalProduct": true}'::jsonb, taxonomy_id);
END IF;
end loop;
end;
$$;


















DROP FUNCTION f_serialize_stats_fields(numeric,character varying,character varying,character varying,character varying,character varying,character varying,jsonb,jsonb,character varying);















CREATE OR REPLACE FUNCTION public.f_serialize_stats_fields(quantity numeric, unit character varying, stage character varying, from_qty_unit character varying, type character varying, p_package_type character varying, p_shipping_status character varying, data jsonb DEFAULT NULL::jsonb, attributes jsonb DEFAULT NULL::jsonb, taxonomy_subtype character varying DEFAULT NULL::character varying, OUT seeds_qty numeric, OUT packaged_seeds_qty numeric, OUT seeds_weight numeric, OUT whole_plants numeric, OUT vegetative_plants numeric, OUT packaged_vegetative_plants_qty numeric, OUT fresh_cannabis_weight numeric, OUT purchased_hemp_weight numeric, OUT dried_cannabis_weight numeric, OUT extracts_weight numeric, OUT extracts_inhaled_weight numeric, OUT extracts_ingested_weight numeric, OUT extracts_other_weight numeric, OUT edibles_solid_weight numeric, OUT edibles_non_solid_weight numeric, OUT topicals_weight numeric, OUT fresh_cannabis_qty numeric, OUT purchased_hemp_qty numeric, OUT dried_cannabis_qty numeric, OUT extracts_qty numeric, OUT extracts_inhaled_qty numeric, OUT extracts_ingested_qty numeric, OUT extracts_other_qty numeric, OUT edibles_solid_qty numeric, OUT edibles_non_solid_qty numeric, OUT topicals_qty numeric, OUT package_type character varying, OUT shipping_status character varying, OUT other_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    plants DECIMAL;
    dry DECIMAL;
    cured DECIMAL;
    distilled DECIMAL;
    crude DECIMAL;
    cannabinoid DECIMAL;
    sift DECIMAL;
    terpene DECIMAL;
    biomass DECIMAL;
BEGIN
	
	shipping_status = p_shipping_status;
	
	package_type := 'unpackage';
	
    seeds_qty := 0;
    IF (unit = 'seeds') THEN
        seeds_qty := GREATEST(0,quantity);
    END IF;

    IF (seeds_qty > 0) THEN
        IF (type = 'received inventory') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(data->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
        ELSIF (type = 'batch') THEN
            IF (attributes->>'seed_weight' IS NOT NULL) THEN
                seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seed_weight' AS DECIMAL), 0)) * seeds_qty;
            ELSE
                seeds_weight := GREATEST(0,COALESCE(CAST(attributes->>'seeds_weight' AS DECIMAL), 0));
            END IF;
        ELSIF (type = 'sample') THEN
            seeds_weight := GREATEST(0,COALESCE(CAST(data->>'seeds_weight' AS DECIMAL), 0));
        ELSE
            seeds_weight := 0;
        END IF;
    END IF;

    plants := 0;
    IF (unit = 'plants') THEN
        plants := GREATEST(0,quantity);
    END IF;

    IF (plants > 0) THEN
            IF ((stage in ('planning', 'propagation', 'germinating', 'vegetation') OR type IN ('received inventory', 'mother', 'mother batch', 'lot', 'lot item'))) OR (data->'plan'->>'end_type'='plants') THEN
                vegetative_plants := plants;
            ELSE
                whole_plants := plants;
            END IF;
    END IF;

    fresh_cannabis_weight := 0;
    IF (unit = 'g-wet' AND (from_qty_unit != 'plants' OR from_qty_unit IS NULL)) THEN
        fresh_cannabis_weight := GREATEST(0,quantity);
    END IF;
   
   	purchased_hemp_weight := 0;
  	IF (unit = 'purchasedHemp') THEN
        purchased_hemp_weight := GREATEST(0,quantity);
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
	
	cannabinoid := 0;
    IF (unit = 'cannabinoid') THEN
        cannabinoid := GREATEST(0,quantity);
    END IF;
	
	sift := 0;
    IF (unit = 'sift') THEN
        sift := GREATEST(0,quantity);
    END IF;
	
	terpene := 0;
    IF (unit = 'terpene') THEN
        terpene := GREATEST(0,quantity);
    END IF;
	
	biomass := 0;
    IF (unit = 'biomass') THEN
        biomass := GREATEST(0,quantity);
    END IF;

    extracts_weight := distilled + crude; --+ cannabinoid + sift + terpene + biomass;
    
    extracts_inhaled_weight := 0;
    IF (taxonomy_subtype = 'inhaled') THEN
        extracts_inhaled_weight := GREATEST(0,quantity);
    END IF;

    extracts_ingested_weight := 0;
    IF (taxonomy_subtype = 'ingested' AND (unit NOT IN ('crude', 'distilled') OR (unit IN ('crude', 'distilled') AND type = 'lot item' AND p_package_type != 'unpackaged'))) THEN
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

   	other_weight := 0;
   	IF(type = 'sample' AND unit = 'g-wet' AND from_qty_unit = 'plants') THEN 
   		other_weight := GREATEST(0,quantity);
   	END IF;


    IF (type = 'lot item') then
    	
    	if(p_package_type = 'packaged') then
    		package_type = 'package';
    	else
    		package_type = 'unpackage';
    	end if;
    
        IF (fresh_cannabis_weight > 0) THEN
            fresh_cannabis_qty := 1;
        ELSIF (dried_cannabis_weight > 0) THEN
            dried_cannabis_qty := 1;
        --ELSIF (extracts_weight > 0) THEN
        --    extracts_qty := 1;
        ELSIF (plants > 0) THEN
            packaged_vegetative_plants_qty := 1;

        ELSIF (extracts_inhaled_weight > 0) THEN
            extracts_inhaled_qty := 1;
        ELSIF (extracts_ingested_weight > 0) THEN
            extracts_ingested_qty := 1;
        ELSIF (extracts_other_weight > 0  AND (unit NOT IN ('cannabinoid', 'sift', 'terpene', 'biomass'))) THEN
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
$function$
;









DROP FUNCTION f_get_current_inventory(character varying,integer);








CREATE OR REPLACE FUNCTION public.f_get_current_inventory(final_date character varying, org_id integer, OUT unpackaged_seed_inventory numeric, OUT unpackaged_vegetative_plants_inventory numeric, OUT unpackaged_whole_cannabis_plants_inventory numeric, OUT unpackaged_fresh_cannabis_inventory numeric, OUT unpackaged_purchased_hemp_inventory numeric, OUT unpackaged_extracts_inventory numeric, OUT unpackaged_dried_cannabis_inventory numeric, OUT packaged_seed_inventory numeric, OUT packaged_vegetative_plants_inventory numeric, OUT packaged_fresh_cannabis_inventory numeric, OUT packaged_dried_cannabis_inventory numeric, OUT packaged_extracts_inventory numeric, OUT unpackaged_extracts_inhaled_inventory numeric, OUT unpackaged_extracts_ingested_inventory numeric, OUT unpackaged_extracts_other_inventory numeric, OUT unpackaged_edibles_solid_inventory numeric, OUT unpackaged_edibles_nonsolid_inventory numeric, OUT unpackaged_topicals_inventory numeric, OUT unpackaged_other_inventory numeric, OUT packaged_extracts_inhaled_inventory numeric, OUT packaged_extracts_ingested_inventory numeric, OUT packaged_extracts_other_inventory numeric, OUT packaged_edibles_solid_inventory numeric, OUT packaged_edibles_nonsolid_inventory numeric, OUT packaged_topicals_inventory numeric, OUT packaged_seed_inventory_weight numeric, OUT packaged_fresh_cannabis_inventory_weight numeric, OUT packaged_dried_cannabis_inventory_weight numeric, OUT packaged_extracts_inventory_weight numeric, OUT packaged_extracts_inhaled_inventory_weight numeric, OUT packaged_extracts_ingested_inventory_weight numeric, OUT packaged_extracts_other_inventory_weight numeric, OUT packaged_edibles_solid_inventory_weight numeric, OUT packaged_edibles_nonsolid_inventory_weight numeric, OUT packaged_topicals_inventory_weight numeric)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
            DECLARE
                initial_date character varying;
                final_day numeric;
            BEGIN	
                SELECT TO_CHAR(MIN(timestamp), 'YYYY-MM-DD') FROM public.inventories INTO initial_date;
				
                            
                SELECT 
                    -- unpackage (kg)
                    SUM(COALESCE((f).seeds_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_seed_inventory,
                    SUM(COALESCE((f).vegetative_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_vegetative_plants_inventory,		
                    SUM(COALESCE((f).whole_plants,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_whole_cannabis_plants_inventory,
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).purchased_hemp_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_purchased_hemp_inventory,
                    SUM(COALESCE((f).dried_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_topicals_inventory,
                    SUM(COALESCE((f).other_weight, 0)) FILTER (WHERE (f).package_type ='unpackage') AS unpackaged_other_inventory,
                    
                    -- packaged (#)
                    SUM(COALESCE((f).packaged_seeds_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_seed_inventory,
                    SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_vegetative_plants_inventory,				
                    SUM(COALESCE((f).fresh_cannabis_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_fresh_cannabis_inventory,
                    SUM(COALESCE((f).dried_cannabis_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_dried_cannabis_inventory,
                    SUM(COALESCE((f).extracts_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_inventory,
                    
                    SUM(COALESCE((f).extracts_inhaled_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_inhaled_inventory,
                    SUM(COALESCE((f).extracts_ingested_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_ingested_inventory,
                    SUM(COALESCE((f).extracts_other_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_other_inventory,
                    SUM(COALESCE((f).edibles_solid_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_edibles_solid_inventory,
                    SUM(COALESCE((f).edibles_non_solid_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_edibles_nonsolid_inventory,
                    SUM(COALESCE((f).topicals_qty, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_topicals_inventory,
                    
                    
                    -- packaged weight(#)
                    SUM(COALESCE((f).seeds_qty,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_seed_inventory_weight, -- total number of seeds
                    SUM(COALESCE((f).fresh_cannabis_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_fresh_cannabis_inventory_weight,
                    SUM(COALESCE((f).dried_cannabis_weight,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_dried_cannabis_inventory_weight,
                    SUM(COALESCE((f).extracts_weight,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_inventory_weight,
                    
                    SUM(COALESCE((f).extracts_inhaled_weight,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_inhaled_inventory_weight,
                    SUM(COALESCE((f).extracts_ingested_weight,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_ingested_inventory_weight,
                    SUM(COALESCE((f).extracts_other_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_extracts_other_inventory_weight,
                    SUM(COALESCE((f).edibles_solid_weight,0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_edibles_solid_inventory_weight,
                    SUM(COALESCE((f).edibles_non_solid_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_edibles_nonsolid_inventory_weight,
                    SUM(COALESCE((f).topicals_weight, 0)) FILTER (WHERE (f).package_type ='package' AND (f).shipping_status IS NULL) AS packaged_topicals_inventory_weight
            
                FROM (
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv 
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1)  
                    WHERE inv.latest_quantity > 0 and
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) AND
                        type in ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    --samples that have not been sent to the lab and do not come from plants
                    SELECT f_serialize_stats_fields(inv.latest_quantity, inv.latest_unit, inv.latest_stage, inv.from_qty_unit, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f, inv.type, inv.data
                    FROM f_inventories_latest_stats_stage(final_date, org_id) as inv
                    --FROM f_inventories_latest_stats_stage('2020-05-31', 1) as inv
                    inner join stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    INNER JOIN (
                        SELECT 
                            CAST(sample_activity.data->>'inventory_id' AS bigint) as id,
                            MAX(sample_activity.id) AS act_id
                        FROM activities AS sample_activity
                        WHERE 
                            sample_activity.name in ('create_sample', 'sample_sent_to_lab') 
                            AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= final_date
                            --AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= '2020-05-31'
                            --AND sample_activity.data->>'from_qty_unit' != 'plants'
                        GROUP BY sample_activity.data->>'inventory_id'
                    ) AS latest_activity ON inv.id = latest_activity.id
                    INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='create_sample' 
                    WHERE inv.latest_quantity > 0 AND
                          inv.type ='sample' AND
                        --inv.organization_id = 1 AND
                            --inv.timestamp >= cast('2021-11-01' as date)
                            inv.organization_id = org_id AND
                            inv.timestamp >= cast(initial_date as date) 
                        --inv.organization_id = 1 AND
                        --TO_CHAR(inv.timestamp,'YYYY-MM-DD') BETWEEN '2019-05-31' AND '2020-05-31' 
                        
            
                    ) AS T1
                    INTO
                        unpackaged_seed_inventory,
                        unpackaged_vegetative_plants_inventory,		
                        unpackaged_whole_cannabis_plants_inventory,
                        unpackaged_fresh_cannabis_inventory,
                        unpackaged_purchased_hemp_inventory,
                        unpackaged_dried_cannabis_inventory,
                        unpackaged_extracts_inventory,
                        
                        unpackaged_extracts_inhaled_inventory,
                        unpackaged_extracts_ingested_inventory,		
                        unpackaged_extracts_other_inventory,
                        unpackaged_edibles_solid_inventory,
                        unpackaged_edibles_nonsolid_inventory,
                        unpackaged_topicals_inventory,
                        unpackaged_other_inventory,
                        
                        --Packaged (#)
                        packaged_seed_inventory,
                        packaged_vegetative_plants_inventory,				
                        packaged_fresh_cannabis_inventory,
                        packaged_dried_cannabis_inventory,
                        packaged_extracts_inventory,
                        
                        packaged_extracts_inhaled_inventory, 
                        packaged_extracts_ingested_inventory, 
                        packaged_extracts_other_inventory, 
                        packaged_edibles_solid_inventory,
                        packaged_edibles_nonsolid_inventory, 
                        packaged_topicals_inventory,
                        
                        
                        --packaged weight(#)
                        packaged_seed_inventory_weight,
                        packaged_fresh_cannabis_inventory_weight,
                        packaged_dried_cannabis_inventory_weight,
                        packaged_extracts_inventory_weight,
                        
                        packaged_extracts_inhaled_inventory_weight, 
                        packaged_extracts_ingested_inventory_weight, 
                        packaged_extracts_other_inventory_weight, 
                        packaged_edibles_solid_inventory_weight,
                        packaged_edibles_nonsolid_inventory_weight, 
                        packaged_topicals_inventory_weight;
             
            END;$function$
;















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
                   unpackaged_purchased_hemp_closing_inventory = COALESCE(T1.unpackaged_purchased_hemp_inventory,0)/1000,
                   unpackaged_dried_cannabis_closing_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
                   unpackaged_extracts_closing_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
                   unpackaged_extracts_inhaled_closing_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
                   unpackaged_extracts_ingested_closing_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
                   unpackaged_extracts_other_closing_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
                   unpackaged_edibles_solid_closing_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
                   unpackaged_edibles_nonsolid_closing_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
                   unpackaged_topicals_closing_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,
                   unpackaged_other_closing_inventory = COALESCE(T1.unpackaged_other_inventory,0)/1000,
                   
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
                    unpackaged_purchased_hemp_adjustment_loss = coalesce(t3.unpackaged_purchased_hemp_adjustment_loss , 0)/ 1000,
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
                        where t2.type = 'purchased_hemp') as unpackaged_purchased_hemp_adjustment_loss,
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
                                    when name IN ('batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'purchasedHemp' then 'purchased_hemp'
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
                                        when name IN ('batch_record_crude_oil_weight') and data->>'from_qty_unit' = 'purchasedHemp' then 'purchased_hemp'
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









CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_cultivators_processors(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to cultivators and process
	            
            */
	        SET enable_nestloop = off;
	       
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_shipped_cultivators_processors = COALESCE(T2.unpackaged_seed_shipped_cultivators_processors,0),
                unpackaged_vegetative_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_vegetative_plants_shipped_cultivators_processors,0),
                unpackaged_whole_cannabis_plants_shipped_cultivators_processors = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_cultivators_processors,0),
                unpackaged_fresh_shipped_cultivators_processors = COALESCE(T2.unpackaged_fresh_shipped_cultivators_processors,0)/1000,
                unpackaged_purchased_hemp_shipped_cultivators_processors = COALESCE(T2.unpackaged_purchased_hemp_shipped_cultivators_processors,0)/1000,
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
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'purchasedHemp') AS unpackaged_purchased_hemp_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_cultivators_processors,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit IN ('distilled', 'crude', 'biomass', 'terpene', 'sift', 'cannabinoid'))) AS unpackaged_extracts_shipped_cultivators_processors,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested' AND T1.unit NOT IN ('distilled', 'crude')) AS unpackaged_extracts_ingested_shipped_cultivators_processors,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other' AND T1.unit NOT IN ('biomass', 'terpene', 'sift', 'cannabinoid')) AS unpackaged_extracts_other_shipped_cultivators_processors,
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
	        SET enable_nestloop = off;
	       
            UPDATE health_canada_report
            SET 		
                unpackaged_seed_destroyed = COALESCE(T2.unpackaged_seed_destroyed,0)/1000,
                unpackaged_vegetative_plants_destroyed = COALESCE(T2.unpackaged_vegetative_plants_destroyed,0),
                unpackaged_whole_cannabis_plants_destroyed = COALESCE(T2.unpackaged_whole_cannabis_plants_destroyed,0),
                unpackaged_fresh_cannabis_destroyed = COALESCE(T2.unpackaged_fresh_cannabis_destroyed,0)/1000,
                unpackaged_purchased_hemp_destroyed = COALESCE(T2.unpackaged_purchased_hemp_destroyed,0)/1000,
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
                    SUM(COALESCE(T1.quantity, 0)) FILTER (WHERE T1.unit = 'purchasedHemp' AND T1.type != 'lot item') AS unpackaged_purchased_hemp_destroyed,
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





















CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_export(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
        BEGIN		
            /* 
	             sent to researchers
	            
            */
	        SET enable_nestloop = off;
	       
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported = COALESCE(T2.unpackaged_seeds_shipped_exported,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported,0),
                unpackaged_whole_cannabis_plants_shipped_exported = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported,0),
                unpackaged_fresh_cannabis_shipped_exported = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported,0)/1000,
                unpackaged_purchased_hemp_shipped_exported = COALESCE(T2.unpackaged_purchased_hemp_shipped_exported,0)/1000,
                unpackaged_dried_cannabis_shipped_exported = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported,0)/1000,
                unpackaged_extracts_shipped_exported = COALESCE(T2.unpackaged_extracts_shipped_exported,0)/1000,
                
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
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'purchasedHemp') AS unpackaged_purchased_hemp_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit IN ('distilled', 'crude', 'biomass', 'terpene', 'sift', 'cannabinoid'))) AS unpackaged_extracts_shipped_exported,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other' AND T1.unit NOT IN ('biomass', 'terpene', 'sift', 'cannabinoid')) AS unpackaged_extracts_other_shipped_exported,
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
	        SET enable_nestloop = off;
	       
            UPDATE health_canada_report
            SET 		
                unpackaged_seeds_shipped_exported_value = COALESCE(T2.unpackaged_seeds_shipped_exported_value,0),
                unpackaged_vegetative_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_vegetative_cannabis_plants_shipped_exported_value,0),
                unpackaged_whole_cannabis_plants_shipped_exported_value = COALESCE(T2.unpackaged_whole_cannabis_plants_shipped_exported_value,0),
                unpackaged_fresh_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_fresh_cannabis_shipped_exported_value,0)/1000,
                unpackaged_purchased_hemp_shipped_exported_value = COALESCE(T2.unpackaged_purchased_hemp_shipped_exported_value,0)/1000,
                unpackaged_dried_cannabis_shipped_exported_value = COALESCE(T2.unpackaged_dried_cannabis_shipped_exported_value,0)/1000,
                unpackaged_extracts_shipped_exported_value = COALESCE(T2.unpackaged_extracts_shipped_exported_value,0)/1000,
                
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
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE T1.unit = 'purchasedHemp') AS unpackaged_purchased_hemp_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_cannabis_shipped_exported_value,
                    SUM(COALESCE(T1.price,0)) FILTER (WHERE (T1.unit IN ('distilled', 'crude', 'biomass', 'terpene', 'sift', 'cannabinoid'))) AS unpackaged_extracts_shipped_exported_value,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_exported_value,
	                SUM(COALESCE(T1.price,0)) FILTER(WHERE T1.subtype = 'other' AND T1.unit NOT IN ('biomass', 'terpene', 'sift', 'cannabinoid')) AS unpackaged_extracts_other_shipped_exported_value,
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










CREATE OR REPLACE FUNCTION public.f_hc_report_inventory_produced_processed(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
    DECLARE package_oil DECIMAL;
   	DECLARE v_taxonomy_id bigint;
	
        BEGIN
        -- unpackaged seed processed and unpacked vegetative plants produced
	    SET enable_nestloop = off;
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
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                UNION ALL
                SELECT 0, COALESCE((data->>'to_qty')::numeric, 0) as clones
                FROM activities
                WHERE name = 'propagate_cuttings' AND
                    organization_id = org_id AND
                    timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged vegetative plants processed and  whole plant produced
        UPDATE health_canada_report
        SET 
            unpackaged_vegetative_plants_processed = COALESCE(T2.plants_processed,0),
            unpackaged_whole_cannabis_plants_produced = COALESCE(T2.plants_processed,0)	
        FROM (
            SELECT 
                SUM(COALESCE(T1.plants_processed,0)) AS plants_processed			
            FROM (
                SELECT
                    GREATEST(0,COALESCE(CAST(act.data->>'qty' AS DECIMAL),0)) AS plants_processed
                FROM activities act 
                WHERE act.name = 'update_stage' 
                    AND act.data->>'to_stage' = 'flowering' 
                    AND act.organization_id = org_id 
                    AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged fresh cannabis produced and whole plants processed
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
                WHERE name IN ('batch_record_bud_harvest_weight', 'batch_record_harvest_weight', 'batch_record_harvest_weight_partially')
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged dried cannabis produced, unpackaged pure intermediate produced
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
                    FROM inventories AS inv
                    INNER JOIN (
                        SELECT
                            CAST(act_adj.data->>'from_inventory_id' AS bigint) AS inventory_id,
                            act_adj.id AS id,
                            max(act_adj.timestamp)
                        FROM activities AS act_adj
                        WHERE act_adj.name IN ('batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight')
                            AND act_adj.timestamp <= CAST(final_date AS "timestamp")
                        GROUP BY act_adj.data->>'from_inventory_id', act_adj.id
                    ) AS T0 ON T0.inventory_id = inv.id
                    INNER JOIN activities AS act ON act.id = t0.id
                    WHERE act.organization_id = org_id 
                        AND act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
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
                AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as dried_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('cured', 'dry') 
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                ) as t1
        ) AS T2
        WHERE id = report_id;
       
       
        -- purchased hemp
        UPDATE health_canada_report
        SET
            unpackaged_purchased_hemp_processed = COALESCE(T2.purchased_hemp_processed,0)/1000
        FROM (
            SELECT SUM(t1.purchased_hemp_used) AS purchased_hemp_processed from (
            SELECT CAST (data->>'to_qty' AS numeric) as purchased_hemp_used 
                FROM activities 
                WHERE name IN ('batch_record_crude_oil_weight')
                AND data->>'from_qty_unit' in ('purchasedHemp') 
                --AND organization_id = 1 
                --AND TO_CHAR(timestamp,'YYYY-MM-DD') BETWEEN '2020-12-01'  AND '2020-12-30'
                AND organization_id = org_id 
                AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as purchased_hemp_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' in ('purchasedHemp') 
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                
                ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged new extractions processed and produced
       
        package_oil := (COALESCE((SELECT SUM(CAST(actTransf.data->>'to_qty' AS DECIMAL))
				FROM activities AS act
				INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
				INNER JOIN stats_taxonomies AS st ON st.name = actTransf.data->>'to_qty_unit' AND st.organization_id = act.organization_id
				LEFT JOIN skus AS s ON CAST(act.data->>'sku_id' AS INTEGER) = s.id
				WHERE act.name ='create_lot_item' AND s.package_type = 'packaged' AND 
				actTransf.data->>'to_qty_unit' IN ('crude', 'distilled') AND
				-- act.organization_id = 1 and
				-- TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
				    act.organization_id = org_id AND
				    act.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")),0));
       	

		
		v_taxonomy_id := (SELECT id FROM taxonomies t WHERE name = 'stats' AND organization_id = org_id);
				   		
				   
        UPDATE health_canada_report
        set
            -- extracts produced + oil produced
            unpackaged_extracts_produced = (COALESCE(unpackaged_extracts_produced, 0)) + (COALESCE(extracts_processed, 0)/1000)
            + (COALESCE(edibles_solid, 0)/1000)
            + (COALESCE(edibles_nonsolid, 0)/1000)
            + (COALESCE(extracts_ingested, 0)/1000)
            + (COALESCE(extracts_inhaled, 0)/1000)
            + (COALESCE(extracts_other, 0)/1000)
            - (COALESCE(extracts_pure_intermediate_reductions, 0)/1000),
            
            unpackaged_edibles_solid_produced = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_produced = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_produced = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) - (COALESCE(extracts_ingested_reductions, 0)/1000) + (COALESCE(extracts_ingested_additions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_produced = COALESCE(extracts_inhaled, 0)/1000 - (COALESCE(extracts_inhaled_reductions, 0)/1000) + (COALESCE(extracts_inhaled_additions, 0)/1000),
            unpackaged_extracts_other_produced = COALESCE(extracts_other, 0)/1000 - (COALESCE(extracts_other_reductions, 0)/1000) + (COALESCE(extracts_other_additions, 0)/1000),
            unpackaged_topicals_produced = COALESCE(topicals, 0)/1000 - (COALESCE(extracts_topicals_reductions, 0)/1000) + (COALESCE(extracts_topicals_additions, 0)/1000),
            
            unpackaged_edibles_solid_processed = COALESCE(edibles_solid, 0)/1000,
            unpackaged_edibles_nonsolid_processed = COALESCE(edibles_nonsolid, 0)/1000,
            unpackaged_extracts_ingested_processed = (COALESCE(extracts_ingested, 0)/1000) + (COALESCE(extracts_oil, 0)/1000) - (COALESCE(extracts_oil_reductions, 0)/1000) - (COALESCE(extracts_ingested_reductions, 0)/1000) + (COALESCE(extracts_ingested_additions, 0)/1000) + package_oil/1000,
            unpackaged_extracts_inhaled_processed = COALESCE(extracts_inhaled, 0)/1000 - (COALESCE(extracts_inhaled_reductions, 0)/1000) + (COALESCE(extracts_inhaled_additions, 0)/1000),
            unpackaged_extracts_other_processed = COALESCE(extracts_other, 0)/1000 - (COALESCE(extracts_other_reductions, 0)/1000) + (COALESCE(extracts_other_additions, 0)/1000),
            unpackaged_topicals_processed = COALESCE(topicals, 0)/1000 - (COALESCE(extracts_topicals_reductions, 0)/1000) + (COALESCE(extracts_topicals_additions, 0)/1000),
            
            unpackaged_pure_intermediate_reductions_other = COALESCE(reductions_other, 0)/1000
        FROM (
            
				SELECT
		        SUM(COALESCE(CAST (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE (st."name" NOT IN ('crude', 'distilled') AND st."name" NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AND (act."data"->>'from_qty_unit' NOT IN ('crude', 'distilled') AND act."data"->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract' ))) as extracts_processed,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_solid') AS edibles_solid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='edibles_nonsolid') AS edibles_nonsolid,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_ingested,
		        
				SUM(COALESCE(cast (act.data->>'from_qty' as DECIMAL),0)) FILTER (WHERE act."data"->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND name NOT IN ('seeds', 'plants')) AND act."name" IN ('batch_record_final_extracted_weight', 'queue_for_destruction')) AS extracts_oil_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='ingested' AND st."name" NOT IN ('crude', 'distilled') AND act."name" IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')) AS extracts_oil,
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='inhaled' AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_inhaled,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='other' /*AND st."name" NOT IN ('sift', 'cannabinoid', 'terpene', 'biomass')*/ AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS extracts_other,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' ='topicals' AND act.data->>'from_qty_unit' NOT IN (SELECT name FROM taxonomy_options to2 WHERE taxonomy_id = v_taxonomy_id AND DATA->>'type' = 'extract')) AS topicals,
		        
		        
		        
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'inhaled' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_inhaled_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'ingested' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_ingested_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'other' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_other_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st.data->>'subtype' = 'topicals' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_topicals_reductions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE from_st."name" IN ('crude', 'distilled') AND st.DATA->>'type' = 'extract') AS extracts_pure_intermediate_reductions,
		        
		        
		        
		        
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'inhaled' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_inhaled_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'ingested' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_ingested_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'other' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_other_additions,
		        SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE st.data->>'subtype' = 'topicals' AND from_st.data->>'subtype' != st.data->>'subtype' AND from_st.DATA->>'type' = 'extract') AS extracts_topicals_additions,
		        
		        
		        
		        
		        -- Other reductions if extracted from oil we need to put it on other reductions to math works.
		        --SUM(COALESCE(cast (act.data->>'to_qty' as DECIMAL),0)) FILTER (WHERE act.data->>'from_qty_unit' IN ('crude', 'distilled')) AS reductions_other
		        SUM(COALESCE(0)) AS reductions_other

		        FROM activities act
			    INNER JOIN
				(
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_final_extracted_weight')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('queue_for_destruction')
					AND a1."data"->>'from_qty_unit' IN ('crude', 'distilled')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
					UNION ALL 
					
					SELECT a1."data"->>'from_inventory_id' AS id,
					max(a1."timestamp") AS "timestamp" 
					FROM activities a1
					WHERE 
					a1.name IN ('batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
					AND a1.organization_id = org_id
					AND a1.timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
					GROUP BY a1."data"->>'from_inventory_id'
					
				) AS act_oil ON 
				act."data"->>'from_inventory_id' = act_oil.id AND act."timestamp" = act_oil.timestamp AND act.name IN ('batch_record_final_extracted_weight', 'queue_for_destruction', 'batch_record_distilled_oil_weight', 'batch_record_crude_oil_weight')
				INNER JOIN stats_taxonomies st ON 
				(act.data->>'to_qty_unit' = st.name OR (act.data->>'from_qty_unit' = st.name AND act."name" IN ('sample_sent_to_lab') )) AND st.organization_id = act.organization_id
				INNER JOIN stats_taxonomies from_st ON 
				(act.data->>'from_qty_unit' = from_st.name OR (act.data->>'from_qty_unit' = from_st.name AND act."name" IN ('sample_sent_to_lab'))) AND from_st.organization_id = act.organization_id
				
					
        ) AS T2
        WHERE id = report_id;

            -- unpackaged fresh cannabis processed 
        UPDATE health_canada_report
        SET
            unpackaged_fresh_cannabis_processed = COALESCE(T2.fresh_cannabis_processed,0)/1000
        FROM (
            SELECT SUM(t1.fresh_cannabis_used) AS fresh_cannabis_processed 
            FROM  (
                SELECT CAST (data->>'to_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_dry_weight', 'batch_record_crude_oil_weight', 'batch_record_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
                    
                UNION ALL
                
                SELECT CAST (data->>'from_qty' AS numeric) as fresh_cannabis_used 
                FROM activities 
                WHERE name IN ('batch_record_final_extracted_weight')
                    AND data->>'from_qty_unit' = 'g-wet'
                    AND organization_id = org_id 
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) as t1
        ) AS T2
        WHERE id = report_id;

        -- unpackaged other produced
        UPDATE health_canada_report
        SET
            unpackaged_other_produced = COALESCE(T2.gwet_produced,0) / 1000
        FROM (
            SELECT
                SUM(COALESCE(T1.gwet_produced,0)) AS gwet_produced
            FROM (
                SELECT
                    COALESCE(CAST(data->>'to_qty' AS DECIMAL),0) AS gwet_produced
                FROM activities
                WHERE name = 'create_sample'
                    AND data->>'from_qty_unit' = 'plants'
                    AND organization_id = org_id
                    AND timestamp BETWEEN CAST(initial_date AS "timestamp") AND CAST(final_date AS "timestamp")
            ) AS T1
        ) AS T2
        WHERE id = report_id;
        END;
        $function$
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
                unpackaged_purchased_hemp_shipped_researchers = COALESCE(T2.unpackaged_purchased_hemp_shipped_researchers,0)/1000,
                unpackaged_dried_shipped_researchers = COALESCE(T2.unpackaged_dried_shipped_researchers,0)/1000,
                unpackaged_extracts_shipped_researchers = COALESCE(T2.unpackaged_extracts_shipped_researchers,0)/1000,
                
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
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE T1.unit = 'purchasedHemp') AS unpackaged_purchased_hemp_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'dry' OR T1.unit = 'cured')) AS unpackaged_dried_shipped_researchers,
                    SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit IN ('distilled', 'crude', 'biomass', 'terpene', 'sift', 'cannabinoid'))) AS unpackaged_extracts_shipped_researchers,
                  
                    -- new endtypes
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'solid') AS unpackaged_edibles_solids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'nonsolid') AS unpackaged_edibles_nonsolids_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'inhaled') AS unpackaged_extracts_inhaled_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'ingested') AS unpackaged_extracts_ingested_shipped_researchers,
	                SUM(COALESCE(T1.to_qty,0)) FILTER(WHERE T1.subtype = 'other' AND T1.unit NOT IN ('biomass', 'terpene', 'sift', 'cannabinoid')) AS unpackaged_extracts_other_shipped_researchers,
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
	    SET enable_nestloop = off;
        UPDATE health_canada_report
        SET

            unpackaged_seed_shipped_analytical_testers = COALESCE(T2.unpackaged_seed_shipped_analytical_testers,0)/1000,
            unpackaged_vegetative_plants_shipped_analytical_testers = 0, -- this goes to adjustment/loss section
            unpackaged_whole_cannabis_plants_shipped_analytical_testers = 0,-- this goes to adjustment/loss section
            unpackaged_fresh_shipped_analytical_testers = COALESCE(T2.unpackaged_fresh_shipped_analytical_testers,0)/1000,
            unpackaged_purchased_hemp_shipped_analytical_testers = COALESCE(T2.unpackaged_purchased_hemp_shipped_analytical_testers,0)/1000,
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
                SUM(T1.quantity) FILTER(WHERE T1.unit = 'purchasedHemp') AS unpackaged_purchased_hemp_shipped_analytical_testers,
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
                    INNER JOIN activities AS act_create_sample ON act.data->>'inventory_id' = act_create_sample.data->>'inventory_id' AND act_create_sample.name ='create_sample'
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
                    unpackaged_purchased_hemp_opening_inventory = COALESCE(T1.unpackaged_purchased_hemp_inventory,0)/1000,
                    unpackaged_dried_cannabis_opening_inventory = COALESCE(T1.unpackaged_dried_cannabis_inventory,0)/1000,
                    unpackaged_extracts_opening_inventory = COALESCE(T1.unpackaged_extracts_inventory,0)/1000,
                    
                    unpackaged_edibles_solid_opening_inventory = COALESCE(T1.unpackaged_edibles_solid_inventory,0)/1000,
                    unpackaged_edibles_nonsolid_opening_inventory = COALESCE(T1.unpackaged_edibles_nonsolid_inventory,0)/1000,
                    unpackaged_extracts_inhaled_opening_inventory = COALESCE(T1.unpackaged_extracts_inhaled_inventory,0)/1000,
                    unpackaged_extracts_ingested_opening_inventory = COALESCE(T1.unpackaged_extracts_ingested_inventory,0)/1000,
                    unpackaged_extracts_other_opening_inventory = COALESCE(T1.unpackaged_extracts_other_inventory,0)/1000,
                    unpackaged_topicals_opening_inventory = COALESCE(T1.unpackaged_topicals_inventory,0)/1000,
                    unpackaged_other_opening_inventory = COALESCE(T1.unpackaged_other_inventory,0)/1000,
                    
                    
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

























CREATE OR REPLACE FUNCTION public.f_hc_report_received_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
            BEGIN		
                --received inventories
                UPDATE health_canada_report
                SET	
                    --unpackaged domestic
                    unpackaged_seed_received_domestic = COALESCE(T3.unpackaged_seed_received_domestic ,0)/1000,
                    unpackaged_vegetative_plants_received_domestic = COALESCE(T3.unpackaged_vegetative_plants_received_domestic,0),
                    unpackaged_fresh_cannabis_received_domestic = COALESCE(T3.unpackaged_fresh_cannabis_received_domestic ,0)/1000,
                    unpackaged_purchased_hemp_received_domestic = COALESCE(T3.unpackaged_purchased_hemp_received_domestic ,0)/1000,
                    unpackaged_dried_cannabis_received_domestic = COALESCE(T3.unpackaged_dried_cannabis_received_domestic ,0)/1000,
                    unpackaged_extracts_received_domestic = COALESCE(T3.unpackaged_extracts_received_domestic ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_domestic = COALESCE(T3.unpackaged_extracts_inhaled_received_domestic ,0)/1000,
                    unpackaged_extracts_ingested_received_domestic = COALESCE(T3.unpackaged_extracts_ingested_received_domestic,0)/1000,
                    unpackaged_extracts_other_received_domestic = COALESCE(T3.unpackaged_extracts_other_received_domestic ,0)/1000,
                    unpackaged_edibles_solid_received_domestic = COALESCE(T3.unpackaged_edibles_solid_received_domestic ,0)/1000,
                    unpackaged_edibles_nonsolid_received_domestic = COALESCE(T3.unpackaged_edibles_nonsolid_received_domestic ,0)/1000,
                    unpackaged_topicals_received_domestic = COALESCE(T3.unpackaged_topicals_received_domestic ,0)/1000,
                    
                    --unpackaged imported		
                    unpackaged_seed_received_imported = COALESCE(T3.unpackaged_seed_received_imported ,0)/1000,
                    unpackaged_vegetative_plants_received_imported = COALESCE(T3.unpackaged_vegetative_plants_received_imported,0),
                    unpackaged_fresh_cannabis_received_imported = COALESCE(T3.unpackaged_fresh_cannabis_received_imported ,0)/1000,
                    unpackaged_purchased_hemp_received_imported = COALESCE(T3.unpackaged_purchased_hemp_received_imported ,0)/1000,
                    unpackaged_dried_cannabis_received_imported = COALESCE(T3.unpackaged_dried_cannabis_received_imported ,0)/1000,
                    unpackaged_extracts_received_imported = COALESCE(T3.unpackaged_extracts_received_imported ,0)/1000,
                    
                    unpackaged_extracts_inhaled_received_imported = COALESCE(T3.unpackaged_extracts_inhaled_received_imported ,0)/1000,
                    unpackaged_extracts_ingested_received_imported = COALESCE(T3.unpackaged_extracts_ingested_received_imported,0)/1000,
                    unpackaged_extracts_other_received_imported = COALESCE(T3.unpackaged_extracts_other_received_imported ,0)/1000,
                    unpackaged_edibles_solid_received_imported = COALESCE(T3.unpackaged_edibles_solid_received_imported ,0)/1000,
                    unpackaged_edibles_nonsolid_received_imported = COALESCE(T3.unpackaged_edibles_nonsolid_received_imported ,0)/1000,
                    unpackaged_topicals_received_imported = COALESCE(T3.unpackaged_topicals_received_imported ,0)/1000,

                    
                    --packaged domestic
                    packaged_seed_received_domestic = COALESCE(T3.packaged_seed_received_domestic ,0),
                    packaged_vegetative_plants_received_domestic = COALESCE(T3.packaged_vegetative_plants_received_domestic,0),
                    packaged_fresh_cannabis_received_domestic = COALESCE(T3.packaged_fresh_cannabis_received_domestic ,0),
                    packaged_dried_cannabis_received_domestic = COALESCE(T3.packaged_dried_cannabis_received_domestic ,0),
                    packaged_extracts_received_domestic = COALESCE(T3.packaged_extracts_received_domestic ,0),	
                    
                    packaged_extracts_inhaled_received_domestic = COALESCE(T3.packaged_extracts_inhaled_received_domestic ,0),
                    packaged_extracts_ingested_received_domestic = COALESCE(T3.packaged_extracts_ingested_received_domestic,0),
                    packaged_extracts_other_received_domestic = COALESCE(T3.packaged_extracts_other_received_domestic ,0),
                    packaged_edibles_solid_received_domestic = COALESCE(T3.packaged_edibles_solid_received_domestic ,0),
                    packaged_edibles_nonsolid_received_domestic = COALESCE(T3.packaged_edibles_nonsolid_received_domestic ,0),
                    packaged_topicals_received_domestic = COALESCE(T3.packaged_topicals_received_domestic ,0)
                    
                FROM (
                    -- here i do the pivot (rows to column and columns to rows)
                    SELECT 
                        -- unpackage domestic(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_seed_received_domestic,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_vegetative_plants_received_domestic,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.purchased_hemp_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_purchased_hemp_received_domestic,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_dried_cannabis_received_domestic,
            
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'domestic') AS unpackaged_topicals_received_domestic,
                        
                        -- unpackage imported(kg)
                        SUM(COALESCE(T2.seeds_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_seed_received_imported,
                        SUM(COALESCE(T2.vegetative_plants,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_vegetative_plants_received_imported,
                        SUM(COALESCE(T2.fresh_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_fresh_cannabis_received_imported,
                        SUM(COALESCE(T2.purchased_hemp_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_purchased_hemp_received_imported,
                        SUM(COALESCE(T2.extracts_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_received_imported,
                        SUM(COALESCE(T2.dried_cannabis_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_dried_cannabis_received_imported,
                        
                        SUM(COALESCE(T2.extracts_inhaled_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_inhaled_received_imported,
                        SUM(COALESCE(T2.extracts_ingested_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_ingested_received_imported,
                        SUM(COALESCE(T2.extracts_other_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_extracts_other_received_imported,
                        SUM(COALESCE(T2.edibles_solid_weight,0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_solid_received_imported,
                        SUM(COALESCE(T2.edibles_non_solid_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_edibles_nonsolid_received_imported,
                        SUM(COALESCE(T2.topicals_weight, 0)) FILTER (WHERE T2.package_type ='unpackage' AND T2.type_shipping = 'imported') AS unpackaged_topicals_received_imported,
                        
                        
                        -- packaged domestic(#)
                        SUM(COALESCE(T2.packaged_seeds_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_seed_received_domestic,
                        SUM(COALESCE(T2.packaged_vegetative_plants_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_vegetative_plants_received_domestic,				
                        SUM(COALESCE(T2.fresh_cannabis_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_fresh_cannabis_received_domestic,
                        SUM(COALESCE(T2.dried_cannabis_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_dried_cannabis_received_domestic,
                        SUM(COALESCE(T2.extracts_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_received_domestic,
                        
                        SUM(COALESCE(T2.extracts_inhaled_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_inhaled_received_domestic,
                        SUM(COALESCE(T2.extracts_ingested_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_ingested_received_domestic,
                        SUM(COALESCE(T2.extracts_other_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_extracts_other_received_domestic,
                        SUM(COALESCE(T2.edibles_solid_qty,0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_solid_received_domestic,
                        SUM(COALESCE(T2.edibles_non_solid_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_edibles_nonsolid_received_domestic,
                        SUM(COALESCE(T2.topicals_qty, 0)) FILTER (WHERE T2.package_type ='package' AND T2.type_shipping = 'domestic') AS packaged_topicals_received_domestic
                        
                        FROM (
                        SELECT SUM(COALESCE((f).seeds_weight,0)) AS seeds_weight,
                            SUM(COALESCE((f).packaged_seeds_qty,0)) AS packaged_seeds_qty,
                            SUM(COALESCE((f).vegetative_plants,0)) AS vegetative_plants,
                            SUM(COALESCE((f).packaged_vegetative_plants_qty,0)) AS packaged_vegetative_plants_qty,
                            SUM(COALESCE((f).fresh_cannabis_weight, 0)) AS fresh_cannabis_weight,
                            SUM(COALESCE((f).purchased_hemp_weight, 0)) AS purchased_hemp_weight,
                            SUM(COALESCE((f).extracts_weight,0)) AS extracts_weight,
                            SUM(COALESCE((f).dried_cannabis_weight, 0)) AS dried_cannabis_weight,				
                            SUM(COALESCE((f).fresh_cannabis_qty, 0)) AS fresh_cannabis_qty,
                            SUM(COALESCE((f).extracts_qty,0)) AS extracts_qty,
                            SUM(COALESCE((f).dried_cannabis_qty, 0)) AS dried_cannabis_qty,		
                            
                            SUM(COALESCE((f).extracts_inhaled_weight,0)) AS extracts_inhaled_weight,
                            SUM(COALESCE((f).extracts_inhaled_qty, 0)) AS extracts_inhaled_qty,	
                            SUM(COALESCE((f).extracts_ingested_weight,0)) AS extracts_ingested_weight,
                            SUM(COALESCE((f).extracts_ingested_qty, 0)) AS extracts_ingested_qty,	
                            SUM(COALESCE((f).extracts_other_weight,0)) AS extracts_other_weight,
                            SUM(COALESCE((f).extracts_other_qty, 0)) AS extracts_other_qty,	
                            SUM(COALESCE((f).edibles_solid_weight,0)) AS edibles_solid_weight,
                            SUM(COALESCE((f).edibles_solid_qty, 0)) AS edibles_solid_qty,	
                            SUM(COALESCE((f).edibles_non_solid_weight,0)) AS edibles_non_solid_weight,
                            SUM(COALESCE((f).edibles_non_solid_qty, 0)) AS edibles_non_solid_qty,
                            SUM(COALESCE((f).topicals_weight,0)) AS topicals_weight,
                            SUM(COALESCE((f).topicals_qty, 0)) AS topicals_qty,
                            T1.type_shipping,
                            (f).package_type as package_type
                        FROM (
                            SELECT f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype') AS f,
                            (f_serialize_stats_fields(CAST(act.data->>'to_qty' as numeric), inv.latest_unit, NULL, NULL, inv.type, inv.package_type, inv.shipping_status, inv.data, inv.attributes, st.data->>'subtype')).fresh_cannabis_weight,
                                    CASE
                                        WHEN crm.data->'residing_address'->>'country' NOT IN ('Canada', 'ca', 'canada') THEN 'imported' 
                                        ELSE 'domestic'
                                    END AS type_shipping
                                    
                            --FROM f_inventories_latest_stats_stage('2021-06-30', 1) as inv
                            FROM f_inventories_latest_stats_stage(final_date, org_id)  as inv
                                INNER JOIN activities AS act ON (act.name = 'receive_inventory' and act.data->>'inventory_id' = CAST(inv.id AS VARCHAR)) 
                                OR (act.name = 'receive_processor' and act.data->>'to_inventory_id' = CAST(inv.id AS VARCHAR))
                                LEFT JOIN crm_accounts AS crm ON CAST(crm.id AS VARCHAR) = act.data->>'vendor_id'
                                INNER JOIN organizations as org on inv.organization_id = org.id
                                inner join stats_taxonomies as st on st.name = inv.latest_unit AND st.organization_id = org.id
                            WHERE type IN ('received inventory', 'batch') AND 
                                --inv.organization_id = 1 AND
						                            --inv.timestamp >= cast('2021-11-01' as date)
	                            inv.organization_id = org_id AND
	                            inv.timestamp >= cast(initial_date as date)
                        ) AS T1
                        GROUP BY T1.type_shipping, (f).package_type
                    ) AS T2
                ) AS T3
                WHERE id = report_id;	
                            
            END;$function$
;






















CREATE OR REPLACE FUNCTION public.f_test_report_result(report_id integer)
 RETURNS text[]
 LANGUAGE plpgsql
AS $function$
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
                    unpackaged_seed_reductions_shipped_returned+
                    unpackaged_seeds_shipped_exported+
                    unpackaged_seed_processed),
                    --closing
                    unpackaged_seed_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
    
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Seeds calculation is incorrect.';
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
                    unpackaged_vegetative_plants_shipped_cultivators_processors+
                    unpackaged_vegetative_plants_shipped_researchers+
                    unpackaged_vegetative_cannabis_plants_shipped_exported+
                    unpackaged_vegetative_plants_destroyed+
                    unpackaged_vegetative_plants_reductions_shipped_returned+
                    unpackaged_vegetative_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_vegetative_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Vegetative Cannabis Plants calculation is incorrect.';
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
                    unpackaged_whole_cannabis_plants_shipped_exported+
                    unpackaged_whole_cannabis_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_whole_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Whole Cannabis Plants calculation is incorrect.';
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
                    unpackaged_fresh_cannabis_reductions_shipped_returned+
                    unpackaged_fresh_shipped_cultivators_processors+
                    unpackaged_fresh_cannabis_shipped_exported+
                    unpackaged_fresh_shipped_researchers+
                    unpackaged_fresh_cannabis_destroyed+
                    unpackaged_fresh_shipped_analytical_testers),
                    --closing
                    unpackaged_fresh_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Fresh Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
               
               
               
               
               -- unpackaged purchased hemp
                SELECT
                    --opening
                    unpackaged_purchased_hemp_opening_inventory,
                    --adition
                    (
                    unpackaged_purchased_hemp_received_domestic+
                    unpackaged_purchased_hemp_received_imported),
                    --reduction
                    (unpackaged_purchased_hemp_processed+
                    unpackaged_purchased_hemp_adjustment_loss+
                    unpackaged_purchased_hemp_reductions_shipped_returned+
                    unpackaged_purchased_hemp_shipped_cultivators_processors+
                    unpackaged_purchased_hemp_shipped_exported+
                    unpackaged_purchased_hemp_shipped_researchers+
                    unpackaged_purchased_hemp_destroyed+
                    unpackaged_purchased_hemp_shipped_analytical_testers),
                    --closing
                    unpackaged_purchased_hemp_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Fresh Cannabis calculation is incorrect.';
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
                    unpackaged_dried_shipped_cultivators_processors+
                    unpackaged_dried_cannabis_shipped_exported+
                    unpackaged_dried_shipped_researchers+
                    unpackaged_dried_cannabis_reductions_shipped_returned+
                    unpackaged_dried_shipped_analytical_testers),
                    --closing
                    unpackaged_dried_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Dried Cannabis calculation is incorrect.';
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
                    (
                    unpackaged_edibles_solid_processed+
                    unpackaged_edibles_nonsolid_processed+
                    unpackaged_extracts_ingested_processed+
                    unpackaged_extracts_inhaled_processed+
                    unpackaged_extracts_other_processed+
                    unpackaged_extracts_shipped_cultivators_processors+
                    unpackaged_extracts_shipped_researchers+
                    unpackaged_topicals_processed+
                    unpackaged_extracts_packaged_label+
                    unpackaged_pure_intermediate_reductions_other+
                    unpackaged_extracts_adjustment_loss+
                    unpackaged_extracts_reductions_shipped_returned+
                    unpackaged_extracts_destroyed+
                    unpackaged_extracts_shipped_analytical_testers),
                    --closing
                    unpackaged_extracts_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Pure Intermediate calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- unpackaged extracts inhaled
                SELECT
                    --opening
                    unpackaged_extracts_inhaled_opening_inventory,
                    --adition
                    (unpackaged_extracts_inhaled_produced+
                    unpackaged_extracts_inhaled_received_domestic+
                    unpackaged_extracts_inhaled_received_imported),
                    --reduction
                    (unpackaged_extracts_inhaled_packaged_label+
                    unpackaged_extracts_inhaled_adjustment_loss+
                    unpackaged_extracts_inhaled_shipped_researchers+
                    unpackaged_extracts_inhaled_shipped_cultivators_processors+
                    unpackaged_extracts_inhaled_shipped_exported+
                    unpackaged_extracts_inhaled_destroyed+
                    unpackaged_extracts_inhaled_reductions_shipped_returned+
                    unpackaged_extracts_inhaled_analytical_testers),
                    --closing
                    unpackaged_extracts_inhaled_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Extracts Inhaled calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                -- unpackaged extracts other
                SELECT
                    --opening
                    unpackaged_extracts_other_opening_inventory,
                    --adition
                    (unpackaged_extracts_other_produced+
                    unpackaged_extracts_other_received_domestic+
                    unpackaged_extracts_other_received_imported),
                    --reduction
                    (unpackaged_extracts_other_packaged_label+
                    unpackaged_extracts_other_adjustment_loss+
                    unpackaged_extracts_other_destroyed+
                    unpackaged_extracts_other_reductions_shipped_returned+
                    unpackaged_extracts_other_analytical_testers),
                    --closing
                    unpackaged_extracts_other_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Extracts Other calculation is incorrect.';
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Pacakged Seeds calculation is incorrect.';
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Vegetative Cannabis Plants calculation is incorrect.';
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Fresh Cannabis calculation is incorrect.';
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Dried Cannabis calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
                -- Packaged extracts cannabis
                SELECT
                    --opening
                    packaged_extracts_ingested_opening_inventory,
                    --adition
                    (packaged_extracts_ingested_received_domestic +
                    packaged_extracts_ingested_quantity_packaged),
                    --reduction
                    (packaged_extracts_ingested_destroyed +
                    packaged_extracts_ingested_shipped_domestic),
                    --closing
                    packaged_extracts_ingested_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Ingested (oil) calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
               -- Packaged extracts inhaled
                SELECT
                    --opening
                    packaged_extracts_inhaled_opening_inventory,
                    --adition
                    (packaged_extracts_inhaled_received_domestic+
                    packaged_extracts_inhaled_quantity_packaged),
                    --reduction
                    (packaged_extracts_inhaled_destroyed+
                    packaged_extracts_inhaled_shipped_domestic),
                    --closing
                    packaged_extracts_inhaled_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Inhaled calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
    
               -- Packaged extracts other
                SELECT
                    --opening
                    packaged_extracts_other_opening_inventory,
                    --adition
                    (packaged_extracts_other_received_domestic+
                    packaged_extracts_other_quantity_packaged),
                    --reduction
                    (packaged_extracts_other_destroyed+
                    packaged_extracts_other_shipped_domestic),
                    --closing
                    packaged_extracts_other_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Other calculation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                RETURN return_values;
            END ;
    
            $function$
;

        
        
        """)


def downgrade():
    pass
