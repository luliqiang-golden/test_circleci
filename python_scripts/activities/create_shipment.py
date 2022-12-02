"""Create Shipment"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks


class CreateShipment(ActivityHandler):
    """
        Action to create an shipment
        :param crm_account_id: The existing CRM account id
        
        :returns: An object containing the new activity's id and the new shipment's id
    """

    required_args = {
        'name',
        'crm_account_id',
        'shipping_address'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new shipment        
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """

        cls.check_required_args(args)
            
        shipment_object = {
            "crm_account_id": args["crm_account_id"],
            "status" :"pending",
            "shipping_address": args["shipping_address"],
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
        }
        
        shipment_result = insert_into_db('shipments', shipment_object)
        args["shipment_id"] = shipment_result['id']
     
        activity_result = cls.insert_activity_into_db(args)
        firing_webhooks(organization_id=args["organization_id"], event='shipments.created',
                        event_data=args)
        return {
            "activity_id": activity_result["id"],
            "shipment_id": args["shipment_id"]
        }
