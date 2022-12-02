"""Record oil batch weight at the end of oil extraction (convert g-wet to g-oil)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class RecordCrudeOilWeight(ActivityHandler):
    """
    Action to record crude oil weight
    :param to_qty: The qty of crude oil weight recorded
    :param to_qty_unit: The new unit for the batch, it should be crude
    :param to_inventory_id: The batch id need to be updated
    :param from_qty: The qty of batch transfer from
    :param from_qty_unit: The old unit for the batch, it should be g-wet or dry or cured 
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
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)
        if  args['from_qty_unit'] not in ['g-wet', 'dry', 'cured', 'purchasedHemp','crude']:
            raise ClientBadRequest({
                "code":
                "batch_record_crude_oil_weight_unit_mismatch",
                "message":
                "batch record crude oil activity must transform from g-wet, dry, or cured"
            }, 400)

        if  args['to_qty_unit'] != 'crude':
            raise ClientBadRequest({
                "code":
                "batch_record_crude_oil_weight_unit_mismatch",
                "message":
                "Batch record crude oil weight activity must transform into g-oil (crude)"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "batch_record_crude_oil_weight_id_mismatch",
                "message":
                "Batch record crude oil weight activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
