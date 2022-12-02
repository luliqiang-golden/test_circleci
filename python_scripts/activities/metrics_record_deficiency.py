""" Record deficiency in plants """

from activities.activity_handler_class import ActivityHandler


class MetricsRecordDeficiency(ActivityHandler):
    """ Record deficiency in plants """

    required_args = {
        'name',
        'inventory_id',
        'recorded_by',
        'deficiency',
        'plants_affected',
        'description',
    }
