# Import libraries from parent folder
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE, insert_into_db
 
from constants import USER_ID


def create_rules():
    """Creates rules for every organization."""
    transfer_inventory_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Transfer inventory",
        "activity": "transfer_inventory",
        "conditions": [{
            "match_fields": [
                {
                    "field": "variety",
                    "match": "variety"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "from_inventory_id"
        },{
            "match_fields": [
                {
                    "field": "variety",
                    "match": "variety"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "from_inventory_id"
        },{
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        }]
    }

    destroy_material_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Destroy material",
        "activity": "destroy_material",
        "conditions": [{
            "field": "witness_1",
            "regex": "[\\w\\-,+@.\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "witness_1_role",
            "regex": "[\\w\\-,.\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "witness_2",
            "regex": "[\\w\\-+@,.\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "witness_2_role",
            "regex": "[\\w\\-,.\\s]+",
            "condition_type": "data_validation"
        }]
    }

    batch_record_harvest_weight_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Record bud weight",
        "activity": "batch_record_harvest_weight",
        "conditions": [{
            "field": "to_qty_unit",
            "regex": "g-wet",
            "condition_type": "data_validation"
        },{
            "field": "from_qty_unit",
            "regex": "plants",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "field": "from_qty",
            "regex": "\\d+",
            "condition_type": "data_validation"
        },{
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "to_inventory_id"
        }]
    }

    batch_record_dry_weight_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Record batch dry weight",
        "activity": "batch_record_dry_weight",
        "conditions": [{
            "field": "to_qty_unit",
            "regex": "g-dry",
            "condition_type": "data_validation"
        },{
            "field": "from_qty_unit",
            "regex": "g-wet",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "field": "from_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "operator": "=",
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "to_inventory_id"
        }]
    }

    complete_oil_extraction_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Complete oil extraction",
        "activity": "complete_oil_extraction",
        "conditions": [{
            "field": "to_qty_unit",
            "regex": "ml",
            "condition_type": "data_validation"
        },{
            "field": "from_qty_unit",
            "regex": "g-wet",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "field": "from_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "operator": "=",
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "to_inventory_id"
        }]
    }

    sample_sent_to_lab_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Sample sent to lab",
        "activity": "sample_sent_to_lab",
        "conditions": [{
            "field": "from_qty_unit",
            "regex": "(g-dry|g-oil)",
            "condition_type": "data_validation"
        },{
            "field": "from_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        },{
            "field": "sample_sent_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "lab_name",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "sample"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "from_inventory_id"
        }]
    }

    sample_lab_result_received_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Sample lab result received",
        "activity": "sample_lab_result_received",
        "conditions": [{
            "field": "received_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "sample"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "from_inventory_id"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "related_inventory_id"
        }]
    }

    queue_for_destruction_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Queue for destruction",
        "activity": "queue_for_destruction",
        "conditions": [{
            "field": "from_qty",
            "conditions": [
                {
                    "qty_unit": "from_qty_unit",
                    "qty_value": "from_qty",
                    "inventory_id": "from_inventory_id",
                    "condition_type": "inventory_count"
                }
            ],
            "condition_type": "conditional_has_field"
        },{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        },{
            "field": "type_of_waste",
            "match": "name",
            "taxonomy_name": "waste_types",
            "condition_type": "taxonomy_validation"
        },{
            "field": "reason_for_destruction",
            "match": "name",
            "taxonomy_name": "destruction_reasons",
            "condition_type": "taxonomy_validation"
        },{
            "field": "destroyed_qty",
            "regex": "\\d+\\.?\\d*",
            "condition_type": "data_validation"
        },{
            "field": "destroyed_qty_unit",
            "regex": "g",
            "condition_type": "data_validation"
        },{
            "field": "weighed_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "checked_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "collected_from",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    complete_destruction_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Complete destruction",
        "activity": "complete_destruction",
        "conditions": [{
            "match_fields": [
                {
                    "field": "destroyed_qty_unit",
                    "match": "destroyed_qty_unit"
                },
                {
                    "match": "name",
                    "regex": "queue_for_destruction"
                }
            ],
            "condition_type": "activity_match",
            "activity_id_field": "queue_destruction_activity_id"
        }]
    }

    receive_inventory_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Receive inventory",
        "activity": "receive_inventory",
        "conditions": [{
            "field": "vendor_name",
            "regex": "[\\w\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "net_weight_received",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "number_of_pieces",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "weighed_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "checked_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "to_qty_unit",
            "regex": "(g-dry|g-wet|ml|seeds|plants)",
            "condition_type": "data_validation"
        },{
            "field": "vendor_lot_number",
            "regex": "[\\w\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "intended_use",
            "regex": "[\\w\\s]+",
            "condition_type": "data_validation"
        },{
            "field": "quarantined",
            "regex": "true",
            "condition_type": "data_validation"
        },{
            "field": "to_stage",
            "match": "name",
            "taxonomy_name": "stages",
            "condition_type": "taxonomy_validation"
        },{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        }]
    }

    create_mother_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create mother",
        "activity": "create_mother",
        "conditions": [{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        }]
    }

    create_batch_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create batch",
        "activity": "create_batch",
        "conditions": [{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        }]
    }

    propagate_cuttings_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Propagate cuttings",
        "activity": "propagate_cuttings",
        "conditions": [{
            "field": "to_qty_unit",
            "regex": "plants",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "[1-9]\\d*",
            "condition_type": "data_validation"
        },{
            "match_fields": [
                {
                    "match": "variety",
                    "comparison": "="
                }
            ],
            "condition_type": "inventory_compare",
            "first_inventory_id_field": "to_inventory_id",
            "second_inventory_id_field": "from_inventory_id"
        },{
            "qty_unit": "to_qty_unit",
            "qty_value": "source_count",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        }]
    }

    update_room_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Update Room",
        "activity": "update_room",
        "conditions": [{
            "field": "to_room",
            "condition_type": "room_validation"
        }]
    }

    approve_received_inventory_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Approve Received Inventory",
        "activity": "approve_received_inventory",
        "conditions": []
    }

    create_activity_log_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create activity log",
        "activity": "create_activity_log",
        "conditions": [],
        "detail": ""
    }

    update_stage_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Update stage",
        "activity": "update_stage",
        "conditions": []
    }

    org_update_theme_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Update Theme",
        "activity": "org_update_theme",
        "conditions": []
    }

    plants_prune_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Plants Prune",
        "activity": "plants_prune",
        "conditions": [{
            "field": "part_pruned",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "pruned_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    plants_flush_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Plants flush",
        "activity": "plants_flush",
        "conditions": [{
            "field": "flushed_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    plants_add_pesticide_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Plants add pesticide",
        "activity": "plants_add_pesticide",
        "conditions": [{
            "field": "pesticide_name",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "person_in_charge",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_branch_count_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect branch count",
        "activity": "metrics_collect_branch_count",
        "conditions": [{
            "field": "branch_count",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_bud_density_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect bud density",
        "activity": "metrics_collect_bud_density",
        "conditions": [{
            "field": "density",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_bud_size_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect bud size",
        "activity": "metrics_collect_bud_size",
        "conditions": [{
            "field": "diameter",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_height_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect height",
        "activity": "metrics_collect_height",
        "conditions": [{
            "field": "height",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_trichome_color_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect trichrome color",
        "activity": "metrics_collect_trichome_color",
        "conditions": [{
            "field": "trichome_color",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_internodal_space_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect internodal space",
        "activity": "metrics_collect_internodal_space",
        "conditions": [{
            "field": "internodal_space",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_record_deficiency_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics record deficiency",
        "activity": "metrics_record_deficiency",
        "conditions": [{
            "field": "plants_affected",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "recorded_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "deficiency",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    plants_pinch_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Plants pinch",
        "activity": "plants_pinch",
        "conditions": [{
            "field": "pinching_method",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "pinched_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    plants_defoliate_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Plants defoliate",
        "activity": "plants_defoliate",
        "conditions": [{
            "field": "defoliated_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    metrics_collect_bud_moisture_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Metrics collect bud moisture",
        "activity": "metrics_collect_bud_moisture",
        "conditions": [{
            "field": "moisture",
            "regex": "([1-9]\\d*\\.\\d*|0?\\.\\d*[1-9]\\d*|[1-9]\\d*)",
            "condition_type": "data_validation"
        },{
            "field": "collected_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    batch_visual_inspection_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Visual Inspection",
        "activity": "batch_visual_inspection",
        "conditions": []
    }

    create_sample_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create Sample",
        "activity": "create_sample",
        "conditions": [{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        },{
            "field": "sampled_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "field": "approved_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        }]
    }

    unset_room_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Unset Room",
        "activity": "unset_room",
        "conditions": []
    }

    batch_record_final_yield_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Batch Record Final Yield",
        "activity": "batch_record_final_yield",
        "conditions": [{
            "field": "to_qty_unit",
            "regex": "g-dry",
            "condition_type": "data_validation"
        },{
            "field": "from_qty_unit",
            "regex": "g-dry",
            "condition_type": "data_validation"
        },{
            "field": "to_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "field": "from_qty",
            "regex": "([0-9]*[.])?[0-9]+",
            "condition_type": "data_validation"
        },{
            "qty_unit": "from_qty_unit",
            "qty_value": "from_qty",
            "inventory_id": "from_inventory_id",
            "condition_type": "inventory_count"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "to_inventory_id"
        }]
    }

    create_lot_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create Lot",
        "activity": "create_lot",
        "conditions": [{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        }]
    }

    create_sku_weight_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create SKU",
        "activity": "create_sku_weight",
        "conditions": []
    }

    create_lot_item_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create Lot Item",
        "activity": "create_lot_item",
        "conditions": [{
            "field": "variety",
            "match": "name",
            "taxonomy_name": "varieties",
            "condition_type": "taxonomy_validation"
        }]
    }

    sample_update_test_result_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Sample Update Test Result",
        "activity": "sample_update_test_result",
        "conditions": [{
            "field": "updated_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "sample"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "inventory_id"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "related_inventory_id"
        }]
    }

    batch_qa_review_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Batch QA review",
        "activity": "batch_qa_review",
        "conditions": [{
            "field": "reviewed_by",
            "regex": "(?!\\s*$).+",
            "condition_type": "data_validation"
        },{
            "match_fields": [
                {
                    "match": "type",
                    "regex": "batch"
                }
            ],
            "condition_type": "inventory_match",
            "inventory_id_field": "inventory_id"
        }]
    }

    sku_update_status_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "SKU Update Status",
        "activity": "sku_update_status",
        "conditions": []
    }

    create_crm_account_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Create CRM Account",
        "activity": "create_crm_account",
        "conditions": []
    }

    crm_account_update_status_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "CRM Account Update Status",
        "activity": "crm_account_update_status",
        "conditions": []
    }

    batch_plan_update_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Update batch plan",
        "activity": "batch_plan_update",
        "conditions": []
    }

    batch_record_oil_weight_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "Batch Record Oil Weight",
        "activity": "batch_record_oil_weight",
        "conditions": []
    }

    crm_account_update_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "CRM Account Update",
        "activity": "crm_account_update",
        "conditions": []
    }

    crm_account_attach_document_rule = {
        "organization_id": 0,
        "created_by": USER_ID,
        "name": "CRM Account Attach Document",
        "activity": "crm_account_attach_document",
        "conditions": []
    }

    rules = [
        transfer_inventory_rule,
        destroy_material_rule,
        batch_record_harvest_weight_rule,
        batch_record_dry_weight_rule,
        complete_oil_extraction_rule,
        sample_sent_to_lab_rule,
        sample_lab_result_received_rule,
        queue_for_destruction_rule,
        complete_destruction_rule,
        receive_inventory_rule,
        create_mother_rule,
        create_batch_rule,
        propagate_cuttings_rule,
        update_room_rule,
        approve_received_inventory_rule,
        create_activity_log_rule,
        update_stage_rule,
        org_update_theme_rule,
        plants_prune_rule,
        plants_flush_rule,
        plants_add_pesticide_rule,
        metrics_collect_branch_count_rule,
        metrics_collect_bud_density_rule,
        metrics_collect_bud_size_rule,
        metrics_collect_height_rule,
        metrics_collect_trichome_color_rule,
        metrics_collect_internodal_space_rule,
        metrics_record_deficiency_rule,
        plants_pinch_rule,
        plants_defoliate_rule,
        metrics_collect_bud_moisture_rule,
        batch_visual_inspection_rule,
        create_sample_rule,
        unset_room_rule,
        batch_record_final_yield_rule,
        create_lot_rule,
        create_sku_weight_rule,
        create_lot_item_rule,
        sample_update_test_result_rule,
        batch_qa_review_rule,
        sku_update_status_rule,
        create_crm_account_rule,
        crm_account_update_status_rule,
        batch_plan_update_rule,
        batch_record_oil_weight_rule,
        crm_account_update_rule,
        crm_account_attach_document_rule
    ]

    for rule in rules:
        insert_into_db("rules", rule)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    create_rules()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
