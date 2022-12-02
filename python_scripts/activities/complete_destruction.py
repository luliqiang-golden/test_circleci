"""Class to handle requests to complete a destruction event. Hint: you should use the REST interface instead"""
from class_errors import ClientBadRequest


def do_activity(args, current_user):
    """Action to complete a destruction event"""

    raise ClientBadRequest({
        "code":
        "use_rest_endpoint",
        "message":
        "A complete_destruction activity can only be created by POSTing a destroy_material activity"
    }, 500)
