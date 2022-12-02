"""Record sample_sent_to_lab"""
from activities.activity_handler_class import ActivityHandler
# from class_errors import ClientBadRequest


class SampleSentToLab(ActivityHandler):
    """
    Record sample_sent_to_lab
    :param related_id: The batch id the sample comes from
    :param from_inventory_id: The id used to subtract stats when sending the sample to the lab
    :param batch_in_qa: boolean indicating whether this batch was in QA when it was generated
    :param inventory_id: The sample id
    :param to_test_status: The test status of the sample, if batch_in_qa is true, this gets sent to batch as well
    """

    required_args = {'from_inventory_id', 'name', 'sample_sent_by', 'lab_name',
                     'from_qty', 'from_qty_unit', 'inventory_id', 'to_test_status',
                     'related_inventory_id', 'timestamp'}

    @classmethod
    def do_activity(cls, args, current_user):

        cls.check_required_args(args)
        
        """ If batch in qa is not an arg, then the data is old and it came from qa """
        if 'batch_in_qa' not in args.keys():
            args['batch_in_qa'] = True

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
