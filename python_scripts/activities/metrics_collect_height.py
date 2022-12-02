""" Collect height of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectHeight(ActivityHandler):
    """ Record growth of plant through height """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'height',
    }
