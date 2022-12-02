"""Provides all the available validators"""
import importlib
from class_errors import ClientBadRequest

VALIDATORS = {}
VALIDATOR_NAMES = [
    'inventory_count',
    'inventory_match',
    'data_validation',
    'taxonomy_validation',
    'upload_validation',
    'conditional_has_field',
    'activity_match',
    'inventory_compare',
    'compare_fields',
    'stage_validation',
    'room_validation',
    'inventory_condition',
]

for validator_name in VALIDATOR_NAMES:
    full_validator_name = "rule_validators.{}".format(validator_name)
    try:
        VALIDATORS[validator_name] = importlib.import_module(
            full_validator_name)
    except ImportError:
        raise ClientBadRequest({
            "code":
            "invalid_validator",
            "message":
            "A validator could not be loaded ({})".format(validator_name)
        }, 500)
