"""
queue_for_destruction - Queue material for destruction
"""
import datetime
import psycopg2
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest
from db_functions import insert_into_db, get_avarage_seed_weight, update_batch_seed_weight, select_resource_from_db

ATTRIBUTE = psycopg2.extras.Json({"status": "undestroyed"})


class QueueForDestruction(ActivityHandler):
    """
    Create a destruction inventory with undestroyed status, moving (if needed) inventory quantity from the source inventory 
    and add, in grams, the total amount of the material to be detroyed in the new inventory item

    :param from_inventory_id: Inventory ID of the source inventory item
    :param from_qty: Quantity being removed from the source inventory item
    :type from_qty: number
    :param from_qty_unit: Unit of the quantity being removed from the source inventory item

    :param to_qty: Quantity being added to the target inventory item
    :type to_qty: number
    :param to_qty_unit: Unit of the quantity being added to the target inventory item

    :variety: variety of the source inventory
    :type_of_waste: type of what is gonna be destroyed. eg. stems, flowers, leaves, etc.
    :weighed_by: person who weighed
    :checked_by: person who checked
    :reason_for_destruction:  the reason why the material is going to be destroyed
    :collected_from: the room where it was collected from

    :returns: An object containing the activity_id and inventory_id

    :raises: 400 disallowed_args
    :raises: 400 missing_required_fields
    """

    required_args = {
        'from_inventory_id', 'to_qty', 'to_qty_unit'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :param current_user: current user object
        """
        required_args = cls.required_args

        args_set = set(args)

        if 'from_qty' in args:
            required_args.update(['from_qty', 'from_qty_unit'])
        else:
            required_args.difference_update(['from_qty', 'from_qty_unit'])

        disallowed_args = cls.global_disallowed_args - required_args

        # if there is an intersection
        if args_set & disallowed_args:
            raise ClientBadRequest(
                {
                    "code": "sent_disallowed_fields",
                    "description": "Client sent activity with disallowed fields"
                }, 400)

        # if args doesn't have all of required args
        if required_args - args_set:
            raise ClientBadRequest(
                {
                    "code": "missing_required_fields",
                    "description": "Missing one of {}".format(
                        ', '.join(cls.required_args))
                }, 400)

        inventory_name = "{0}-{1}-{2}".format(
            args["variety"],
            datetime.datetime.now().isocalendar()[1],
            datetime.datetime.now().year % 100,
        )

        inventory_object = {
            "type": "destruction inventory",
            "variety": args["variety"],
            "from_inventory_id": args["from_inventory_id"],
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "name": inventory_name,
            "attributes": ATTRIBUTE,
            "reason_for_destruction": args['reason_for_destruction'],
            "collected_from": args['collected_from'],
            "timestamp": args['timestamp'] or datetime.datetime.now(),
        }

        return_obj = {}

        if 'from_qty' in args and args['from_qty_unit'] == 'seeds':
            inventory = select_resource_from_db(resource='inventories', resource_id=args["from_inventory_id"],organization_id=args["organization_id"])
            if inventory and inventory['type'] == 'batch':
                seeds_weight = round(get_avarage_seed_weight(args['organization_id'], args['from_inventory_id']) * float(args['from_qty']), 2)

                # update batch's seed weight 
                current_seeds_weight = float(inventory['attributes']['seeds_weight']) - seeds_weight

                result = update_batch_seed_weight(args['from_inventory_id'], current_seeds_weight)
                return_obj["batch_affected_rows"] = result['affected_rows']

        inventory_result = insert_into_db('Inventories', inventory_object)

        args["to_inventory_id"] = inventory_result["id"]

        return_obj["inventory_id"] = inventory_result["id"]

        if (args["reason_for_destruction"] == "Ungerminated seeds"):
            args['to_qty'] = round(get_avarage_seed_weight(args['organization_id'], args['from_inventory_id'])* float(args['from_qty']),3)
            args['to_qty_unit'] = 'g-wet'

        activity_result = cls.insert_activity_into_db(args)

        return_obj["activity_id"] = activity_result["id"]

        return return_obj
