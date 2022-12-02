"""Class to handle requests to create a rule. Hint: you should use the REST interface instead"""

from class_errors import ClientBadRequest


def do_activity(args, current_user):
    """Action to update a rule"""

    raise ClientBadRequest({
        "code":
        "use_rest_endpoint",
        "message":
        "An update_rule activity can only be created by PATCHing the rule"
    }, 500)
