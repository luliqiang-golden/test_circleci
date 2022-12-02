"""Validate that a given activity matches a pattern or incoming activity data"""
import re

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    """
    {
        "condition_type": "activity_match",
        "activity_id_field": "reference_activity_id",
        "match_fields": [ # fields on arg to match to property on existing activity
            {"field": "inventory_id", "match": "from_inventory_id"},
            {"regex":"passed", "match":"result"}
            ]
    }
    """
    if condition['condition_type'] != "activity_match":
        raise EngineError({
            "error":
            "activity_match_condition_error",
            "description":
            'Condition sent to activity_match handler, but is not an activity_match condition'
        }, 500)

    if 'activity_id_field' not in condition:
        raise EngineError({
            "error":
            "activity_match_condition_error",
            "description":
            "'activity_id_field' is a required field for activity_match conditions"
        }, 403)

    if condition['activity_id_field'] not in args:
        raise EngineError({
            "error":
            "activity_match_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['activity_id_field'])
        }, 403)

    if 'match_fields' not in condition:
        raise EngineError({
            "error":
            "activity_match_condition_error",
            "description":
            "'match_fields' is a required field for activity_match conditions"
        }, 403)

    if not isinstance(condition["match_fields"], list):
        raise EngineError({
            "error": "activity_match_condition_error",
            "description": "'match_fields' must be a list"
        }, 403)

    for match_field in condition["match_fields"]:
        if "field" not in match_field and "regex" not in match_field:
            raise EngineError({
                "error":
                "activity_match_condition_error",
                "description":
                "'field' or 'regex' is required in each activity_match match_fields object"
            }, 403)

        if "match" not in match_field:
            raise EngineError({
                "error":
                "activity_match_condition_error",
                "description":
                "'match' is required in each activity_match match_fields object"
            }, 403)

        if 'field' in match_field and match_field['field'] not in args:
            raise EngineError({
                "error":
                "activity_match_condition_error",
                "description":
                "Attempting to validate '{}' field but it was not found in the activity data".
                format(match_field['field'])
            }, 403)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "activity_match_condition_error",
            "description":
            "'organization_id' is a required field for activity_match conditions"
        }, 403)

    activity_item = db_functions.select_resource_from_db(
        "activities", args[condition["activity_id_field"]],
        args["organization_id"])

    if not activity_item:
        raise EngineError({
            "error":
            "activity_match_error",
            "description":
            "Activity #{} doesn't exist".format(
                args[condition["activity_id_field"]])
        }, 403)

    for match_field in condition["match_fields"]:
        if match_field["match"] not in activity_item:
            raise EngineError({
                "error":
                "activity_match_condition_error",
                "description":
                "Attempting to validate '{}' but it was not found in the reference activity".
                format(match_field['match'])
            }, 403)

        if 'field' in match_field:
            if activity_item[match_field["match"]] != args[match_field["field"]]:
                raise EngineError({
                    "error":
                    "activity_match_equality_error",
                    "description":
                    "Activity field {0} ({1}) does not match reference activity field {2} ({3})".
                    format(match_field['field'], args[match_field['field']],
                           match_field['match'],
                           activity_item[match_field['match']])
                }, 403)

        if 'regex' in match_field:
            try:
                val = re.fullmatch(match_field['regex'],
                                   activity_item[match_field['match']])
            except re.error:
                raise EngineError({
                    "error":
                    "activity_match_regex_error",
                    "description":
                    "Activity regex {} could not be compiled".format(
                        match_field['regex'])
                }, 403)

            if not val:
                raise EngineError({
                    "error":
                    "activity_match_regex_error",
                    "description":
                    "Activity regex ({0}) does not match reference activity field {1} ({2})".
                    format(match_field['regex'], match_field['match'],
                           activity_item[match_field['match']])
                }, 403)
