"""Class to handle requests to external crm account update"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class ExternalCRMAccountUpdateStatus(ActivityHandler):
    """Action to update external crm account"""

    required_args = {
        'name',
        'crm_account_id',
        'to_status',
        'updated_by'
    }
