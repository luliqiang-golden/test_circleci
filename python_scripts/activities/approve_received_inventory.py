"""Class to handle requests to move a received inventory item from unapproved stage to approved stage"""

from activities.activity_handler_class import ActivityHandler


class ApproveReceivedInventory(ActivityHandler):
    """Action to approve a received inventory item"""

    required_args = {
        'inventory_id',
        'quarantined',
        'to_stage',
        # 'timestamp',
    }
