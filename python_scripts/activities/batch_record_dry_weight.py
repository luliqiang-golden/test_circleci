"""Record dry batch weight at the end of drying process (convert g-wet to g-dry)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class RecordDryWeight(ActivityHandler):
    """
    Action to record dry weight
    :param to_qty: The qty of dry weight recorded
    :param to_qty_unit: The new unit for the batch, it should be dry
    :param to_inventory_id: The batch id need to be updated
    :param from_qty: The qty of batch transfer from
    :param from_qty_unit: The old unit for the batch, it should be g-wet 
    :param from_inventory_id: The batch id need to be updated, it should be same with to_inventory_id

    :returns: An object containing the new activity's id

    """

    required_args = {
        'to_qty', 'to_qty_unit', 'to_inventory_id', 'from_qty',
        'from_qty_unit', 'from_inventory_id', 'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        if args['from_qty_unit'] != 'g-wet' or args['to_qty_unit'] != 'dry':
            raise ClientBadRequest({
                "code":
                "batch_record_dry_weigh_unit_mismatch",
                "message":
                "Record dry weigh activity must transform plants into g-dry(dry)"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "batch_record_dry_weigh_id_mismatch",
                "message":
                "Record dry weigh activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
