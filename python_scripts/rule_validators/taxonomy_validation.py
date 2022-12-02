"""Validate that data is consistent with applicable taxonomies"""

from class_errors import EngineError
import db_functions


def validate(condition, args, **kwargs):
    """
    Compare field to values from taxonomy
    Requires:
    * taxonomy_name: the standard name of the taxonomy
    * field: the args field to validate
    * match: the key of the taxonomy option to validate (ie - name, id, custom_name)
    Example: to check that the value of the "brand" meta-value is a valid option name in the "brand-names" taxonomy:
    {
        "condition_type": "taxonomy_validation",
        "field": "brand",
        "taxonomy_name": "brand-names",
        "match": "name"
    }
    """
    if condition['condition_type'] != "taxonomy_validation":
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            'Condition sent to taxonomy_validation handler, but is not a taxonomy_validation condition'
        }, 500)

    if 'taxonomy_name' not in condition:
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            "'taxonomy_name' is a required field for taxonomy_validation conditions"
        }, 403)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            "'field' is a required field for taxonomy_validation conditions"
        }, 403)

    if 'match' not in condition:
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            "'match' is a required field for taxonomy_validation conditions"
        }, 403)

    if condition['field'] not in args:
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['field'])
        }, 403)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "taxonomy_validation_condition_error",
            "description":
            "'organization_id' is a required field for taxonomy_validation conditions"
        }, 403)

    taxonomy_db_collection = db_functions.select_collection_from_db(
        'taxonomies',
        args['organization_id'],
        meta=False,
        filters=[('name', '=', condition['taxonomy_name'])])

    if taxonomy_db_collection[1]['count'] != 1:
        raise EngineError({
            "error":
            "taxonomy_validation_taxonomy_error",
            "description":
            "There are {0} results for taxonomy named '{1}'. There should be exactly one".
            format(taxonomy_db_collection[1]['count'],
                   condition['taxonomy_name'])
        }, 403)

    taxonomy_id = taxonomy_db_collection[0][0]['id']

    taxonomy_options = db_functions.select_collection_from_db(
        'taxonomy_options',
        args['organization_id'],
        filters=[('taxonomy_id', '=', taxonomy_id),
                 ('name', '=', args[condition['field']])])

    taxonomy_options = taxonomy_options[0]

    for option in taxonomy_options:
        if (condition['match'] in option
                and option[condition['match']] == args[condition['field']]):
            return

    raise EngineError({
        "error":
        "taxonomy_validation_option_error",
        "description":
        "'{0}' is not a valid option in the '{1}' taxonomy".format(
            args[condition['field']], condition['taxonomy_name'])
    }, 403)
