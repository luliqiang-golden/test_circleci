"""new-end-types-hcr-orders-between-date

Revision ID: d6d2d9beea8b
Revises: 85bf8f5d2817
Create Date: 2021-06-14 14:23:23.540734

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6d2d9beea8b'
down_revision = '85bf8f5d2817'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
            CREATE OR REPLACE FUNCTION f_orders_between_date(org_id bigint, initial_date character varying, final_date character varying)
             RETURNS TABLE(province text, sku_type text, type text, report_section text, quantity integer, account_type text, total numeric, weight numeric)
             LANGUAGE plpgsql
            AS $function$
            BEGIN
              RETURN QUERY
                SELECT
                    orders.province,
                    orders.sku_type,
                    CASE
                        WHEN orders.account_type = 'patient' THEN 'medical_consumer'
                        WHEN orders.account_type = 'retailer' THEN 'nonmedical_retailer'
                        WHEN orders.account_type = 'distributor' THEN 'nonmedical_distributor'
                        WHEN orders.account_type in ('licence holder', 'researcher') THEN 'intra_industry'
                        WHEN orders.account_type = 'recreational consumer' THEN 'nonmedical_recreational'
                    END AS type,
            
                    st.data->>'reportSection' report_section,
                    orders.quantity,
                    orders.account_type,
                    orders.total,
                    (orders.f).qty as weight
                FROM
                (SELECT
                    oi.quantity,
                    o.shipping_address->>'province' AS province,
                    TRIM(REPLACE(CAST(crm.account_type AS VARCHAR), '"', '')) as account_type,
                    oi.price + oi.provincial_tax + oi.shipping_value - oi.discount as total,
                    o.id,
                    COALESCE(oi.sku_type, 'unpackaged') as sku_type,
                    f_serialize_stats(oi.ordered_stats) as f
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
                            FROM orders WHERE status='approved' and
                                organization_id = org_id and
                                LEFT(data->>'payment_date',10) between initial_date and final_date
            --                     organization_id = 1 and
            --                     LEFT(data->>'payment_date',10) between '2021-06-01' and '2021-06-30'
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
                            FROM (
                                SELECT *
                                    FROM orders
                                    WHERE status='cancelled'
                                    AND LEFT(data->>'payment_date',10) between initial_date and final_date
            --                         AND LEFT(data->>'payment_date',10) between '2021-06-01' and '2021-06-30'
                                ) AS b
                            INNER JOIN (SELECT *
                                from activities
                                WHERE
                                    name = 'order_update_status' AND
                                    data->>'to_status' = 'cancelled' AND
                                    TO_CHAR(timestamp,'YYYY-MM-DD') > final_date
            --                         TO_CHAR(timestamp,'YYYY-MM-DD') > '2021-06-30'
                                    ) AS a ON b.id = CAST(a.data->>'order_id' AS INTEGER)
                    ) AS order_status ON order_status.id = o.id
                ) as orders
                inner join stats_taxonomies st on st.name = (orders.f).unit;
            
            END;
            $function$
            ;
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """
            DROP FUNCTION IF EXISTS f_orders_between_date(bigint, varchar, varchar);
        """
    )
