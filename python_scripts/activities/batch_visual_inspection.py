""" Batch Visual Inspection """

from activities.activity_handler_class import ActivityHandler


class BatchVisualInspection(ActivityHandler):
    """
    Perform Batch Visual Inspection

    :param inventory_id: Inventory ID of the batch being inspected
    :type inventory_id: str
    :param inspection_result: 'pass' or 'fail'
    """

    required_args = {
        'name',
        'inventory_id',
        'inspection_result',
        'inspected_by',
        'approved_by',
        'to_test_status',
        'timestamp',
    }
