"""new-end-types-hcr-return-received-inventory

Revision ID: 6257b2dbcb30
Revises: cc3ff5b23164
Create Date: 2021-06-15 09:26:17.907331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6257b2dbcb30'
down_revision = 'cc3ff5b23164'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
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
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
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

            END;$function$
            ;

        """
    )
