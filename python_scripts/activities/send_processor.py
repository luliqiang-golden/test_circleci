"""Send to Processor"""
from pytz import timezone
from datetime import datetime
from activities.activity_handler_class import ActivityHandler
from activities.create_signature import CreateSignature
from db_functions import DATABASE, update_resource_attribute_into_db
from class_errors import ClientBadRequest

import psycopg2


class SendProcessor(ActivityHandler):
    """Send to Processor"""

    required_args = {
        "name",
        "from_inventory_id",
        "from_qty_unit",
        "from_qty",
        "crm_account_id",
        "timestamp",        
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
            
            act_result = cls.insert_activity_into_db(args)

            update_inv_result = update_resource_attribute_into_db('inventories', args["from_inventory_id"], "processor_status", 'sent_to_processor')
            update_inv_result = update_resource_attribute_into_db('inventories', args["from_inventory_id"], "room", "")

            signatures_required_fields = {
                'name': 'create_signature',
                'activity_id': act_result['id'],
                'timestamp': args['timestamp'] or datetime.now(timezone('UTC')),
                'organization_id': args['organization_id'], 
                'created_by': args['created_by']
            }

            if ('approved_by' in args):
                approved_by_obj = {
                    **signatures_required_fields,
                    'field': 'approved by',
                    'signed_by': args['approved_by']
                }
                CreateSignature.do_activity(approved_by_obj, {})

            if ('recorded_by' in args):
                recorded_by_obj = {
                    **signatures_required_fields,
                    'field': 'recorded by',
                    'signed_by': args['recorded_by']
                }
                CreateSignature.do_activity(recorded_by_obj, {})


            return_obj = {
                "activity_id": act_result["id"],
                "affected_rows_inv": update_inv_result['affected_rows'],
            }

            DATABASE.dedicated_connection().commit()

            return return_obj

        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError, Exception) as error:              
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "send_processor_error",
                "message": "There was an error sending from processor. "+error.args[0]
            }, 500)
            
