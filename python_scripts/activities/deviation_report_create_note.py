"""Deviation Report Create Note"""

from activities.activity_handler_class import ActivityHandler


class DeviationReportCreateNote(ActivityHandler):
    """Deviation Report Create Note"""

    required_args = {
        'deviation_report_id',
        'description',
        'detail'
    }
