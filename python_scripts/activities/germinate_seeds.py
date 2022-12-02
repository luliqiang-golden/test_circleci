"""Germinate seeds into plants"""

from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from db_functions import get_avarage_seed_weight, select_resource_from_db

class GerminateSeeds(ActivityHandler):
    """
    Action to germinate seeds
    :param to_qty: The qty of plants be recorded, it should less than or equal to from_qty
    :param to_qty_unit: The new unit for the batch, it should be plants
    :param to_inventory_id: The batch id need to be updated
    :param from_qty: The qty of batch transfer from, it should more than or equal to to_qty
    :param from_qty_unit: The old unit for the batch, it should be seeds 
    :param from_inventory_id: The batch id need to be updated, it should be same with to_inventory_id

    :returns: An object containing the new activity's id

    """

    required_args = {
        'to_qty', 'to_qty_unit', 'to_inventory_id', 'from_qty',
        'from_qty_unit', 'from_inventory_id', 'seeds_weight'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Germinate seeds into plants"""

        cls.check_required_args(args)
        
        if (args['from_qty_unit'] != 'seeds') or (args['to_qty_unit'] != 'plants'):
            raise ClientBadRequest(
                {
                    "code": "germinate_unit_mismatch",
                    "message":
                    "Germination activity must transform seeds into plants"
                }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "germinate_id_mismatch",
                "message":
                "Germination activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        if args['from_qty'] < args['to_qty'] or args['to_qty'] < 0:
            raise ClientBadRequest({
                "code":
                "germinate_qty_mismatch",
                "message":
                "Germination must result in plants being less or equal to seeds and greater or equal to zero"
            }, 400)
        
        if args['from_qty'] < 0:
            raise ClientBadRequest({
                "code":
                "germinate_qty_mismatch",
                "message":
                "Germination must not result in negative seeds"
            }, 400)

        # To get latest value of batch stats after queue_for_destruction update
        from_inventory = select_resource_from_db(resource='inventories', resource_id=args['from_inventory_id'],organization_id=args['organization_id'])
        args['from_qty'] = float(from_inventory['stats']['seeds'])

        args['seeds_weight'] = round(get_avarage_seed_weight(args['organization_id'], args['from_inventory_id'])*float(args['to_qty']),3)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
