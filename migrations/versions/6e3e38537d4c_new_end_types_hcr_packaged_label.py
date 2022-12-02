"""new-end-types-hcr-packaged-label

Revision ID: 6e3e38537d4c
Revises: 50161e97182c
Create Date: 2021-06-15 09:19:22.800769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e3e38537d4c'
down_revision = '50161e97182c'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
                    unpackaged_extracts_packaged_label = COALESCE(T2.unpackaged_extracts_packaged_label,0)/1000,
                    packaged_seed_quantity_packaged = COALESCE(T2.packaged_seed_quantity_packaged,0),
                    packaged_vegetative_plants_quantity_packaged = COALESCE(T2.packaged_vegetative_plants_quantity_packaged,0),
                    packaged_fresh_cannabis_quantity_packaged = COALESCE(T2.packaged_fresh_cannabis_quantity_packaged,0),
                    packaged_dried_cannabis_quantity_packaged = COALESCE(T2.packaged_dried_cannabis_quantity_packaged,0),
                    packaged_extracts_quantity_packaged = COALESCE(T2.packaged_extracts_quantity_packaged,0),
                    
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
                        SUM(COALESCE(T1.to_qty,0)) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS unpackaged_extracts_packaged_label,
                        
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
                        COUNT(*) FILTER (WHERE (T1.unit = 'distilled' OR T1.unit = 'crude')) AS packaged_extracts_quantity_packaged,
                        
                        COUNT(*) FILTER (WHERE (T1.subtype = 'solid')) AS packaged_edibles_solid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'nonsolid')) AS packaged_edibles_nonsolid_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'inhaled')) AS packaged_extracts_inhaled_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'ingested')) AS packaged_extracts_ingested_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'other')) AS packaged_extracts_other_quantity_packaged,
                        COUNT(*) FILTER (WHERE (T1.subtype = 'topicals')) AS packaged_topicals_quantity_packaged
                    
                    FROM (
                        SELECT CAST(actTransf.data->>'to_qty' AS DECIMAL) AS to_qty, actTransf.data->>'to_qty_unit' AS unit, st.data->>'subtype' as subtype
                        FROM activities AS act
                        INNER JOIN activities AS actTransf ON act.data->>'inventory_id' = actTransf.data->>'to_inventory_id' AND actTransf.name = 'transfer_inventory'
                        inner join stats_taxonomies st on st.name = actTransf.data->>'to_qty_unit'
                        WHERE act.name ='create_lot_item' AND
        --					act.organization_id = 1 and
        --					TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN '2021-06-01'  AND '2021-06-30'
                            act.organization_id = org_id AND
                            TO_CHAR(act.timestamp,'YYYY-MM-DD') BETWEEN initial_date AND final_date
                        ) AS T1
                    ) AS T2
                    WHERE id = report_id;
                    
            END;$function$
        ;

        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
                
                
            END;$function$
        ;

        """
    )
