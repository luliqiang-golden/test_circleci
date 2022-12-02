"""Class to handle requests to relate attach document to crm account"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class CRMAccountAttachDocument(ActivityHandler):
    """Action to relate uploaded document to crm account"""

    required_args = {
        'name',
        'crm_account_id',
        'upload_id',
        # 'attached_by'
    }
