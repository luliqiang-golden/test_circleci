"""Propagate cuttings from one plant to another"""

from activities.activity_handler_class import ActivityHandler


class PropagateCuttings(ActivityHandler):
    """Create plant inventory from a mother"""

    required_args = {
        'to_inventory_id',
        'to_qty',
        'to_qty_unit',
        'from_inventory_id',
        'name',
        'timestamp',
    }
