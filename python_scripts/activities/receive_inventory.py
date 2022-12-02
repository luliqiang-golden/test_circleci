"""Class to handle requests to add an item to inventory from outside source"""

from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler
from activities.update_room import UpdateRoom


class ReceiveInventory(ActivityHandler):
    """Action to add item to inventory from outside source"""

    required_args = {
        'to_qty',
        'to_qty_unit',
        'variety',
        'variety_id',
        'name',
        'quarantined',
        'to_stage',
        'room',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):

        cls.check_required_args(args)

        name = "{0} {1}".format(args['variety'], args['to_qty_unit'])

        inventory_object = {
            "name": name,
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "received inventory",
            "variety": args["variety"],
            "variety_id": args["variety_id"],
            "package_type": args["package_type"],
            "timestamp": args["timestamp"],
        }

        if (args['package_type'] =='packaged'):
            inventory_object["qty_packages"] = args["qty_packages"]
            inventory_object["qty_per_package"] = args["qty_weight"]
        
        if (args['to_qty_unit'] == 'seeds'):
            inventory_object["seed_weight"] = args["seed_weight"]
            inventory_object["qty_seeds"] = args["qty_seeds"]
                

        inventory_result = insert_into_db('Inventories',
                                          inventory_object)

        args["to_inventory_id"] = inventory_result["id"]
        args["inventory_id"] = inventory_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        update_room_activity_data = {
                'name': 'update_room',
                'to_room': args['room'],
                'inventory_id': inventory_result["id"],
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'],
            }
        
        UpdateRoom.do_activity(update_room_activity_data, {})

        return {
            "activity_id": activity_result["id"],
            "inventory_id": inventory_result["id"]
        }
