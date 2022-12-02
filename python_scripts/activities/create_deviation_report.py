"""Class to handle requests to create a deviation report"""
import psycopg2.extras

from db_functions import insert_into_db, select_from_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from activities.create_capa import CreateCapa
from activities.capa_add_link import CapaAddLink

class CreateDeviationReport(ActivityHandler):
    """Action to create a deviation report"""

    required_args = {
        'organization_id',
        'created_by',
        'deviation_report_name',
        'type',
        'effective_date',
        'relates_to',
        'potential_impact'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new deviation report"""

        cls.check_required_args(args)

        __deviation_report_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "name": args["deviation_report_name"],
            "type": args["type"],
            "status": "unsigned",
            "effective_date": args["effective_date"],
            "relates_to": args["relates_to"],
            "potential_impact": args["potential_impact"]
        }
        args['to_status'] = 'unsigned'

        deviation_report_object = cls.check_arguments(args, __deviation_report_object)

        link_capa_object = deviation_report_object

        deviation_report_result = insert_into_db('deviation_reports', deviation_report_object)
        
        if "capa_id" in link_capa_object:
            link_capa_object["deviation_report_id"] = deviation_report_result["id"]
            cls.capa_link_to_deviation_report(link_capa_object)         

        args["deviation_report_id"] = deviation_report_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "deviation_report_id": deviation_report_result["id"]
        }

    @staticmethod
    def check_arguments(args, deviation_report_object):
        if args["type"].lower() == "unplanned":
            try:
                deviation_report_object["classification"] = args["classification"]
                deviation_report_object["investigation_details"] = args["investigation_details"]
                deviation_report_object["root_cause"] = args["root_cause"]
            except:
                raise ClientBadRequest(
                {
                    "code": "create_deviation_report_error",
                    "message": "Classification, investigation details or root cause is missing"
                }, 500)

        if args["type"].lower() == "planned":
            try: 
                deviation_report_object["planned_reason"] = args["planned_reason"]
            except:
                raise ClientBadRequest(
                {
                    "code": "create_deviation_report_error",
                    "message": "Planned reason is missing"
                }, 500)
        
        if args["impact_details"]:
            deviation_report_object["impact_details"] = args["impact_details"]

        if args["additional_details"]:
            deviation_report_object["additional_details"] = args["additional_details"]
        
        if args["sop_ids"]:
            deviation_report_object["sop_ids"] = args["sop_ids"]

        if args["batch_ids"]:
            deviation_report_object["batch_ids"] = args["batch_ids"]
        
        if args["room_ids"]:
            deviation_report_object["room_ids"] = args["room_ids"]
        
        if args["consumable_ids"]:
            deviation_report_object["consumable_ids"] = args["consumable_ids"]
        
        if args["capa"] and args["capa"] is True:

            deviation_report_object["capa_id"] = CreateDeviationReport.create_capa(args)
        
        if args["related_deviation_report"] and args["related_deviation_report"] is True:
            try:
                deviation_report_object["deviation_report_ids"] = args["deviation_report_ids"]
            except:
                raise ClientBadRequest(
                {
                    "code": "create_deviation_report_error",
                    "message": "Related deviation ids are missing"
                }, 500)
        
        return deviation_report_object

    @staticmethod
    def create_capa(args):
        capa_record = {
                "name": "create_capa",
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "description": args["capa_name"],
                "reported_by": CreateDeviationReport.get_user_by_id(args)["name"]
            }
        return CreateCapa.do_activity(capa_record, {})

    @staticmethod
    def capa_link_to_deviation_report(deviation_report):
        capa_link_record = {
            "name": "capa_add_link",
            "organization_id": deviation_report["organization_id"],
            "created_by": deviation_report["created_by"],
            "capa_id": deviation_report["capa_id"]["capa_id"],
            "link_type": "deviation report",
            "link_id": deviation_report["deviation_report_id"]
        }

        CapaAddLink.do_activity(capa_link_record, {})  

    @staticmethod
    def get_user_by_id(args):
        params = {"id": args["created_by"]}
        query = '''
            SELECT *
            FROM users
            WHERE id = %(id)s
            limit 1 
        '''
        return select_from_db(query, params)[0]