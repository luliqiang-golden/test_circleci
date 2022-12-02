"""Org Update Temperature Scale"""

from db_functions import update_into_db
from db_functions import update_resource_attribute_into_db, select_from_db, delete_from_db, DATABASE
from class_errors import ClientBadRequest
import psycopg2


from activities.activity_handler_class import ActivityHandler


class OrgUpdateTemperatureScale(ActivityHandler):
    """Org Update Temperature Scale"""

    required_args = {'name', 'organization_id', 'temperature_scale'}

    @classmethod
    def do_activity(cls, args, current_user):
                
        cls.check_required_args(args)
        DATABASE.dedicated_connection().begin()       
        try:
            update_value = {"temperature_scale": args['temperature_scale']}
            update_result = update_into_db('organizations', args['organization_id'],
                                   update_value)
            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()        
            return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }

        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "update__temperature_scale",
                "message": "There was an error updating status of an order. Error: "+error.args[0]
            }, 500)
