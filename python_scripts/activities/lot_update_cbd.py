"""Activity to update CBD details for a lot"""

from activities.activity_handler_class import ActivityHandler
from db_functions import update_resource_attribute_into_db, DATABASE
import psycopg2

class UpdateCbd(ActivityHandler):
    """Lot CBD update"""

    required_args = {
        'name',
        'to_cbd_ratio',
        'cbd_unit',
        'inventory_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        if ('to_cbd_ratio' not in args):
            cls.required_args.add('to_cbd_percentage')
            cls.required_args.difference_update(['to_cbd_ratio'])
        else:
            cls.required_args.difference_update(['to_cbd_percentage'])
        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()

        try:
            update_result = {}
            if ('to_cbd_ratio' in args):
                update_result = update_resource_attribute_into_db('inventories', args['inventory_id'], 'cbd_ratio', args['to_cbd_ratio'])
            if ('to_cbd_percentage' in args):
                update_result = update_resource_attribute_into_db('inventories', args['inventory_id'], 'cbd_percentage', args['to_cbd_percentage'])


            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()

            return {
                "activity_id": activity_result["id"],
                "affected_rows": update_result['affected_rows']
            }
        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "lot_update_cbd",
                "message": "There was an error updating cbd. Error: " + error.args[0]
            }, 500)