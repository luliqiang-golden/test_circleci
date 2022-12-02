"""Record batch_qa_review"""
from activities.activity_handler_class import ActivityHandler
# from class_errors import ClientBadRequest


class BatchQaReview(ActivityHandler):
    """Record batch_qa_review"""

    required_args = {'name', 'inventory_id', 'qa_review_result', 'reviewed_by',
                     'to_test_status'}
