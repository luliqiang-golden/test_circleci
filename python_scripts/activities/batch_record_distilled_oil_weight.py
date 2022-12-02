"""Record oil batch weight at the end of distilling stage (convert crude g-oil to distilled)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class RecordDistilledOilWeight(ActivityHandler):
    """
    Action to record distilled oil weight
    :param to_qty: The qty of distilled oil weight recorded
    :param to_qty_unit: The new unit for the batch, it should be distilled
    :param to_inventory_id: The batch id need to be updated
    :param from_qty: The qty of batch transfer from
    :param from_qty_unit: The old unit for the batch, it should be crude 
    :param from_inventory_id: The batch id need to be updated, it should be same with to_inventory_id
    :param oil_density: the density of the current batch
    
    :returns: An object containing the new activity's id

    """

    required_args = {
        'to_qty',
        'to_qty_unit',
        'to_inventory_id',
        'from_qty',
        'from_qty_unit',
        'from_inventory_id',
        'name',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        if  args['from_qty_unit'] not in ['crude', 'distilled']:
            raise ClientBadRequest({
                "code":
                "batch_record_distilled_oil_weight_unit_mismatch",
                "message":
                "Record distilled oil weight activity must transform from g-oil (crude) or g-oil (distilled)"
            }, 400)

        if  args['to_qty_unit'] != 'distilled':
            raise ClientBadRequest({
                "code":
                "batch_record_distilled_oil_weight_unit_mismatch",
                "message":
                "Batch record distilled oil weight activity must transform into g-oil (distilled)"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "batch_record_distilled_oil_weight_id_mismatch",
                "message":
                "Record distilled oil weight activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
