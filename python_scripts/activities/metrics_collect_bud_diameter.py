""" Collect bud diameter of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectBudDiameter(ActivityHandler):
    """ Record bud diameter of plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'bud_diameter',
    }
