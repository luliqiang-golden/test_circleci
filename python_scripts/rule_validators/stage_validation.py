"""Validate that data is consistent with applicable taxonomies"""

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    stages = []

    if condition['condition_type'] != "stage_validation":
        raise EngineError({
            "error":
            "stage_validation_condition_error",
            "description":
            'Condition sent to stage_validation handler, but is not a stage_validation condition'
        }, 500)

    if 'inventory_id_field' not in condition:
        raise EngineError({
            "error":
            "stage_validation_condition_error",
            "description":
            "'inventory_id' is a required field for stage_validation conditions"
        }, 403)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "stage_validation_condition_error",
            "description":
            "'field' is a required field for stage_validation conditions"
        }, 403)

    if condition['inventory_id_field'] not in args:
        raise EngineError({
            "error":
            "stage_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['inventory_id_field'])
        }, 403)

    if condition['field'] not in args:
        raise EngineError({
            "error":
            "stage_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['field'])
        }, 403)

    update_stage = args[condition['field']]

    selected_inventory = db_functions.select_resource_from_db(
        'inventories', args['inventory_id'], args['organization_id'])

    if selected_inventory is None:
        raise EngineError({
            "error":
            "stage_validation_error",
            "description":
            "Can't find item {0} because it doesn't exist".format(
                args[condition['inventory_id_field']])
        }, 403)

    taxonomy_collection = db_functions.select_collection_from_db(
        'taxonomies',
        args['organization_id'],
        meta=False,
        filters=[('name', '=', 'stages')])

    if taxonomy_collection[1]['count'] is 0:
        raise EngineError({
            "error": "stage_validation_error",
            "description": "Taxonomy does not exist"
        }, 403)

    stage_collection = db_functions.select_collection_from_db(
        'taxonomy_options',
        args['organization_id'],
        meta=False,
        filters=[('taxonomy_id', '=', taxonomy_collection[0]
                  [0]['id']), ('name', '=', update_stage)]
    )

    if stage_collection[1]['count'] is 0:
        raise EngineError(
            {
                "error": "stage_validation_error",
                "description": "Stages don't exist on taxonomy options"
            }, 403)

    try:
        current_stage = selected_inventory['attributes']["stage"]
    except KeyError:
        current_stage = None

    try:
        current_type = selected_inventory['type']
    except KeyError:
        current_type = None

    stages_object = stage_collection[0]

    for stage in stages_object:
        stages.append(stage['name'].lower())
    if update_stage.lower() not in stages:
        raise EngineError(
            {
                "error": "stage_validation_condition_error",
                "description": "{} stage does not exist".format(update_stage)
            }, 403)

    if current_stage is not None:
        for stage in stages_object:
            if stage['name'].lower() == update_stage.lower():
                if current_stage.lower() not in stage['allowed_previous_stages']:
                    stage_error(current_stage, update_stage)
    else:
        for stage in stages_object:
            if stage['name'].lower() == update_stage.lower():
                if '' in stage['allowed_previous_stages']:
                    pass
                else:
                    stage_error('New', update_stage)

    for stage in stages_object:
        if stage['name'].lower() == update_stage.lower():
            if current_type not in stage['allowed_inventory_types']:
                raise EngineError({
                    "error":
                    "stage_validation_condition_error",
                    "description":
                    "{} inventory type is not allowed in the requested stage, {}".
                    format(current_type, update_stage)
                }, 403)


def stage_error(current_stage, update_stage):
    raise EngineError({
        "error":
        "stage_validation_condition_error",
        "description":
        "{} stage does not exist as a previous stage on requested stage, {}".
        format(current_stage, update_stage)
    }, 403)
