"""  Flush Plants """

from activities.activity_handler_class import ActivityHandler


class PlantsFlush(ActivityHandler):
    """ Flush plants """

    required_args = {
        'name',
        'inventory_id',
        'flushed_by',
        'timestamp',
    }
