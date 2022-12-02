"""Validate that a given inventory item is sent to correct destination"""
from rule_validators import validators
import re

from class_errors import EngineError
import db_functions


def validate(condition, args, current_user):
    """
    Validate inventory conditions
    {
        'condition_type': 'inventory_condition',
        'inventory_id': 'to_inventory_id',
        'match': 'type',
        'switches': [
            {
                'regex': 'mother',
                'conditions': [
                    {
                        'condition_type': 'inventory_count',
                        'inventory_id': 'to_inventory_id',
                        'qty_unit': 'to_qty_unit',
                        'qty_value': 'to_qty',
                        'operator': '='
                    },
                ]
            },
            {
                'regex': 'batch',
                'conditions': [
                    {
                        'condition_type': 'inventory_count',
                        'inventory_id': 'to_inventory_id',
                        'qty_unit': 'to_qty_unit',
                        'qty_value': 'to_qty',
                    },
                ]
            },
        ]
    }
    """
    if condition['condition_type'] != "inventory_condition":
        raise EngineError({
            "error":
            "inventory_condition_condition_error",
            "description":
            'Condition sent to inventory_condition handler, but is not an inventory_condition condition'
        }, 500)

    if 'inventory_id' not in condition:
        raise EngineError({
            "error":
            "inventory_condition_condition_error",
            "description":
            "'inventory_id' is a required field for inventory_condition conditions"
        }, 403)

    if condition['inventory_id'] not in args:
        raise EngineError({
            "error":
            "inventory_condition_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['inventory_id'])
        }, 403)

    if 'match' not in condition:
        raise EngineError({
            "error":
            "inventory_condition_condition_error",
            "description":
            "'match' is a required field for inventory_condition conditions"
        }, 403)

    if 'switches' not in condition:
        raise EngineError({
            "error":
            "inventory_condition_condition_error",
            "description":
            "'switches' is a required field for inventory_condition conditions"
        }, 403)

    if not isinstance(condition["switches"], list):
        raise EngineError({
            "error": "inventory_condition_condition_error",
            "description": "'switches' must be a list"
        }, 403)

    inventory_item = db_functions.select_resource_from_db(
        "inventories", args[condition["inventory_id"]],
        args['organization_id'])

    for switch in condition["switches"]:
        if "regex" not in switch or "conditions" not in switch:
            raise EngineError({
                "error":
                "inventory_condition_condition_error",
                "description":
                "'regex' and 'conditions' are required in each inventory_condition switches object"
            }, 403)

        if not isinstance(switch["conditions"], list):
            raise EngineError({
                "error": "inventory_condition_condition_error",
                "description": "'conditions' must be a list"
            }, 403)

        if not inventory_item:
            raise EngineError({
                "error":
                "inventory_condition_error",
                "description":
                "Inventory item #{} doesn't exist".format(
                    args[condition["inventory_id"]])
            }, 403)

        if re.fullmatch(switch['regex'], inventory_item[condition['match']]):
            for sub_condition in switch['conditions']:
                if 'condition_type' not in sub_condition:
                    raise EngineError({
                        "error": "rule_engine_error",
                        "description": 'Subcondition missing condition_type'
                    }, 403)

                try:
                    validators.VALIDATORS[sub_condition['condition_type']].validate(
                        sub_condition, args, current_user=current_user)
                except KeyError:
                    raise EngineError({
                        "error":
                        "rule_engine_error",
                        "description":
                        "No condition handlers for rule condition type {0} in subcondition".
                        format(sub_condition['condition_type'])
                    }, 403)
