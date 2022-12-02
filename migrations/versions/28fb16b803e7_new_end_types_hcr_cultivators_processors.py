"""new-end-types-hcr-cultivators-processors

Revision ID: 28fb16b803e7
Revises: 30b0d81d7e13
Create Date: 2021-08-23 07:33:17.007275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28fb16b803e7'
down_revision = '30b0d81d7e13'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
"""

ALTER TABLE health_canada_report 
    ADD COLUMN IF NOT exists unpackaged_seed_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    ADD COLUMN IF NOT exists unpackaged_vegetative_plants_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    ADD COLUMN IF NOT exists unpackaged_whole_cannabis_plants_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    ADD COLUMN IF NOT exists unpackaged_fresh_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    ADD COLUMN IF NOT exists unpackaged_dried_shipped_cultivators_processors numeric(14,2) DEFAULT 0,
    ADD COLUMN IF NOT exists unpackaged_extracts_shipped_cultivators_processors numeric(14,2) DEFAULT 0;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS 
$$
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
    -- adjustment and loss
    PERFORM f_hc_report_inventory_adjustment_loss(report_id, initial_date, final_date, org_id);
    --destruction
    PERFORM f_hc_report_inventory_destroyed(report_id, initial_date, final_date, org_id);
    -- packaged shipped domestic
    PERFORM f_hc_report_inventory_shipped_domestic(report_id, initial_date, final_date, org_id);
    -- cultivator and processor
    PERFORM f_hc_report_inventory_cultivators_processors(report_id, initial_date, final_date, org_id);
    --closing inventory
    PERFORM f_hc_report_closing_inventory(report_id, final_date, org_id);
    --return items
    PERFORM f_hc_report_return_received_inventory(report_id, initial_date, final_date, org_id);    
END;
$$;
"""
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
"""
ALTER TABLE health_canada_report 
    DROP COLUMN IF EXISTS unpackaged_seed_shipped_cultivators_processors,
    DROP COLUMN IF EXISTS unpackaged_vegetative_plants_shipped_cultivators_processors,
    DROP COLUMN IF EXISTS unpackaged_whole_cannabis_plants_shipped_cultivators_processors,
    DROP COLUMN IF EXISTS unpackaged_fresh_shipped_cultivators_processors,
    DROP COLUMN IF EXISTS unpackaged_dried_shipped_cultivators_processors,
    DROP COLUMN IF EXISTS unpackaged_extracts_shipped_cultivators_processors;

CREATE OR REPLACE FUNCTION public.f_hc_report_inventory(report_id integer, initial_date character varying, final_date character varying, org_id integer)
 RETURNS void
 LANGUAGE plpgsql
AS 
$$
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
"""
    )
