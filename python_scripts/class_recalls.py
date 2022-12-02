"""Endpoints for Recalls"""
from flask import jsonify
from flask_restful import Resource
from numpy import array
from resource_functions import get_collection, get_resource
from auth0_authentication import requires_auth

import operator

from db_functions import select_resource_from_db, DATABASE


class Recalls(Resource):

    # Read all
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='recalls')


class Recall(Resource):

    # Read single Recall by id
    @requires_auth
    def get(self, current_user, recall_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=recall_id,
            organization_id=organization_id,
            resource='recalls')


class RecallDetails(Resource):

    # Read single Recall details
    @requires_auth
    def get(self, current_user, recall_id, organization_id=None):
        # If applicable, information on who produced, imported, packaged or labelled the affected cannabis or cannabis product
        # If the recall is related to a cannabis accessory that is a cannabis product, name and address of each person that produced or imported the cannabis accessory or any part of it

        # The number of each affected lot or batch
        # If known, the number of any lot or batch that was used to make the cannabis product
        # The reasons for initiating a recall
        # A description of the cannabis or cannabis product being recalled, including the brand name
        recall_info = get_recall(
            current_user=current_user,
            recall_id=recall_id,
            organization_id=organization_id,
        )

        temp = recall_info.json

        # The quantity that remains in possession of the license holder
        # The quantity that was produced or imported by the license holder
        lots = get_lots(
            current_user=current_user,
            organization_id=organization_id,
            lot_ids=temp["lot_ids"]
        )

        total_left = list(map(operator.itemgetter(
            "stats"), lots))

        # The quantity that was sold or distributed by the license holder
        # The quantity that remains in possession of the license holder
        # The quantity that was produced or imported by the license holder
        lot_items = get_lot_items(
            current_user=current_user,
            organization_id=organization_id,
            lot_ids=temp["lot_ids"]
        )

        batches = get_batches(
            current_user=current_user,
            organization_id=organization_id,
            lots=lots
        )

        order_items = get_order_items(
            current_user=current_user,
            organization_id=organization_id,
            lot_items=lot_items
        )

        # The name of license holder
        org = get_org(organization_id)
        if order_items:
            total_sold = list(map(operator.itemgetter(
                "shipped_stats"), order_items))

            skus = get_skus(
                current_user=current_user,
                organization_id=organization_id,
                order_items=order_items
            )

            # The period of time during which the product was sold or distributed
            orders = get_orders(
                current_user=current_user,
                organization_id=organization_id,
                order_items=order_items
            )

            # The number of supply chain customers to whom it was sold or distributed
            orders_count = len(orders)

            orders_end_date = max([item.get('order_received_date')
                                   for item in orders if item.get('order_received_date')])
            orders_start_date = min([item.get('order_received_date')
                                     for item in orders if item.get('order_received_date')])

            accounts = get_crm_accounts(
                current_user=current_user,
                organization_id=organization_id,
                orders=orders
            )

            return jsonify(
                recall_info=recall_info.json,
                lots=lots,
                total_left=total_left,
                lot_items=lot_items,
                batches=batches,
                order_items=order_items,
                total_sold=total_sold,
                skus=skus,
                orders=orders,
                orders_count=orders_count,
                orders_start_date=orders_start_date,
                orders_end_date=orders_end_date,
                accounts=accounts,
                org=org)
        else:
            return jsonify(
                recall_info=recall_info.json,
                lots=lots,
                total_left=total_left,
                lot_items=lot_items,
                total_sold=0,
                batches=batches,
                org=org)


def get_org(organization_id):
    org = select_resource_from_db(
        'organizations', organization_id, organization_id)

    del org['theme']
    del org['features']
    del org['security']

    return org


def get_recall(current_user, recall_id, organization_id):
    recall_info = get_resource(
        current_user=current_user,
        resource_id=recall_id,
        organization_id=organization_id,
        resource='recalls')

    return recall_info


def get_lots(current_user, organization_id, lot_ids):
    lot_filters = [('type', '=', 'lot'), ]
    lot_inv = "|".join(map(str, lot_ids))
    lot_filters.append(('id', '=', lot_inv))

    lots = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='inventories',
        filters=lot_filters,
        paginate=False)

    return lots


def get_lot_items(current_user, organization_id, lot_ids):
    lot_items_filters = [('type', '=', 'lot item'), ]
    lot_items_inv = "|".join(map(str, lot_ids))
    lot_items_filters.append(('from_inventory_id', '=', lot_items_inv))

    lot_items = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='inventories',
        filters=lot_items_filters,
        paginate=False)

    return lot_items


def get_batches(current_user, organization_id, lots):
    batch_ids = []
    for item in lots:
        if item.get('from_inventory_id'):
            from_ids_array = item.get('from_inventory_id')
            if(isinstance(from_ids_array, list)):
                for batch_id in from_ids_array: 
                    batch_ids.append(batch_id)
            else:
                batch_ids.append(from_ids_array)

    batch_filters = [('type', '=', 'batch'), ]
    batch_inv = "|".join(map(str, batch_ids))
    batch_filters.append(('id', '=', batch_inv))

    batches = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='inventories',
        filters=batch_filters,
        paginate=False)

    return batches


def get_order_items(current_user, organization_id, lot_items):
    order_item_ids = [item.get('order_item_id')
                      for item in lot_items if item.get('order_item_id')]
    order_item_inv = "|".join(map(str, order_item_ids))
    order_item_filters = [('id', '=', order_item_inv)]
    if order_item_ids:
        order_items = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='order_items',
            filters=order_item_filters,
            paginate=False)
        return order_items


def get_orders(current_user, organization_id, order_items):
    order_ids = map(operator.itemgetter(
        "order_id"), order_items)

    order_inv = "|".join(map(str, order_ids))
    order_filters = [('id', '=', order_inv)]

    orders = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='orders',
        filters=order_filters,
        paginate=False)

    return orders


def get_crm_accounts(current_user, organization_id, orders):
    account_ids = map(operator.itemgetter(
        "crm_account_id"), orders)

    account_inv = "|".join(map(str, account_ids))
    account_filters = [('id', '=', account_inv)]

    accounts = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='crm_accounts',
        filters=account_filters,
        paginate=False)

    return accounts


def get_skus(current_user, organization_id, order_items):
    sku_ids = map(operator.itemgetter(
        "sku_id"), order_items)

    sku_inv = "|".join(map(str, sku_ids))
    sku_filters = [('id', '=', sku_inv)]

    skus = get_collection(
        current_user=current_user,
        organization_id=organization_id,
        resource='skus',
        filters=sku_filters,
        paginate=False)

    return skus
