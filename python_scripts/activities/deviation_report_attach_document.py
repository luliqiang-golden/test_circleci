"""Class to handle requests to relate attach document to deviation report"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class DeviationReportAttachDocument(ActivityHandler):
    """Action to relate uploaded document to deviation report"""

    required_args = {
        'upload_id',
        'deviation_report_id'
    }