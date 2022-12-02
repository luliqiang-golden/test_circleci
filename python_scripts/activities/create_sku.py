"""Class to handle requests to create a sku"""
import datetime
import json
from db_functions import insert_into_db, select_from_db, execute_query_into_db

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks

class CreateSKU(ActivityHandler):
    """Action to create a sku"""

    required_args = {
        'name',
        'sku_name',
        'variety',
        'organization_id',
        'created_by',
        'sales_class',
        'target_qty',
        'target_qty_unit',
        'price',
        'type',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new sku inventory item"""

        cls.check_required_args(args)

        target_unit = ''

        if args['target_qty_unit'] == 'plants':
            target_unit = ' Plants'
        elif args['target_qty_unit'] == 'seeds':
            target_unit = ' Seeds'
        elif args['target_qty_unit'] == 'g-wet':
            target_unit = 'g Wet'
        else:
            target_unit = "g {}".format(args["target_qty_unit"].capitalize())

        if get_sku(args["organization_id"], args["sku_name"], args["sales_class"]) != []:
            raise ClientBadRequest(
                {
                    "code": "create_sku",
                    "message": "sku already exists"
                }, 500)

        sku_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "name": args["sku_name"],
            "variety": args["variety"],
            "sales_class": args["sales_class"],
            "target_qty": args["target_qty"],
            "target_qty_unit": args["target_qty_unit"],
            "price": args['price'],
            "type": args['type']
        }

        if "external_sku_id" in args:
            sku_object["external_sku_id"] = args["external_sku_id"]

        if "external_sku_variant_id" in args:
            sku_object["external_sku_variant_id"] = args["external_sku_variant_id"]

        if "cannabis_class" in args:
            sku_object["cannabis_class"] = args["cannabis_class"]

        sku_result = insert_into_db('Skus', sku_object)
        current_inventory = get_current_inventory(args["organization_id"], sku_result["id"])
        add_current_inventory(args["organization_id"], sku_result["id"], current_inventory)
        args["sku_id"] = sku_result["id"]
        activity_result = cls.insert_activity_into_db(args)
        
        sku_detail_webhook = get_sku_for_webhook(args["organization_id"], sku_result["id"])
        firing_webhooks(organization_id=args.get("organization_id"), event='skus.created', event_data=sku_detail_webhook)
        
        return {
            "activity_id": activity_result["id"],
            "sku_id": sku_result["id"]
        }

def get_sku_for_webhook(organization_id, sku_id):
    '''Returns sku detail by sku id'''
    params = {'organization_id': organization_id, 'sku_id': sku_id}
    query = '''
        select  s.id as sku_id, s.name, s.current_inventory, s.price, s.variety, s.id, 
        s.data->>'external_sku_id' as external_sku_id,
        s.data->>'external_sku_variant_id' as external_sku_variant_id
        from skus as s 
        where s.organization_id=%(organization_id)s
        and s.id = %(sku_id)s 
    '''
    result = select_from_db(query, params)
    if (result):            
        return result[0]


def get_sku(organization_id, name, sales_class):
    """ function to get existing SKU with same name and sales class """
    params = {'organization_id': organization_id, 'name': name, 'sales_class': sales_class }

    query = '''
    SELECT *
    FROM skus AS s
    WHERE s.organization_id = %(organization_id)s
        and s.name = %(name)s
        and s.sales_class = %(sales_class)s
    '''

    return select_from_db(query, params)


def get_current_inventory(organization_id, sku_id):
    """returns total quantity available in inventory with same name"""
    params = {
        'organization_id': organization_id,
        'sku_id': sku_id
    }

    query = '''
            SELECT COUNT(*) FROM inventories AS i
                WHERE cast(i.data->>'sku_id' as integer) = %(sku_id)s
                AND i.type = 'lot item'
                AND i.organization_id = %(organization_id)s;
            '''
    result = select_from_db(query, params)
    return result[0].get("count")


def add_current_inventory(organization_id, sku_id, current_inventory):
    '''Updates current_inventory column in skus table with current_inventory value'''
    params = {
        'organization_id': organization_id,
        'sku_id': sku_id,
        'current_inventory': current_inventory
    }
    query = '''
            UPDATE skus 
            SET current_inventory = %(current_inventory)s
            WHERE id = %(sku_id)s 
            AND organization_id = %(organization_id)s;
    '''
    return execute_query_into_db(query, params)
