"""
consumable_lot_use_items - remove consumable items as they are used
"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from db_functions import select_resource_from_db, update_into_db, DATABASE
from activities.plants_add_pesticide import PlantsAddPesticide
from activities.plants_add_ipm import PlantsAddIPM
import psycopg2

class ConsumableLotUseItems(ActivityHandler):
    """
    Remove consumable items as they are used, if the type of item is fertilizer or pesticide, then call the activity PlantsAddPesticide, the activity will record type and subtype and linked batch to track the activity
    :param current_user: current user object
    :param linked_inventory_id: inventory to be linked
    :param type: type of consumable lot
    :param subtype: subtype of consumable lot
    :param person_in_charge: the employee to charge the activity - not required because add pesticide doesn't use it
    :param from_consumable_lot_id: the id of consumable lot
    :param from_qty: the quantity of consumable lot to use
    :param from_qty_unit: the unit of consumable lot
    """

    required_args = {
        'type',
        'subtype',
        'from_consumable_lot_id',
        'from_amount',
        'from_qty',
        'from_qty_unit',
        'organization_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        """

        cls.check_required_args(args)

        consumable_lot_object = select_resource_from_db(
            'consumable_lots', args['from_consumable_lot_id'], args['organization_id'])

        current_qty = consumable_lot_object['current_qty']

        if args['from_qty'] > float(current_qty):

            raise ClientBadRequest({
                "code":
                "consumable_lot_use_items_out_of_bound",
                "description":
                "Current quantity({0}) is less than from_qty({1})".
                format(current_qty, args['from_qty'])
            }, 400)

        if args['linked_inventory_id']:
            linked_inventory = select_resource_from_db(
                'inventories', args['linked_inventory_id'], args['organization_id'])

            if not linked_inventory or (args['linked_inventory_id'] != linked_inventory['id']):

                raise ClientBadRequest({
                    "code":
                    "consumable_lot_use_items_bad_inventory",
                    "description":
                    "Linked Inventory Id #{} is not correct".
                    format(args['linked_inventory_id'])
                }, 400)

        current_qty = float(current_qty) - args['from_qty']

        DATABASE.dedicated_connection().begin()
        try:
            update_db_result = update_into_db(
                'consumable_lots', args['from_consumable_lot_id'], {'current_qty': current_qty})
            activity_result = cls.insert_activity_into_db(args)

            if args['type'].lower() == 'pesticide':
                activity_data = {
                    'organization_id': args['organization_id'],
                    'created_by': args['created_by'],
                    'inventory_id': args['linked_inventory_id'],
                    'quantity': args['from_qty'],
                    'name': 'plants_add_pesticide',
                    'from_consumable_lot_id': args['from_consumable_lot_id'],
                    'consumable_class_id': args['consumable_class_id'],
                    'pesticide_name': args['subtype'],
                    'sprayed_by': args['sprayed_by'],
                    'prepared_by': args['prepared_by'],
                    'qty_unit': args['from_qty_unit'],
                    'timestamp': args.get('timestamp') or datetime.datetime.now(),
                }
                cls.insert_activity_into_db(activity_data)

            if args['type'].lower() == 'ipm' or args['type'].lower() == 'insects' or args['type'].lower() == 'insect':
                add_ipm_data = {
                    'organization_id': args['organization_id'],
                    'created_by': args['created_by'],
                    'name': 'plants_add_ipm',
                    'from_consumable_lot_id': args['from_consumable_lot_id'],
                    'inventory_id': args['linked_inventory_id'],
                    'room': args['room'],
                    'consumable_class_id': args['consumable_class_id'],
                    'prepared_by': args['prepared_by'],
                    'added_by': args['added_by'],
                    'ipm_subtype': args['subtype'],
                    'container_qty': args['container_qty'],
                    'container_unit': args['container_unit'],
                    'pest': args['pest'],
                    'quantity': args['from_qty'],
                    'qty_unit': args['from_qty_unit'],
                    'timestamp': args.get('timestamp') or datetime.datetime.now(),
                }
                PlantsAddIPM.do_activity(add_ipm_data, {})

            
            DATABASE.dedicated_connection().commit()
            return {
                "activity_id": activity_result["id"],
                "consumable_lot_affected_rows": update_db_result['affected_rows'],
            }
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:            
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "use_consumable_item",
                    "message": "There was an error canceling an order item. Error: "+error.args[0]
                }, 500)
