"""split batch to 2 batches"""
import datetime
import json
import decimal
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from db_functions import select_resource_from_db, insert_into_db

class DecimalEncoder(json.JSONEncoder):
    """use to transfer decimal to float"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return (self, obj)


class SplitBatch(ActivityHandler):
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
        "to_qty",
        "from_qty",
        "to_qty_unit",
        "from_qty_unit",
        "from_inventory_id",
        "timestamp",
        }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new batch which has the same plan and attribute with the origin one"""

        cls.check_required_args(args)

        if args['from_qty_unit'] != args['to_qty_unit']:
            raise ClientBadRequest({
                "code":
                "split_batch_unit_mismatch",
                "message":
                "Split batch activity must have the same from_qty_unit and to_qty_unit ({0} != {1})".
                format(args['from_qty_unit'], args['to_qty_unit'])
            }, 400)

        if args['from_qty'] != args['to_qty']:
            raise ClientBadRequest({
                "code":
                "split_batch_qty_mismatch",
                "message":
                "Split batch activity must have the same from_qty and to_qty ({0} != {1})".
                format(args['from_qty'], args['to_qty'])
            }, 400)

        parent_batch_inventory = select_resource_from_db(
            "inventories", args["from_inventory_id"], args["organization_id"])
        
        variety = parent_batch_inventory["variety"]
        inventory_name = "{0}-{1}-{2}".format(
            variety,
            datetime.datetime.now().isocalendar()[1],
            datetime.datetime.now().year % 100,
        )
        
        inventory_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "batch",
            "variety": variety,
            "variety_id": parent_batch_inventory["variety_id"],
            "name": inventory_name,
            "plan": parent_batch_inventory["plan"],
            "attributes": json.dumps(parent_batch_inventory["attributes"], cls=DecimalEncoder),
            "timestamp": args["timestamp"] or datetime.datetime.now(),
        }

        inventory_result = insert_into_db("Inventories", inventory_object)

      
        args["to_inventory_id"] = inventory_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "inventory_id": args["to_inventory_id"]
            }
