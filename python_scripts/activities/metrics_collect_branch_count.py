""" Collect number of branches in plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectBranchCount(ActivityHandler):
    """ Record number of branches for plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'branch_count',
    }
