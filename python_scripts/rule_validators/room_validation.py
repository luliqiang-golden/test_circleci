"""Validate that activity data is consistent with room data"""

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    """
    Compare field to values from a room
    Requires:
    * field: the args field to validate
    Example: to check that the value of the "to_room" activity key is a valid room name:
    {
        "condition_type": "room_validation",
        "field": "to_room"
    }
    """
    if condition['condition_type'] != "room_validation":
        raise EngineError({
            "error":
            "room_validation_condition_error",
            "description":
            'Condition sent to room_validation handler, but is not a room_validation condition'
        }, 500)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "room_validation_condition_error",
            "description":
            "'field' is a required field for room_validation conditions"
        }, 403)

    if condition['field'] not in args:
        raise EngineError({
            "error":
            "room_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['field'])
        }, 403)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "room_validation_condition_error",
            "description":
            "'organization_id' is a required field for room_validation conditions"
        }, 403)

    rooms = db_functions.select_collection_from_db(
        'rooms',
        args['organization_id'],
        filters=[('name', '=', args[condition['field']])])

    rooms = rooms[0]

    if rooms:
        # Return as long as we have one room with this name.
        # In the future, do checks to ensure room properties match patterns etc
        return

    raise EngineError({
        "error":
        "room_validation_option_error",
        "description":
        "'{0}' is not a valid room".format(args[condition['field']])
    }, 403)
