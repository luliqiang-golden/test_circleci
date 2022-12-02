# """Class to handle requests to update a sku status"""

from activities.activity_handler_class import ActivityHandler


class UpdateStatus(ActivityHandler):

    required_args = {'to_status', 'sku_id'}
