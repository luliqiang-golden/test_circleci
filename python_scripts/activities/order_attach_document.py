"""Class to handle requests to relate attach document to order"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class OrderAttachDocument(ActivityHandler):
    """Action to relate uploaded document to order"""

    required_args = {
        'name',
        'crm_account_id',
        'order_id',
        'upload_id'
    }
