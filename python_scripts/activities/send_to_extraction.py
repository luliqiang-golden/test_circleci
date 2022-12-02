"""Batch record the extracted weight"""

from db_functions import DATABASE, update_into_db, update_resource_attribute_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from activities.create_batch import CreateBatch
from class_stages import BatchStages
from activities.update_room import UpdateRoom
from activities.batch_plan_update import BatchPlanUpdate
from activities.update_stage import UpdateStage
import psycopg2
from datetime import datetime


class SendToExtraction(ActivityHandler):
    """Send to Extraction"""

    required_args = {"from_inventory_id", 
                     "from_qty_unit",
                     "from_qty",
                     "variety",
                     "variety_id",
                     "custom_name",
                     "room",
                     "name",
                     "end_type",
                    }

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()       
        try:      
            batch_args = {
                "name": "create_batch",
                "variety": args["variety"],
                "variety_id": args["variety_id"],
                "custom_name": args["custom_name"],
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "timestamp": args.get("timestamp", datetime.now()),
            }

            create_batch_result = CreateBatch.do_activity(batch_args, current_user)

            args["to_inventory_id"] = create_batch_result["inventory_id"]
            args["to_qty"] = args["from_qty"]
            args["to_qty_unit"] = args["from_qty_unit"]


            activity_result = cls.insert_activity_into_db(args)

            update_room_args = {
                "name": "update_room",
                "inventory_id": create_batch_result["inventory_id"],
                "to_room": args["room"],
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "timestamp": args.get("timestamp", datetime.now()),
            }
            UpdateRoom.do_activity(update_room_args, current_user)

            batchStage = BatchStages()

            stages = batchStage.get_stages_from_type(args['to_qty_unit'], args['end_type'])
            timeline = []
            for stage in stages:
                timeline.append({"name": stage, "planned_length": ''})


            plan = {
                "start_type": args["to_qty_unit"],
                "end_type": args["end_type"],
                "start_date": args.get("timestamp", datetime.now()),
                "timeline": timeline
            }

            update_plan_args = {
                "name": "batch_plan_update",
                "inventory_id": create_batch_result["inventory_id"],
                "plan": plan,
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "timestamp": args.get("timestamp", datetime.now()),
            }
            BatchPlanUpdate.do_activity(update_plan_args, current_user)



            updateStageData = {
                "name": "update_stage",
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "inventory_id": create_batch_result["inventory_id"], 
                "to_stage": "planning",
                "timestamp": args.get("timestamp", datetime.now()),
            }
                

            UpdateStage.do_activity(updateStageData, current_user)        
            DATABASE.dedicated_connection().commit()
            
            return {
                "activity_id": activity_result["id"],
                "batch_id": create_batch_result["inventory_id"]
            }

        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError, Exception) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "batch_record_extracted_weight_error",
                "message": "Error recording weight extraction."
            }, 500)

        

        