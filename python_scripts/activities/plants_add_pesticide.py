""" Add pesticides to plants """

from activities.activity_handler_class import ActivityHandler


class PlantsAddPesticide(ActivityHandler):
    """ Add pesticides to plants """

    required_args = {
        'name',
        'inventory_id',
        'prepared_by',
        'sprayed_by',
        'pesticide_name',
        'quantity',
        'qty_unit',
        'organization_id',
        'timestamp',
    }
