"""Record bud harvest weight (convert plants to g-wet)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class BatchRecordBudHarvestWeight(ActivityHandler):
    """Record bud harvest weight into g-wet"""

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
        
        if args['to_qty'] <= 0:
            raise ClientBadRequest(
                {
                    "code": "record_bud_harvest_weight_to_qty_error_too_small",
                    "message": "Harvest to qty must be greater than 0"
                }, 400)

        if args['from_qty'] <= 0:
            raise ClientBadRequest(
                {
                    "code": "record_bud_harvest_weight_from_qty_error_too_small",
                    "message": "Harvest from qty must be greater than 0"
                }, 400)

        if (args['from_qty_unit'] != 'plants') or (args['to_qty_unit'] != 'g-wet'):
            raise ClientBadRequest(
                {
                    "code": "harvest_unit_mismatch",
                    "message": "Harvest activity must transform plants into g-wet"
                }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "harvest_id_mismatch",
                "message":
                "Harvest activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
