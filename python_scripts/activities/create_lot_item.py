"""Class to handle requests to create a lot item that will receive inventory from a lot"""
import datetime

from db_functions import (insert_into_db, select_resource_from_db,
                          execute_query_into_db, select_from_db, get_sku_detail)
from class_external_webhooks import firing_webhooks
from activities.activity_handler_class import ActivityHandler


class CreateLotItem(ActivityHandler):
    """Action to create a lot item"""

    required_args = {
        'variety',
        'name',
        'organization_id',
        'created_by',
        'sku_id',
        'from_inventory_id',
        'sku_name',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new lot inventory item"""

        cls.check_required_args(args)

        inventory_name = "{0}-{1}-{2}".format(
            args["variety"],
            datetime.datetime.now().isocalendar()[1],
            datetime.datetime.now().year % 100,
        )

        inventory_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "lot item",
            "variety": args["variety"],
            "name": inventory_name,
            "sku_id": args["sku_id"],
            "from_inventory_id": args["from_inventory_id"],
            "sku_name": args["sku_name"],
        }

        if 'external_product_id' in args:
            inventory_object['external_product_id'] = args['external_product_id']

        inventory_result = insert_into_db('Inventories', inventory_object)

        args["inventory_id"] = inventory_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        cls.increase_skus_current_inventory(args["organization_id"], args["sku_id"])
        sku_detail = get_sku_detail(args["organization_id"], args["sku_id"])
        firing_webhooks(organization_id=args.get("organization_id"), event='skus.updated', event_data=sku_detail)
        return {
            "activity_id": activity_result["id"],
            "inventory_id": inventory_result["id"]
        }

    
    def increase_skus_current_inventory(organization_id, sku_id):
        '''Increases current_inventory value in skus table when lot_item is created'''

        params = {'organization_id': organization_id, 'sku_id': sku_id}
        query = '''
            UPDATE skus
            SET current_inventory = current_inventory + 1
            WHERE id = %(sku_id)s 
            AND organization_id = %(organization_id)s
        '''
        return execute_query_into_db(query, params)



        
