"""Create Activity Log"""

from activities.activity_handler_class import ActivityHandler


class CreateActivityLog(ActivityHandler):
    """Create Activity Log"""

    required_args = {
        'name', 'inventory_id', 'description', 'detail', 'timestamp',
    }
