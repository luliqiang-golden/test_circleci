"""Activity to update GTIN barcodes for a SKU"""

from activities.activity_handler_class import ActivityHandler
from db_functions import update_resource_attribute_into_db, DATABASE
import psycopg2

class UpdateGTINBarcodes(ActivityHandler):
    """SKU GTIN update"""

    required_args = {
        'name',
        'sku_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        if ('to_gtin_12' in args or 'from_gtin_12' in args):
            cls.required_args = cls.required_args.union(['from_gtin_12', 'to_gtin_12'])
        else:
            cls.required_args.difference_update(['from_gtin_12', 'to_gtin_12'])
        if ('to_gtin_14' in args or 'from_gtin_14' in args):
            cls.required_args = cls.required_args.union(['from_gtin_14', 'to_gtin_14'])
        else:
            cls.required_args.difference_update(['from_gtin_14', 'to_gtin_14'])
        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()
        try:
            update_result = {}
            if ('to_gtin_12' in args):
                update_result = update_resource_attribute_into_db('skus', args['sku_id'], 'gtin_12', args['to_gtin_12'])
            if ('to_gtin_14' in args):
                update_result = update_resource_attribute_into_db('skus', args['sku_id'], 'gtin_14', args['to_gtin_14'])

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
                "code": "sku_update",
                "message": "There was an error updating sku. Error: " + error.args[0]
            }, 500)