"""Receive Consumable Lot"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class ReceiveConsumableLot(ActivityHandler):
    """
    Receive Consumable Lot

    :param consumable_class_id: source id of consumable_class
    :param initial_qty: Quantity of certain consumable_class being received
    :type initial_qty: number
    :param unit: Unit of the quantity being received
    :param expiration_date: date if the commodity expires

    :returns: An object containing the new activity's id and consumable_lot_id
    """

    required_args = {
        'consumable_class_id',
        'initial_qty',
        'unit',
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

        consumable_lot_object = {
            "class_id": args["consumable_class_id"],
            "initial_qty": args["initial_qty"],
            "current_qty": args["initial_qty"],
            "unit": args["unit"],
            "status": "awaiting_approval",
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
        }

        if (args["expiration_date"]):
            consumable_lot_object["expiration_date"] = args["expiration_date"]

        consumable_lots_result = insert_into_db(
            'consumable_lots', consumable_lot_object)

        args["consumable_lot_id"] = consumable_lots_result['id']

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "consumable_lot_id": args["consumable_lot_id"]
        }
