"""Class to handle requests to update a mother status"""

from activities.activity_handler_class import ActivityHandler

class MotherUpdateStatus(ActivityHandler):
    """Updating status"""

    required_args = {'to_status', 'inventory_id'}