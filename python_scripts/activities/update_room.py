"""Update room"""

from activities.activity_handler_class import ActivityHandler


class UpdateRoom(ActivityHandler):
    """Updating room if all conditions are met"""

    required_args = {'to_room', 'inventory_id'}	
