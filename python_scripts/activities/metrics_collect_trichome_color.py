""" Collect trichome color of plants """

from activities.activity_handler_class import ActivityHandler


class MetricsCollectTrichomeColor(ActivityHandler):
    """ Record trichome color of plants """

    required_args = {
        'name',
        'inventory_id',
        'collected_by',
        'trichome_color',
    }
