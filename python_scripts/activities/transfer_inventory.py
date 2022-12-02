"""
transfer_inventory - move inventory quantities from one inventory item to another
"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from db_functions import update_batch_seed_weight, update_resource_attribute_into_db, DATABASE, get_avarage_seed_weight, select_resource_from_db
from stats.class_stats import Stats
import psycopg2

class TransferInventory(ActivityHandler):
    """
    Move inventory quantities from one inventory item to another

    :param from_inventory_id: Inventory ID of the source inventory item
    :param from_qty: Quantity being removed from the source inventory item
    :type from_qty: number
    :param from_qty_unit: Unit of the quantity being removed from the source inventory item

    :param to_inventory_id: Inventory ID of the target inventory item
    :param to_qty: Quantity being added to the target inventory item
    :type to_qty: number
    :param to_qty_unit: Unit of the quantity being added to the target inventory item

    :returns: An object containing the new activity's id

    :raises: 400 transfer_unit_mismatch
    :raises: 400 transfer_qty_mismatch
    """

    required_args = {
        'name',
        'to_inventory_id',
        'from_inventory_id',
        'to_qty_unit',
        'from_qty_unit',
        'to_qty',
        'from_qty',
    }
    @staticmethod
    def validate_qty_by_unit(qty, unit, max_amount):
        _qty = float(qty)
        _max_amount = float(max_amount)
        if (_qty <= 0):
            return {
                "error_message": "The value {0} must be greater than zero",
            }

        if (_qty > _max_amount):
            return {
                "error_message": "The value {0} for {1} should be less than {2}"  
            }
        
        if (unit == 'seeds' or unit == 'plants'):
            if not _qty.is_integer():
                return {
                    "error_message": "The value {0} for {1} should be an integer number",
                }
        else:
            decimal_places = str(_qty).split('.')[1]
            if (len(decimal_places) > 3):
                return {
                    "error_message": "The value {0} for {1} should be limited to 3 decimal places",
                }
        return {
            "error_message": "" 
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

        if args['from_qty_unit'] != args['to_qty_unit']:

            raise ClientBadRequest({
                "code":
                "transfer_unit_mismatch",
                "description":
                "Inventory transfers must have the same units ({0} != {1})".
                format(args['from_qty_unit'], args['to_qty_unit'])
            }, 400)

        if (args['from_qty'] != args['to_qty']) and args['mother_type'] != 'clones':
            raise ClientBadRequest({
                "code":
                "transfer_qty_mismatch",
                "description":
                "Inventory transfers with same unit type must have same qty ({0} != {1})".
                format(args['from_qty'], args['to_qty'])
            }, 400)

        DATABASE.dedicated_connection().begin()
        try:        
            from_inventory = select_resource_from_db(resource='inventories', resource_id=args["from_inventory_id"],organization_id=args["organization_id"])
           
            max_amount_from_inventory = Stats.serialize_stats(from_inventory['stats'])["qty"]
            validate_qty_object = TransferInventory.validate_qty_by_unit(args['from_qty'], args['from_qty_unit'], max_amount_from_inventory)
            if validate_qty_object["error_message"]:
                raise ClientBadRequest({
                    "code":
                    "transfer_invalid_qty",
                    "description":
                    validate_qty_object["error_message"].
                    format(args['from_qty'], args['from_qty_unit'], max_amount_from_inventory)
                }, 400)

            validate_qty_object = TransferInventory.validate_qty_by_unit(args['to_qty'], args['to_qty_unit'], max_amount_from_inventory)
            if validate_qty_object["error_message"]:
                raise ClientBadRequest({
                    "code":
                    "transfer_invalid_qty",
                    "description":
                    validate_qty_object["error_message"].
                    format(args['to_qty'], args['to_qty_unit'], max_amount_from_inventory)
                }, 400)

            result = cls.insert_activity_into_db(args)

            return_obj = {
                "activity_id": result["id"],
            }
            
            to_inventory = select_resource_from_db(resource='inventories', resource_id=args["to_inventory_id"],organization_id=args["organization_id"])
            if (from_inventory['type'] == 'received inventory' and to_inventory['type'] == 'batch' and args['from_qty_unit'] == 'seeds'):

                number_of_seeds = float(to_inventory['stats']['seeds'])

                seed_weight = get_avarage_seed_weight(args['organization_id'], args['to_inventory_id'])
                seeds_weight = round(seed_weight * number_of_seeds, 2)

                result = update_batch_seed_weight(args['to_inventory_id'], seeds_weight)
                update_resource_attribute_into_db(
                    'inventories', args['to_inventory_id'], 'seed_weight', seed_weight)

                return_obj["batch_affected_rows"] = result['affected_rows']
            
            
            DATABASE.dedicated_connection().commit()
            
            return return_obj



        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "transfer_inventory_error",
                    "message": "There was an error transfering inventory. "+error.args[0]
                }, 500)
