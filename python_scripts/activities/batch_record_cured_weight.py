"""Record dry batch weight at the end of curing process (convert dry to cured)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class RecordCuredWeight(ActivityHandler):
    """
    Action to split one batch to a new batch
    :param to_qty: The qty of the parent batch transfer to new batch
    :param to_qty_unit: The unit of the child batch
    :param to_inventory_id: The new child batch's id
    :param from_qty: The qty of batch transfer from, it should be same with to_qty
    :param from_qty_unit: The unit of the parent batch, it should be same with to_qty_unit
    :param from_inventory_id: The parent batch's id

    :returns: An object containing the new activity's id

    """

    required_args = {
        'to_qty', 'to_qty_unit', 'to_inventory_id', 'from_qty',
        'from_qty_unit', 'from_inventory_id', 'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        if args['from_qty_unit'] != 'dry' or args['to_qty_unit'] != 'cured':
            raise ClientBadRequest({
                "code":
                "batch_record_cured_weight_unit_mismatch",
                "message":
                "Record cured weight activity must transform plants into g-dry"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "batch_record_cured_weight_id_mismatch",
                "message":
                "Record cured weight activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
