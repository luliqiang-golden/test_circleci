"""Endpoints for Orders"""

from flask_restful import Resource
from resource_functions import get_collection, select_from_db
from auth0_authentication import requires_auth


class Orders(Resource):
    # Read all article records

    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='orders')


class Order(Resource):
    # Read single Order by id

    @requires_auth
    def get(self, current_user, order_id, organization_id=None):
        query = '''
            select o.*, i.id as invoice_id,
                o.data ->> 'crm_account_name' as crm_account_name,
                o.data ->> 'tax_name' as tax_name,
                o.data ->> 'payment_date' as payment_date,
                o.data ->> 'payment_status' as payment_status
            from orders o
            left join invoices i on i.order_id = o.id
            where o.id = {0}
        '''.format(order_id)

        return select_from_db(query=query, code="order_error")[0]
