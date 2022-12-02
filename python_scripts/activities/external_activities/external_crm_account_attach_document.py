"""Class to handle requests to relate attach document to external crm account"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class ExternalCRMAccountAttachDocument(ActivityHandler):
    """Action to relate uploaded document to external crm account"""

    required_args = {
        'name',
        'crm_account_id',
        'upload_id'
    }
