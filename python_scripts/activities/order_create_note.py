"""Order Create Note"""

from activities.activity_handler_class import ActivityHandler


class OrderCreateNote(ActivityHandler):
    """Order Create Note"""

    required_args = {
        'name', 'order_id', 'description', 'detail'
    }
