"""new-end-types-hcr-sales-data

Revision ID: fd3d376c9b7f
Revises: d6d2d9beea8b
Create Date: 2021-06-14 14:26:27.052584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd3d376c9b7f'
down_revision = 'd6d2d9beea8b'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
        CREATE OR REPLACE FUNCTION f_hcr_sales_data(org_id bigint, initial_date character varying, final_date character varying)
         RETURNS TABLE(province text, column_type text, column_section text, report_section text, packaged_qty bigint, unpackaged_qty numeric, price numeric)
         LANGUAGE plpgsql
        AS $function$
        BEGIN
          RETURN QUERY
            SELECT tax.province,
               ct.column_type,
               tp.column_section AS                                             column_section,
               s.report_section,
               COALESCE(SUM(quantity)
                        FILTER ( WHERE tp.column_section = o.type AND tax.province = o.province AND
                                       s.report_section = o.report_section), 0) packaged_qty,
               COALESCE(SUM(weight)
                        FILTER ( WHERE tp.column_section = o.type AND tax.province = o.province AND
                                       s.report_section = o.report_section), 0) unpackaged_qty,
               COALESCE(SUM(COALESCE(total, 0))
                        FILTER ( WHERE tp.column_section = o.type AND tax.province = o.province AND
                                       s.report_section = o.report_section), 0) price
            FROM --f_orders_between_date(1, '2021-06-01', '2021-06-30') o,
                 f_orders_between_date(org_id, initial_date, final_date) o,
                 (SELECT cj1.province FROM
                     (VALUES ('AB'), ('BC'), ('MB'), ('NB'), ('NL'), ('NT'),
                         ('NS'), ('NU'), ('QC'),  ('SK'),  ('YT'),  ('ON'),  ('PE')) cj1 (province))tax,
                 (SELECT cj2.column_section
                  FROM (VALUES ('medical_consumer'),
                               ('nonmedical_retailer'),
                               ('nonmedical_distributor'),
                               ('intra_industry_packaged'),
                               ('intra_industry_unpackaged'),
                               ('nonmedical_recreational')) cj2 (column_section)) tp,
                 (SELECT DISTINCT data ->> 'reportSection' AS report_section
                  FROM stats_taxonomies) s,
                 (SELECT cj4.column_type FROM (VALUES ('qty'), ('value')) cj4 (column_type)) ct
            GROUP BY tax.province, tp.column_section, s.report_section, ct.column_type;
        END;
        $function$
        ;
    """)

def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS f_hcr_sales_data(bigint,character varying,character varying)
        """
    )