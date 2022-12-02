"""Endpoints for Invoices"""

from flask_restful import Resource
from db_functions import select_from_db
from resource_functions import get_collection, get_resource
from auth0_authentication import requires_auth


class Invoices(Resource):

    def _bind_invoices_with_orders(self):
        query = """
            select
                o.crm_account_id, o.created_by, o.organization_id, o.description, o.order_type, o.order_received_date,
                o.order_placed_by, o.timestamp, o.data, o.shipping_address, o.ordered_stats, o.shipped_stats, o.status,
                o.shipping_status, o.due_date, o.sub_total, o.provincial_tax, o.excise_tax, o.discount_percent,
                o.discount, o.shipping_value, o.total, o.include_tax,
                i.id,
                i.order_id,
                i.timestamp as invoice_date,
                case
                    when o.status = 'cancelled' then 'cancelled'
                    when o.status = 'approved' and o.data ->> 'payment_status' in ('received') then 'payment_received'
                    else 'awaiting_payment'
                end as invoice_status
            from invoices i
            inner join orders o on o.id = i.order_id
            order by i.id desc
        """

        return query

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        query = self._bind_invoices_with_orders()

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='invoices',
            query=query)


class Invoice(Resource):

    # Read single Invoice by id
    @requires_auth
    def get(self, current_user, invoice_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=invoice_id,
            organization_id=organization_id,
            resource='invoices')


class GenerateInvoice(Resource):

    @requires_auth
    def get(self, current_user, invoice_id, organization_id=None):
        query = """
            select i.*,
            (
                select row_to_json(ord)
                    from (
                        select o.shipping_address, o.provincial_tax, o.excise_tax,
                            o.discount_percent, o.discount, o.total, o.include_tax,
                            o.shipping_value, o.sub_total, data ->> 'tax_name' as tax
                        from orders o
                        where o.id = i.order_id
                    ) as ord
            ) as orders,
            (
                select coalesce(array_to_json(array_agg(row_to_json(act))), '[]')
                from (
                    select data ->> 'description' as description, data->> 'detail' as detail
                    from activities
                    where name = 'order_create_note'
                    and cast(data ->> 'order_id' as integer) = o.id
                ) as act
            ) as activities,
            (
                select
                    (org.data -> 'facility_details' -> 'facilityAddress') || (org.data -> 'theme') || jsonb_build_object('name', org.name)
                from organizations org
                where org.id = i.organization_id
            ) as organization,
            (
                select jsonb_build_object('email', ca.data ->> 'email',
                                        'telephone', ca.data ->> 'telephone',
                                        'name', ca.name)
                from crm_accounts ca
                where ca.id = o.crm_account_id
            ) as account,
            (
                select coalesce(array_to_json(array_agg(row_to_json(orderItem))), '[]')
                from (
                    select oi.sku_name, oi.quantity, oi.price
                    from order_items oi
                    where oi.order_id = o.id
                    and oi.status <> 'cancelled'
                ) as orderItem
            ) as order_item

            from invoices i
            inner join orders o on o.id = i.order_id
            where i.id = {0}
        """.format(invoice_id)

        return select_from_db(query=query, code="invoice_generating_error")[0]
