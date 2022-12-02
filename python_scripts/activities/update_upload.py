"""Update upload"""

from class_errors import ClientBadRequest


def do_activity(args, current_user):
    """uploading files if all conditions are met"""

    raise ClientBadRequest({
        "code":
        "use_rest_endpoint",
        "message":
        "An upload_update activity can only be created by POSTing or PATCHing an upload directly to database"
    }, 500)
