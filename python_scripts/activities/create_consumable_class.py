"""Create Consumable Class"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class CreateConsumableClass(ActivityHandler):
    """Create Consumable Class"""

    required_args = {
        'name',
        'type',
        'subtype',
        'unit',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new Consumable Class"""

        required_args = cls.required_args

        if args['unit'].lower() == 'container':
            required_args.add('containerUnit')
            required_args.add('containerQty')
            cls.required_args = required_args
        else:
            required_args.difference_update(['containerUnit', 'containerQty'])
        cls.check_required_args(args)

        consumable_class_object = {
            "type": args["type"],
            "subtype": args["subtype"],
            "unit": args["unit"],
            "status": "enabled",
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
        }

        if args['unit'] == 'container':
            consumable_class_object['containerUnit'] = args['containerUnit']
            consumable_class_object['containerQty'] = args['containerQty']

        consumable_class_result = insert_into_db(
            'consumable_classes', consumable_class_object)
        args["consumable_class_id"] = consumable_class_result['id']

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "consumable_class_id": args["consumable_class_id"]
        }
