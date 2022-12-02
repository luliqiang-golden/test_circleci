"""Batch add additive"""

from db_functions import DATABASE
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
import psycopg2
from copy import deepcopy

class BatchAddAdditive(ActivityHandler):
    """Batch add additive"""

    required_args = {
        'additives',
        'to_inventory_id',
        'to_qty_unit',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)
        
        activities_result = []

        DATABASE.dedicated_connection().begin()     
        try:

            for additive in args["additives"]:

                additive_arg = deepcopy(args)
                additive_arg["from_inventory_id"] = additive["from_inventory_id"]
                additive_arg["from_qty_unit"] = additive["from_qty_unit"]
                additive_arg["from_qty"] = additive["from_qty"]
                additive_arg["to_qty"] = additive["from_qty"]
                additive_arg["timestamp"] = additive["timestamp"]
                # remove additives
                del additive_arg["additives"]
                activity = cls.insert_activity_into_db(additive_arg)
                activities_result.append(activity["id"])
            
            
            return {
                "adding_additives_activities": activities_result
            }
            
        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError, Exception) as error:       
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "batch_add_additives_error",
                "message": "Error adding additivies into a batch."
            }, 500)