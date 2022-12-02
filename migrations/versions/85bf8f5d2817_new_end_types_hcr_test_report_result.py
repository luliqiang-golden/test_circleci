"""new-end-types-hcr-test-report-result

Revision ID: 85bf8f5d2817
Revises: b98aebdbe206
Create Date: 2021-06-14 10:32:00.153410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85bf8f5d2817'
down_revision = 'b98aebdbe206'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION f_test_report_result(report_id integer)
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
                    unpackaged_seed_processed),
                    --closing
                    unpackaged_seed_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
    
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Unpackaged Seeds calulation is incorrect.';
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
                    unpackaged_vegetative_plants_reductions_shipped_returned+
                    unpackaged_vegetative_plants_shipped_analytical_testers),
                    --closing
                    unpackaged_vegetative_cannabis_plants_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
                    unpackaged_fresh_cannabis_reductions_shipped_returned+
                    unpackaged_fresh_cannabis_destroyed+
                    unpackaged_fresh_shipped_analytical_testers),
                    --closing
                    unpackaged_fresh_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
                    unpackaged_dried_cannabis_reductions_shipped_returned+
                    unpackaged_dried_shipped_analytical_testers),
                    --closing
                    unpackaged_dried_cannabis_closing_inventory
                FROM
                    health_canada_report
                where id = report_id
                INTO opening_value, adition_value, reduction_value, closing_value;
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
                    (
                    unpackaged_edibles_solid_processed+
                    unpackaged_edibles_nonsolid_processed+
                    unpackaged_extracts_ingested_processed+
                    unpackaged_extracts_inhaled_processed+
                    unpackaged_extracts_other_processed+
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
                    text_value := 'Unpackaged Pure Intermediate calulation is incorrect.';
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
                    text_value := 'Unpackaged Extracts Inhaled calulation is incorrect.';
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
                    text_value := 'Unpackaged Extracts Other calulation is incorrect.';
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
                    text_value := 'Pacakged Seeds calulation is incorrect.';
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
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
    
                IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                    text_value := 'Packaged Extracts Injested (oil) calulation is incorrect.';
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
                    text_value := 'Packaged Extracts Inhaled calulation is incorrect.';
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
                    text_value := 'Packaged Extracts Other calulation is incorrect.';
                    return_values = array_append(return_values,text_value::TEXT);
                END IF;
    
                RETURN return_values;
            END ;
    
            $function$
        ;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION f_test_report_result(report_id integer)
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
                        unpackaged_seed_processed),
                        --closing
                        unpackaged_seed_closing_inventory
                    FROM
                        health_canada_report
                    where id = report_id
                    INTO opening_value, adition_value, reduction_value, closing_value;
    
    
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Seeds calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Vegetative Cannabis Plants calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Whole Cannabis Plants calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
                        unpackaged_fresh_shipped_analytical_testers),
                        --closing
                        unpackaged_fresh_cannabis_closing_inventory
                    FROM
                        health_canada_report
                    where id = report_id
                    INTO opening_value, adition_value, reduction_value, closing_value;
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Fresh Cannabis calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
                        unpackaged_dried_shipped_analytical_testers),
                        --closing
                        unpackaged_dried_cannabis_closing_inventory
                    FROM
                        health_canada_report
                    where id = report_id
                    INTO opening_value, adition_value, reduction_value, closing_value;
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Dried Cannabis calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
                        unpackaged_extracts_shipped_analytical_testers),
                        --closing
                        unpackaged_extracts_closing_inventory
                    FROM
                        health_canada_report
                    where id = report_id
                    INTO opening_value, adition_value, reduction_value, closing_value;
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Unpackaged Extracts Injested (oil) calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Packaged Vegetative Canabbis Plants calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
                        text_value := 'Packaged Fresh Cannabis calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
                        text_value := 'Packaged Dried Cannabis calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
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
    
                    IF NOT ((opening_value +adition_value) - reduction_value = closing_value) THEN
                        text_value := 'Packaged Extracts Injested (oil) calulation is incorrect. Closing inventory should be '||cast(closing_value as varchar);
                        return_values = array_append(return_values,text_value::TEXT);
                    END IF;
    
                    RETURN return_values;
                END ;
    
                $function$
;
    """
    )
