""" Collect bud moisture of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectBudMoisture(ActivityHandler):
    """ Record bud moisture of plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'bud_moisture',
    }
