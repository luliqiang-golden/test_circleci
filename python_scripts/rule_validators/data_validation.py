"""Generic regex data validator"""

import re
from class_errors import EngineError


def validate(condition, args, **kwargs):
    """Compare field to regex"""
    if condition['condition_type'] != "data_validation":
        raise EngineError({
            "error":
            "data_validation_condition_error",
            "description":
            'Condition sent to data_validation handler, but is not a data_validation condition'
        }, 500)

    if 'regex' not in condition:
        raise EngineError({
            "error":
            "data_validation_condition_error",
            "description":
            "'regex' is a required field for data_validation conditions"
        }, 403)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "data_validation_condition_error",
            "description":
            "'field' is a required field for data_validation conditions"
        }, 403)

    if condition['field'] not in args:
        raise EngineError({
            "error":
            "data_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['field'])
        }, 403)

    regex = re.compile(condition['regex'])

    if regex.fullmatch(str(args[condition['field']])) is None:
        raise EngineError({
            "error":
            "data_validation_condition_error",
            "description":
            "'{0}' in '{1}' does not meet validation requirements".format(
                args[condition['field']], condition['field'])
        }, 403)
