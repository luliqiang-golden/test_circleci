"""Batch Create Sample"""
import datetime
import psycopg2

from db_functions import DATABASE, insert_into_db, get_avarage_seed_weight, select_resource_from_db, update_batch_seed_weight
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class CreateSample(ActivityHandler):
    """
    Create Sample
    :param related_id: The batch id the sample comes from
    :param from_inventory_id: The id used to subtract stats while transfering sample data 
    :param batch_in_qa: boolean indicating whether this batch was in QA when it was generated
    :param inventory_id: The sample id
    :param to_test_status: The test status of the sample, if batch_in_qa is true, this gets sent to batch as well
    """

    required_args = {
        'name', 'from_inventory_id', 'sampled_by', 'approved_by', 'variety', 'created_by', 'to_test_status', 'to_qty', 'to_qty_unit', 'from_qty', 'from_qty_unit', 'related_inventory_id', 'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Create a new sample inventory item
        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        if args['from_qty_unit'] != args['to_qty_unit'] and args['from_qty_unit'] != 'plants':

            raise ClientBadRequest({
                "code":
                "create_sample_unit_mismatch",
                "description":
                "Create sample transfer (besides plants) must have the same units ({0} != {1})".
                format(args['from_qty_unit'], args['to_qty_unit'])
            }, 400)

        if args['from_qty'] != args['to_qty'] and args['from_qty_unit'] != 'plants':
            raise ClientBadRequest({
                "code":
                "create_sample_qty_mismatch",
                "description":
                "Create sample transfer with same unit type (besides plants) must have same qty ({0} != {1})".
                format(args['from_qty'], args['to_qty'])
            }, 400)

        if args['from_qty_unit'] == 'plants' and args['to_qty_unit'] != 'g-wet':
            raise ClientBadRequest({
                "code":
                "create_sample_unit_mismatch",
                "description":
                "Create sample for plants must transfer to g-wet ({0} != {1})".
                format(args['from_qty_unit'], args['to_qty_unit'])
            }, 400)

        if args['from_qty_unit'] == 'plants' and args['from_qty'] != 0:
            raise ClientBadRequest({
                "code":
                "create_sample_qty_mismatch",
                "description":
                "Create sample for plants must be have from_qty = 0 ({0} != {1})".
                format(args['from_qty'], args['to_qty'])
            }, 400)

        DATABASE.dedicated_connection().begin()

        try:
            inventory_name = "{0}-{1}-{2}".format(
                args["variety"],
                datetime.datetime.now().isocalendar()[1],
                datetime.datetime.now().year % 100,
            )

            """ If batch in qa is not an arg, then the data is old and it came from qa """
            if 'batch_in_qa' not in args.keys():
                args['batch_in_qa'] = True

            inventory_object = {
                "type": "sample",
                "variety": args["variety"],
                "from_inventory_id": args["from_inventory_id"],
                "batch_in_qa": args["batch_in_qa"],
                "organization_id": args["organization_id"],
                "created_by": args["created_by"],
                "name": inventory_name,
                "timestamp": args["timestamp"],
            }

            return_obj = {}

            if args['from_qty_unit'] == 'seeds':
                inventory = select_resource_from_db(resource='inventories', resource_id=args["from_inventory_id"],organization_id=args["organization_id"])
                if inventory and inventory['type'] == 'batch':
                    inventory_object['seeds_weight'] = round(get_avarage_seed_weight(args['organization_id'], args['from_inventory_id']) * float(args['to_qty']), 2)
                    args["seeds_weight"] = inventory_object['seeds_weight']

                    # update batch's seed weight 
                    current_seeds_weight = float(inventory['attributes']['seeds_weight']) - float(args["seeds_weight"]) 

                    result = update_batch_seed_weight(args['from_inventory_id'], current_seeds_weight)
                    return_obj["batch_affected_rows"] = result['affected_rows']

            inventory_result = insert_into_db('Inventories', inventory_object)
            return_obj["inventory_id"] = inventory_result["id"]

            args["to_inventory_id"] = inventory_result["id"]
            args["inventory_id"] = inventory_result["id"]
            
            activity_result = cls.insert_activity_into_db(args)

            return_obj["activity_id"] = activity_result["id"]

            DATABASE.dedicated_connection().commit()

            return return_obj


        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:              
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "create_sample_error",
                    "message": "There was an error creating a sample. "+error.args[0]
                }, 500)
