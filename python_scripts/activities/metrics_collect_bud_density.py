""" Collect bud density of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectBudDensity(ActivityHandler):
    """ Record bud density of plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'bud_density',
    }
