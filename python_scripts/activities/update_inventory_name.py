"""Update Inventory Name"""

from activities.activity_handler_class import ActivityHandler

from class_errors import ClientBadRequest
from db_functions import update_into_db, DATABASE
import psycopg2

class UpdateInventoryName(ActivityHandler):
    """Class for updating the name of an inventory"""

    required_args = {
        'to_name',
        'inventory_id',
        'inventory_type',
        'edited_by',
        'approved_by'    
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

        DATABASE.dedicated_connection().begin()
        try:
            inventory_object = {'name': args['to_name']}
            update_db_result = update_into_db('inventories', args['inventory_id'], inventory_object)
            
            result = cls.insert_activity_into_db(args)
                
            DATABASE.dedicated_connection().commit()
            
            return {
                "activity_id": result["id"],
                "affected_rows": update_db_result['affected_rows']
            }


        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "update_inventory_name_error",
                    "message": "There was an error updating the inventory name. "+error.args[0]
                }, 500)
