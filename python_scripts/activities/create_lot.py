"""Class to handle requests to create a lot that will receive inventory from a batch"""
import datetime

from activities.transfer_inventory import TransferInventory
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler
from activities.update_room import UpdateRoom


class CreateLot(ActivityHandler):
    """Action to create a lot"""

    required_args = {
        'name',
        'variety',
        'variety_id',
        'organization_id',
        'created_by',
        'from_inventory_id',
        'to_qty',
        'to_qty_unit',
        'from_qty',
        'from_qty_unit',
        'to_room',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new lot inventory item"""

        cls.check_required_args(args)

        if args.get('lot_name'):
            inventory_name = args.get('lot_name')
        else:
            inventory_name = "{0}-{1}-{2}".format(
                args["variety"],
                datetime.datetime.now().isocalendar()[1],
                datetime.datetime.now().year % 100,
            )

        inventory_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "lot",
            "variety": args["variety"],
            "variety_id": args["variety_id"],
            "from_inventory_id": args["from_inventory_id"],
            "name": inventory_name,
            "timestamp": args["timestamp"] or datetime.datetime.now(),
        }

        if 'external_product_id' in args:
            inventory_object['external_product_id'] = args['external_product_id']

        if "merged_inventories" in args:
            inventory_object["merged_inventories"] = args["merged_inventories"]

        inventory_result = insert_into_db('Inventories', inventory_object)

        create_lot_activity_payload = {
            "name": "create_lot",
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "variety": args["variety"],
            "variety_id": args["variety_id"],
            "from_inventory_id": args["from_inventory_id"],
            "inventory_id": inventory_result["id"],
            "timestamp": args["timestamp"] or datetime.datetime.now(),
        }

        activity_result = cls.insert_activity_into_db(
            create_lot_activity_payload)

        update_room_activity_data = {
            'name': 'update_room',
            'to_room': '' if not args.get('to_room') else args.get('to_room'),
            'inventory_id': inventory_result["id"],
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
            'timestamp': args['timestamp'] or datetime.datetime.now(),
        }
        UpdateRoom.do_activity(update_room_activity_data, {})

        if 'to_qty' in args and 'merged_inventories' not in args:
            transfer_inventory_payload = {
                'name': 'transfer_inventory',
                'to_inventory_id': inventory_result.get('id'),
                'from_inventory_id': args['from_inventory_id'],
                'to_qty_unit': args.get('to_qty_unit'),
                'from_qty_unit': args.get('from_qty_unit'),
                'to_qty': args.get('to_qty'),
                'from_qty': args.get('from_qty'),
                'organization_id': args.get('organization_id'),
                'created_by': args.get('created_by'),
                'timestamp': args.get('timestamp') or datetime.datetime.now(),
            }
            TransferInventory.do_activity(
                transfer_inventory_payload, current_user)

        return {
            "activity_id": activity_result["id"],
            "inventory_id": inventory_result["id"]
        }
