"""Prune plants"""

from activities.activity_handler_class import ActivityHandler
from activities.queue_for_destruction import QueueForDestruction
from db_functions import select_resource_from_db


class PlantsPrune(ActivityHandler):
    """ 
        Action to Prune plants
        :param variety: The variety of the pruned batch
        :param inventory_id: The id of the batch pruned
        :param quantity: The quantity of batch pruned
        :param weighed_by: The person who wheighed the pruned materials
        :param checked_by: The person who checkd the pruning
        :param collected_from: The room in which the pruning was done
    """

    required_args = {
        'name',
        'variety',
        'inventory_id',
        'quantity',
        'weighed_by',
        'checked_by',
        'collected_from',
        'part_pruned',
        'timestamp',
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
        activity_result = cls.insert_activity_into_db(args)

        queue_for_destruction_data = {
            "name": "queue_for_destruction",
            "organization_id": args['organization_id'],
            "created_by": args['created_by'],
            "from_inventory_id": args['inventory_id'],
            "to_qty_unit": 'g-wet',
            "to_qty": args['quantity'],
            "from_qty_unit": 'g-wet',
            "from_qty": 0,
            "variety": args['variety'],
            "weighed_by": args['weighed_by'],
            "checked_by": args['checked_by'],
            "reason_for_destruction": "pruning",
            "type_of_waste": args['part_pruned'],
            "collected_from": args['collected_from'],
            "plants_prune_activity_id": activity_result['id'],
            "timestamp" : args['timestamp']
        }

        result = QueueForDestruction.do_activity(queue_for_destruction_data, {})

        return {
            "activity_id": activity_result["id"],
            "destruction_item_id": result["inventory_id"],
        }
