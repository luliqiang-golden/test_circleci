"""Validate that a given inventory item has sufficient inventory of the required units"""
import operator

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    """
    Compare field to values from taxonomy
    {
        "condition_type": "inventory_count",
        "inventory_id": "from_inventory_id", # the key of the args that holds the id of the inventory item we are checking
        "qty_unit": "from_qty_unit", # the key of the args that holds the quantity unit we will be checking
        "qty_value": "from_qty", # the key of the args that holds the actual quantity we need to check against
        "operator": "<=" # an optional comparison operator. Current inventory qty on the left, qty_value on the right (current_qty >= qty_value)
        # default operator is >=
    }
    """
    if condition['condition_type'] != "inventory_count":
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            'Condition sent to inventory_count handler, but is not an inventory_count condition'
        }, 500)

    if 'inventory_id' not in condition:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "'inventory_id' is a required field for inventory_count conditions"
        }, 403)

    if 'qty_unit' not in condition:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "'qty_unit' is a required field for inventory_count conditions"
        }, 403)

    if 'qty_value' not in condition:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "'qty_value' is a required field for inventory_count conditions"
        }, 403)

    if 'operator' not in condition:
        condition['operator'] = ">="

    ops = {
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=': operator.eq
    }

    if condition['operator'] not in ops.keys():
        raise EngineError({
            "error":
            "inventory_count_operator_error",
            "description":
            "Operator provided ({}) is not valid".format(
                condition['operator'])
        }, 403)

    if condition['inventory_id'] not in args:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['inventory_id'])
        }, 403)

    if condition['qty_unit'] not in args:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['qty_unit'])
        }, 403)

    if condition['qty_value'] not in args:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['qty_value'])
        }, 403)

    try:
        qty_value = int(args[condition['qty_value']])
    except ValueError:
        try:
            qty_value = float(args[condition['qty_value']])
        except ValueError:
            raise EngineError({
                "error":
                "invalid_qty_value",
                "description":
                "Qty value must be a number, but {} was supplied".format(
                    args[condition['qty_value']])
            }, 400)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "inventory_count_condition_error",
            "description":
            "'organization_id' is a required field for inventory_count conditions"
        }, 403)

    inventory_item = db_functions.select_resource_from_db(
        'inventories', args[condition['inventory_id']],
        args['organization_id'])

    if not inventory_item:
        raise EngineError({
            "error":
            "inventory_count_error",
            "description":
            "Can't compare against item {0} because it doesn't exist".format(
                args[condition['inventory_id']])
        }, 403)

    if (not inventory_item['stats']) or (
            args[condition['qty_unit']] not in inventory_item['stats']) or (
                not inventory_item['stats'][args[condition['qty_unit']]]):
        raise EngineError({
            "error":
            "inventory_count_error",
            "description":
            "Wrong inventory amount: requires {0} {1} {2}, item has {3}".
            format(condition['operator'], args[condition['qty_value']],
                   args[condition['qty_unit']], 0)
        }, 403)

    total = inventory_item['stats'][args[condition['qty_unit']]]

    if not ops[condition['operator']](total, qty_value):
        raise EngineError({
            "error":
            "inventory_count_error",
            "description":
            "Wrong inventory amount: requires {0} {1} {2}, item has {3}".
            format(condition['operator'], args[condition['qty_value']],
                   args[condition['qty_unit']], total)
        }, 403)
