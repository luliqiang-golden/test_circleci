"""Applies nested conditions if a field exists on the activity"""

from rule_validators import validators

from class_errors import EngineError


def validate(condition, args, current_user):
    """Apply nested conditions if a field exists on the activity"""

    if condition['condition_type'] != "conditional_has_field":
        raise EngineError({
            "error":
            "conditional_has_field_condition_error",
            "description":
            'Condition sent to conditional_has_field handler, but is not a conditional_has_field condition'
        }, 500)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "conditional_has_field_condition_error",
            "description":
            "'organization_id' is a required field for conditional_has_field conditions"
        }, 403)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "conditional_has_field_condition_error",
            "description":
            "'field' is a required field for conditional_has_field conditions"
        }, 403)

    if condition['field'] not in args:
        return  # only do this if the required field is actually in the activity

    if 'conditions' not in condition or not isinstance(condition['conditions'],
                                                       list):
        raise EngineError({
            "error":
            "conditional_has_field_condition_error",
            "description":
            "'conditions' is a required field for conditional_has_field conditions"
        }, 403)

    for sub_condition in condition['conditions']:

        if 'condition_type' not in sub_condition:
            raise EngineError({
                "error": "rule_engine_error",
                "message": 'Subcondition missing condition_type'
            }, 403)

        try:
            validators.VALIDATORS[sub_condition['condition_type']].validate(
                sub_condition, args, current_user=current_user)
        except KeyError:
            raise EngineError({
                "error":
                "rule_engine_error",
                "message":
                "No condition handlers for rule condition type {0} in subcondition".
                format(sub_condition['condition_type'])
            }, 403)
