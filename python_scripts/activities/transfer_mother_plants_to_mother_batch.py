"""
transfer_mother_plants_to_mother_batch - move mother plants to the mother batch
"""
from datetime import datetime
import psycopg2.extras

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from activities.update_mother_status import MotherUpdateStatus


class TransferMotherPlantsToMotherBatch(ActivityHandler):
    """
    to_inventory_id: mother batch's id
    from_inventory_id: mother plant's id
    """

    required_args = {
        'name',
        'to_inventory_id',
        'from_inventory_id',
        'organization_id',
        'created_by',
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

        if args['to_inventory_id'] == args['from_inventory_id']:
            raise ClientBadRequest({
                "code":
                "transfer_id_same",
                "description":
                "Transfer plants must between 2 different batch ({0} == {1})".
                format(args['to_inventory_id'], args['from_inventory_id'])
            }, 400)

        args["from_qty_unit"] = "plants"
        args["to_qty_unit"] = "plants"
        args["to_qty"] = 1
        args["from_qty"] = 1

        result = cls.insert_activity_into_db(args)

        update_mother_status_result = cls.update_mother_status(args)

        return_obj = {
            "activity_id": result["id"],
            "update_mother_status_activity_id" : update_mother_status_result["activity_id"],
        }

        return return_obj


    @classmethod
    def update_mother_status(cls, args):


        update_mother_status_args = {
            "name": "update_mother_status",
            "organization_id": args['organization_id'],
            "created_by": args['created_by'],
            "inventory_id": args['from_inventory_id'],
            "to_status": "added_to_batch",
            "timestamp": args['timestamp'] or datetime.datetime.now(),
        }

        try: 
            return MotherUpdateStatus.do_activity(update_mother_status_args, {})
        except:
            print('Error: cannot do activity update_mother_status')
            raise
        

