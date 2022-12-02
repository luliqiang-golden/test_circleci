"""Apply a comparison operator to two fields in an activity"""
import operator

from class_errors import EngineError


def validate(condition, args, **kwargs):
    """
    Compare two fields of an activity
    {
        "condition_type": "compare_fields",
        "left_field": "witness_1", # the key of the args that holds the value on the left side of the operator
        "right_field": "witness_2", # the key of the args that holds the value on the right side of the operator
        "operator": "!=" # a comparison operator.
    }
    """

    required_condition_args = [
        'condition_type',
        'left_field',
        'right_field',
        'operator',
    ]

    if not all(condition_arg in condition
               for condition_arg in required_condition_args):
        raise EngineError({
            "error":
            "compare_fields_condition_error",
            "description":
            "Missing a required field for compare_fields conditions"
        }, 403)

    if condition['condition_type'] != "compare_fields":
        raise EngineError({
            "error":
            "compare_fields_condition_error",
            "description":
            'Condition sent to compare_fields handler, but is not an compare_fields condition'
        }, 500)

    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq,
        '!=': operator.ne
    }

    if condition['operator'] not in ops.keys():
        raise EngineError({
            "error":
            "compare_fields_operator_error",
            "description":
            "Operator provided ({}) is not valid".format(
                condition['operator'])
        }, 403)

    if condition['left_field'] not in args:
        raise EngineError({
            "error":
            "compare_fields_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['left_field'])
        }, 403)

    if condition['right_field'] not in args:
        raise EngineError({
            "error":
            "compare_fields_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['right_field'])
        }, 403)

    if not ops[condition['operator']](
            args[condition['left_field']],
            args[condition['right_field']],
    ):
        raise EngineError({
            "error":
            "compare_fields_error",
            "description":
            "Comparison {0} {1} {2} is false".format(
                args[condition['left_field']], condition['operator'],
                args[condition['right_field']])
        }, 403)
