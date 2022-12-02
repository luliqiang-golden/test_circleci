"""compare two inventory items"""

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    """
    Compare field to values from taxonomy
    {
        "condition_type": "inventory_compare",
        "first_inventory_id_field": "from_inventory_id",
        "second_inventory_id_field": "to_inventory_id",
        "match_fields": [ # fields on arg to match to property on inventory item
            {"match": "variety", "comparison": "="},
            ]
    }
    """
    if condition['condition_type'] != "inventory_compare":
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            'Condition sent to inventory_compare handler, but is not an inventory_compare condition'
        }, 500)

    if 'first_inventory_id_field' not in condition:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "'first_inventory_id_field' is a required field for inventory_compare conditions"
        }, 403)

    if 'second_inventory_id_field' not in condition:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "'second_inventory_id_field' is a required field for inventory_compare conditions"
        }, 403)

    if condition['first_inventory_id_field'] not in args:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['first_inventory_id_field'])
        }, 403)

    if condition['second_inventory_id_field'] not in args:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['second_inventory_id_field'])
        }, 403)

    if 'match_fields' not in condition:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "'match_fields' is a required field for inventory_compare conditions"
        }, 403)

    if not isinstance(condition["match_fields"], list):
        raise EngineError({
            "error": "inventory_compare_condition_error",
            "description": "'match_fields' must be a list"
        }, 403)

    for match_field in condition["match_fields"]:
        if "match" not in match_field or "comparison" not in match_field:
            raise EngineError({
                "error":
                "inventory_compare_condition_error",
                "description":
                "'match' and 'comparison' is required in each inventory_compare match_fields object"
            }, 403)

        if match_field["comparison"] != '=':
            raise EngineError({
                "error":
                "inventory_compare_condition_error",
                "description":
                "Comparisons other than '=' are not implemented."
            }, 403)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "inventory_compare_condition_error",
            "description":
            "'organization_id' is a required field for inventory_compare conditions"
        }, 403)

    first_inventory_item = db_functions.select_resource_from_db(
        "inventories", args[condition["first_inventory_id_field"]],
        args["organization_id"])

    if not first_inventory_item:
        raise EngineError({
            "error":
            "inventory_compare_error",
            "description":
            "Inventory item #{} doesn't exist".format(
                args[condition["first_inventory_id_field"]])
        }, 403)

    second_inventory_item = db_functions.select_resource_from_db(
        "inventories", args[condition["second_inventory_id_field"]],
        args["organization_id"])

    if not second_inventory_item:
        raise EngineError({
            "error":
            "inventory_compare_error",
            "description":
            "Inventory item #{} doesn't exist".format(
                args[condition["second_inventory_id_field"]])
        }, 403)

    for match_field in condition["match_fields"]:
        if match_field["match"] not in first_inventory_item or match_field["match"] not in second_inventory_item:
            raise EngineError({
                "error":
                "inventory_compare_condition_error",
                "description":
                "Attempting to validate '{}' but it was not found in the inventory item".
                format(match_field['match'])
            }, 403)

        if first_inventory_item[match_field["match"]] != second_inventory_item[match_field["match"]]:
            raise EngineError({
                "error":
                "inventory_compare_equality_error",
                "description":
                "Field '{0}' on inventory item {1} ({2}) does not match inventory item {3} ({4})".
                format(match_field['match'], first_inventory_item['id'],
                       first_inventory_item[match_field['match']],
                       second_inventory_item['id'],
                       second_inventory_item[match_field['match']])
            }, 403)
