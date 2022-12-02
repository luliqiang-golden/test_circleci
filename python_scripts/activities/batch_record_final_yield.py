"""Record final batch weight at the end of curing process"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class BatchRecordFinalYield(ActivityHandler):
    """
    Action to record final yield
    :param to_qty: The qty of final yield recorded
    :param to_qty_unit: The new unit for the batch, it should be cured
    :param to_inventory_id: The batch id need to be updated
    :param from_qty: The qty of batch transfer from
    :param from_qty_unit: The old unit for the batch, it should be dry 
    :param from_inventory_id: The batch id need to be updated, it should be same with to_inventory_id

    :returns: An object containing the new activity's id

    """

    required_args = {
        'to_qty',
        'to_qty_unit',
        'to_inventory_id',
        'from_qty',
        'from_qty_unit',
        'from_inventory_id',
        'name'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        if args['from_qty_unit'] != 'dry' and args['to_qty_unit'] != 'cured':
            raise ClientBadRequest({
                "code":
                "batch_record_final_yield_unit_mismatch",
                "message":
                "Complete curing activity must keep plants in g-dry.dry"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "batch_record_final_yield_id_mismatch",
                "message":
                "Complete curing activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)


        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
