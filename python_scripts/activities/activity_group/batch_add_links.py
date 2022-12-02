""" 
- Attention

- It is an activity group and because of that, batch_add_links is NOT an activitiy in our database
- Activity Group is a way that we found to avoid to call 2 or more times from frontend to api
- WHY? So, it is being used to guarante that if the first call fails then we are able to do the rollback process
- In this case we will have 3 reals activities which are:
    + capa_add_link
    + deviation_report_add_link
    + sop_add_link
- batch_add_links is not a real activity in our database. It's an activity group which is not the same

"""

import psycopg2.extras
from class_errors import ClientBadRequest
from db_functions import DATABASE
from activities.activity_handler_class import ActivityHandler
from activities.capa_add_link import CapaAddLink
from activities.deviation_report_add_link import DeviationReportAddLink
from activities.sop_add_link import SopAddLink

class BatchAddLinks(ActivityHandler):
    """Action to create and link the following documents
       + Deviation Report
       + SOP
       + Capa
       {
           organization_id
           created_by
           inventory_id
           name
           sop_id
           sop_version_number -> when sop_id has value
           deviation_report_id
           capa_id
       }
    """
    required_args = {
        'organization_id',
        'created_by',
        'inventory_id',
        'name'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Batch Add Links to (SOP, Deviation Report and CAPA)"""

        cls.check_required_args(args)

        cls.validate(args)

        DATABASE.dedicated_connection().begin()

        try:
            result = {}

            if ("capa_id" in args and args["capa_id"]):
                do_capa_link_result = cls.do_capa_add_link(args)
                result = {
                    **result,
                    **do_capa_link_result
                }
            if ("sop_id" in args and args["sop_id"]):
                if ("sop_version_number" in args and args["sop_version_number"]):
                    do_sop_link_result = cls.do_sop_add_link(args)
                    result = {
                        **result,
                        **do_sop_link_result
                    }
            if ("deviation_report_id" in args and args["deviation_report_id"]):
                do_deviation_report_result = cls.do_deviation_report_add_link(args)
                result = {
                    **result,
                    **do_deviation_report_result
                }

            DATABASE.dedicated_connection().commit()

            return result
            """ response payload
                {
                    capa_link_id: id generated when value is inserted into capa_links table
                    capa_link_activity_id: id generated when capa_add_link activity is inserted
                    deviation_report_link_activity_id: id generated when deviation_report_add_link activity is inserted
                    sop_link_activity_id: id generated when sop_add_link activity is inserted
                }
            """

        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "create_batch_link_reports",
                    "message": "There was an error linking reports. "+error.args[0]
                }, 500)

            
    @classmethod
    def validate(cls, args):
        is_valid = False
        if ("capa_id" in args and args["capa_id"]):
	        is_valid = True
        if ("deviation_report_id" in args and args["deviation_report_id"]):
	        is_valid = True
        if ("sop_id" in args and args["sop_id"]):
            if ("sop_version_number" in args and args["sop_version_number"]):
	            is_valid = True
        
        if (not is_valid):
            raise ClientBadRequest(
                {
                    "code": "create_batch_link_reports_error",
                    "message": "CAPA or SOP or Deviation Report is missing"
                }, 500)
        
    @classmethod
    def do_capa_add_link(cls, args):
        capa_add_link_args = {
            "name": "capa_add_link",
            "organization_id": args["organization_id"], 
            "created_by": args["created_by"],
            "inventory_id": args["inventory_id"],
            "link_id": args["inventory_id"],
            "link_type": "batch",
            "capa_id": args["capa_id"]
        }
        result = CapaAddLink.do_activity(capa_add_link_args, {})
        return {
            "capa_link_id": result["capa_link_id"],
            "capa_link_activity_id": result["activity_id"]
        }
    
    @classmethod
    def do_deviation_report_add_link(cls, args):
        deviation_report_add_link_args = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "inventory_id": args["inventory_id"],
            "link_id": args["inventory_id"],
            "link_type": "batch",
            "deviation_report_id": args["deviation_report_id"]
        }
        result = DeviationReportAddLink.do_activity(deviation_report_add_link_args, {})
        return {
            "deviation_report_link_activity_id": result["activity_id"]
        }

    @classmethod
    def do_sop_add_link(cls, args):
        sop_add_link_args = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "inventory_id": args["inventory_id"],
            "link_id": args["inventory_id"],
            "link_type": "batch",
            "sop_id": args["sop_id"],
            "sop_version_number": args["sop_version_number"]
        }
        result = SopAddLink.do_activity(sop_add_link_args, {})
        return {
            "sop_link_activity_id": result["activity_id"]
        }
