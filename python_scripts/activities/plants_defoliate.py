"""  Defoliate plants """
from activities.activity_handler_class import ActivityHandler


class PlantsDefoliate(ActivityHandler):
    """ Defoliate plants """

    required_args = {
        'name',
        'inventory_id',
        'defoliated_by'
    }
