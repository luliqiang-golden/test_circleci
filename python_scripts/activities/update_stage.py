"""Update stage"""

from datetime import datetime
from activities.activity_handler_class import ActivityHandler

from class_errors import ClientBadRequest
from db_functions import update_salvage_batch, update_resource_attribute_into_db, DATABASE, select_resource_from_db
import psycopg2

class UpdateStage(ActivityHandler):
    """Class for updating the stage of an inventory item"""

    required_args = {'to_stage', 'inventory_id', 'timestamp'} 


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

        DATABASE.dedicated_connection().begin()
        try:        
            result = cls.insert_activity_into_db(args)

            return_obj = {
                "activity_id": result["id"],
                "timestamp": args["timestamp"] or datetime.datetime.now(),
            }

            if args['to_stage'] == 'qa':
 
                from_inventory = select_resource_from_db(resource='inventories', resource_id=args["inventory_id"],organization_id=args["organization_id"])
        
                if from_inventory['type'] == 'batch' and 'salvage_batch' in from_inventory['attributes'] and from_inventory['attributes']['salvage_batch']:
                    result = update_salvage_batch(args['inventory_id'], False)
                    return_obj["batch_affected_rows"] = result['affected_rows']
                
            DATABASE.dedicated_connection().commit()
            
            return return_obj


        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "salvage_batch_error",
                    "message": "There was an error salvaging the batch. "+error.args[0]
                }, 500)
