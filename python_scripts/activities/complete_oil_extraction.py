"""Complete oil extraction process (convert g-wet to ml)"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class CompleteOilExtraction(ActivityHandler):
    """Class for recording the end of oil extraction for a batch"""

    required_args = {
        'to_qty', 'to_qty_unit', 'to_inventory_id', 'from_qty',
        'from_qty_unit', 'from_inventory_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):

        cls.check_required_args(args)

        if (args['from_qty_unit'] != 'g-wet') or (args['to_qty_unit'] != 'g-oil'):
            raise ClientBadRequest({
                "code":
                "complete_oil_extraction_unit_mismatch",
                "message":
                "Complete oil extraction activity must transform g-wet into g-oil"
            }, 400)

        if args['to_inventory_id'] != args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "complete_oil_extraction_id_mismatch",
                "message":
                "Complete oil extraction activity must have same from and to inventory ID ({0} != {1})".
                format(args['from_inventory_id'], args['to_inventory_id'])
            }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
