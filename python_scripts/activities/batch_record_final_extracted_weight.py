"""Batch record the final extracted weight"""
from copy import deepcopy

from db_functions import DATABASE
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from activities.update_room import UpdateRoom
import psycopg2
from datetime import datetime


class BatchRecordFinalExtractedWeight(ActivityHandler):
    """Batch record the extracted weight"""

    required_args = {"from_inventory_id",
                     "to_inventory_id",
                     "from_qty_unit",
                     "to_qty_unit",
                     "timestamp",
                     "from_qty",
                     "to_qty",
                     "name"
                    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()       
        try:

            newargs = deepcopy(args)
            newargs['from_inventory_id'] = args['from_inventory_id']
            newargs['to_inventory_id'] = args['to_inventory_id']
            newargs['from_qty'] = args['from_qty']
            newargs['from_qty_unit'] = args['from_qty_unit']
            newargs['to_qty_unit'] = args['to_qty_unit']
            newargs['timestamp'] = args['timestamp']
            newargs['to_qty'] = args['to_qty']

            activity_result = cls.insert_activity_into_db(newargs)

            if args.get("room"):
                update_room_args = {
                    "name": "update_room",
                    "inventory_id": newargs["from_inventory_id"],
                    "to_room": newargs["room"],
                    "organization_id": newargs["organization_id"],
                    "created_by": newargs["created_by"],
                    "timestamp": newargs["timestamp"],
                }
                UpdateRoom.do_activity(update_room_args, current_user)

         
            DATABASE.dedicated_connection().commit()
            
            return {
                "activity_id": activity_result["id"]
            }

        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError, Exception) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "batch_record_extracted_final_weight_error",
                "message": "Error recording final weight extraction."
            }, 500)

        

        