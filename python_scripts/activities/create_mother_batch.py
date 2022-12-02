"""Class to handle requests to create a batch that will receive inventory"""
import datetime
import psycopg2

from db_functions import insert_into_db, DATABASE
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from activities.transfer_mother_plants_to_mother_batch import TransferMotherPlantsToMotherBatch



class CreateMotherBatch(ActivityHandler):
    """Action to create a mother batch"""

    required_args = {
        'variety',
        'variety_id',
        'name',
        'inventory_name',
        'added_by',
        'approved_by',
        'timestamp',

    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new mother batch inventory item"""        

        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()
        try:

            inventory_object = {
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "type": "mother batch",
                "variety": args["variety"],
                "variety_id": args["variety_id"],
                "added_by": args["added_by"],
                "approved_by": args["approved_by"],
                "name": args['inventory_name'],
                "timestamp": args['timestamp'] or datetime.datetime.now(),
            }

            
            inventory_result = insert_into_db('Inventories', inventory_object)

            args["inventory_id"] = inventory_result["id"]

            activity_result = cls.insert_activity_into_db(args)


            if args.get("mother_ids"):
                for from_id in args["mother_ids"]:
                    transf_args = {
                        "name": "transfer_mother_plants_to_mother_batch",
                        "organization_id": args["organization_id"],
                        "created_by": args["created_by"],
                        "to_inventory_id": inventory_result["id"],
                        "from_inventory_id": from_id,
                        "timestamp": args['timestamp'] or datetime.datetime.now(),
                    }
                    TransferMotherPlantsToMotherBatch.do_activity(transf_args, current_user)

            DATABASE.dedicated_connection().commit()
            return {
                "activity_id": activity_result["id"],
                "inventory_id": inventory_result["id"]
            }
        
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "create_mother_batch",
                    "message": "There was an error creating a mother batch. "+error.args[0]
                }, 500)
