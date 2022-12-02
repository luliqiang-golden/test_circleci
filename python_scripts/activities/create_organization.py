"""Create an organization"""

from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler

class CreateOrganization(ActivityHandler):
    """Activity for creating an organization

    :param org_name: name of the organization
    :param created_by: user who is creating the organization
  
    :returns: An object containing the new organization id and the corresponding activity's id 
    """
    required_args = {
        'org_name',
        'created_by'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create an organization
        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        #create a data obj containing default values for an organization
        data_object = {"theme": {"logo": ""},
                        "currency": "CAD",
                        "features": {
                                "qa": True,
                                "admin": True,
                                "orders": True,
                                "uploads": True,
                                "inventory": True,
                                "warehouse": True,
                                "accounting": True,
                                "greenhouse": True,
                                "crm-account": True,
                                "environment": True,
                                "rule-editor": True
                             },
                        "security": {
                            "scanner_timeout": 600,
                            "scanner_timeout_warning": 15
                        },
                        "created_by": args['created_by'],
                        "license_id": "123 ABC",
                        "date_format": "EEEE, MMMM d, y",
                        "date_locale": "en-US",
                        "metric_system": "metric",
                        "upload_formats": [
                            "csv",
                            "jpeg",
                            "pdf"
                        ],
                        "date_time_format": "MMM d, y, h:mm a"
                    }

        data_object['name'] = args['org_name']

        result = insert_into_db('Organizations', data_object)

        args["organization_id"] = result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "organization_id": result["id"]
        }
