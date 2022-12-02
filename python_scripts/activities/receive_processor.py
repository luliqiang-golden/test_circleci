"""Receive from Processor"""
from pytz import timezone
from datetime import datetime
from activities.activity_handler_class import ActivityHandler
from activities.create_signature import CreateSignature
from db_functions import DATABASE, select_from_db, update_resource_attribute_into_db, select_resource_from_db
from class_errors import ClientBadRequest
from activities.update_stage import UpdateStage

import psycopg2


class ReceiveProcessor(ActivityHandler):
    """Receive from Processor"""
      
    required_args = {
        "name",
        "to_inventory_id",
        "to_qty",
        "to_qty_unit",
        "room",
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

            send_processor_obj = cls.get_last_send_processor_activity(args["organization_id"], args["to_inventory_id"])
            from_unit = send_processor_obj["data"]["from_qty_unit"]
            to_unit = args["to_qty_unit"]

            args["send_processor_act_id"] = send_processor_obj["id"],
            args["crm_account_id"] =  send_processor_obj["data"]["crm_account_id"],
            
            act_result = cls.insert_activity_into_db(args)

            processor_status = "received_from_processor_{}".format(args["test_result"]) if args.get("test_result") else "received_from_processor"
            update_inv_result = update_resource_attribute_into_db('inventories', args["to_inventory_id"], "processor_status", processor_status)
            update_inv_result = update_resource_attribute_into_db('inventories', args["to_inventory_id"], "room", args["room"])

            
        
            update_stage_obj = {
                'name': 'update_stage',
                'inventory_id': args["to_inventory_id"],
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.now(timezone('UTC')),
            }

            update_stage_result = None
 
            if (from_unit == "g-wet" and to_unit == "cured"):
                update_stage_obj["to_stage"] = 'curing'
                update_stage_result  = UpdateStage.do_activity(update_stage_obj, current_user)


            if (from_unit == "g-wet" and to_unit == "distilled"):
                update_stage_obj["to_stage"] = 'distilling'
                update_stage_result = UpdateStage.do_activity(update_stage_obj, current_user)




            return_obj = {
                "activity_id": act_result["id"],
                 "affected_rows_inv": update_inv_result['affected_rows'],
            }

            if (update_stage_result):
                return_obj["update_stage_act_id"] = update_stage_result["activity_id"]

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


        

            DATABASE.dedicated_connection().commit()

            return return_obj

        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError, Exception) as error:              
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "receive_processor_error",
                "message": "There was an error returning from processor. "+error.args[0]
            }, 500)
            

    def get_last_send_processor_activity(org_id, inventory_id):
        params = { 'org_id': org_id, "inventory_id": inventory_id }
        
        query = '''
            select * from activities
            where name = 'send_processor' and 
                cast(data->>'from_inventory_id' as numeric) = %(inventory_id)s  and 
                organization_id = %(org_id)s  
            order by id desc limit 1
        '''

        result = select_from_db(query, params)
        if (result):            
            return result[0]


    


    