""" Collect internodal space of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectInternodalSpace(ActivityHandler):
    """ Record internodal space of plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'internodal_space',
    }
