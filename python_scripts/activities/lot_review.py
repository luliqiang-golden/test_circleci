"""Record lot_review"""
from activities.activity_handler_class import ActivityHandler
# from class_errors import ClientBadRequest


class LotReview(ActivityHandler):
    """Record lot_review"""

    required_args = {'name', 'inventory_id', 'lot_review_result', 'reviewed_by',
                     'to_test_status', 'timestamp'}
