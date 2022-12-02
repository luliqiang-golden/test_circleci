"""
consumable_lot_return_items - return consumable items upon request
"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from db_functions import select_resource_from_db, update_into_db


class ConsumableLotReturnItems(ActivityHandler):
    """
    return consumable items upon request
    :param from_consumable_lot_id: consumable lot id
    :param from_qty: Used quantity
    :param from_qty_unit: The existing unit
    """

    required_args = {
        'from_consumable_lot_id',
        'from_qty',
        'from_qty_unit',
        'returned_by'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        consumable_lot_object = select_resource_from_db(
            'consumable_lots', args['from_consumable_lot_id'], args['organization_id'])

        current_qty = consumable_lot_object['current_qty']

        if args['from_qty'] > current_qty:

            raise ClientBadRequest({
                "code":
                "consumable_lot_use_items_out_of_bound",
                "description":
                "Current quantity({0}) is less than from_qty({1})".
                format(current_qty, args['from_qty'])
            }, 400)

        current_qty = current_qty - args['from_qty']

        update_db_result = update_into_db(
            'consumable_lots', args['from_consumable_lot_id'], {'current_qty': current_qty})
        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "consumable_lot_affected_rows": update_db_result['affected_rows'],
        }
