import argparse
from db_functions import DATABASE, insert_into_db
from constants import USER_ID
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def create_roles(organization_id):
    pic_record = {
        "name": "PIC",
        "organization_id": organization_id,
        "created_by": USER_ID,
        "permissions": [
            {
                "object": "organizations",
                "methods": [
                    "GET",
                    "PATCH"
                ]
            },
            {
                "object": "users",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "equipment",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "uploads",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "clients",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "taxonomies",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "taxonomy_options",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "inventories",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "products",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH"
                ]
            },
            {
                "object": "roles",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "rooms",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "rules",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "labels",
                "methods": [
                    "GET"
                ]
            },
            {
                "object": "activities",
                "methods": [
                    "GET",
                    "POST"
                ]
            },
            {
                "object": "skus",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "capas",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "capa_links",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "object": "capa_actions",
                "methods": [
                    "GET",
                    "POST",
                    "PATCH",
                    "DELETE"
                ]
            },
            {
                "action": "admin_adjustment"
            },
            {
                "action": "approve_received_inventory"
            },
            {
                "action": "create_sample"
            },
            {
                "action": "batch_record_harvest_weight"
            },
            {
                "action": "batch_record_dry_weight"
            },
            {
                "action": "batch_record_final_yield"
            },
            {
                "action": "batch_visual_inspection"
            },
            {
                "action": "create_activity_log"
            },
            {
                "action": "create_batch"
            },
            {
                "action": "create_lot"
            },
            {
                "action": "create_mother"
            },
            {
                "action": "destroy_material"
            },
            {
                "action": "metrics_collect_branch_count"
            },
            {
                "action": "metrics_collect_bud_density"
            },
            {
                "action": "metrics_collect_bud_size"
            },
            {
                "action": "metrics_collect_bud_moisture"
            },
            {
                "action": "metrics_collect_height"
            },
            {
                "action": "metrics_collect_internodal_space"
            },
            {
                "action": "metrics_collect_trichome_color"
            },
            {
                "action": "metrics_record_deficiency"
            },
            {
                "action": "org_update_theme"
            },
            {
                "action": "plants_add_pesticide"
            },
            {
                "action": "plants_defoliate"
            },
            {
                "action": "plants_flush"
            },
            {
                "action": "plants_pinch"
            },
            {
                "action": "plants_prune"
            },
            {
                "action": "propagate_cuttings"
            },
            {
                "action": "queue_for_destruction"
            },
            {
                "action": "receive_inventory"
            },
            {
                "action": "sample_sent_to_lab"
            },
            {
                "action": "sample_lab_result_received"
            },
            {
                "action": "sample_update_test_result"
            },
            {
                "action": "batch_qa_review"
            },
            {
                "action": "transfer_inventory"
            },
            {
                "action": "unset_room"
            },
            {
                "action": "update_room"
            },
            {
                "action": "update_rule"
            },
            {
                "action": "update_stage"
            },
            {
                "action": "create_lot"
            },
            {
                "action": "create_sku"
            },
            {
                "action": "create_lot_item"
            },
            {
                "action": "sku_update_status"
            },
            {
                "action": "create_capa"
            },
            {
                "action": "capa_action_cancel"
            },
            {
                "action": "capa_action_close"
            },
            {
                "action": "capa_action_update"
            },
            {
                "action": "capa_add_action"
            },
            {
                "action": "capa_add_link"
            },
            {
                "action": "capa_add_note"
            },
            {
                "action": "capa_approve_action_plan"
            },
            {
                "action": "capa_close"
            },
            {
                "action": "capa_dismiss"
            },
            {
                "action": "capa_initiate"
            },
            {
                "action": "capa_link_disable"
            },
            {
                "action": "capa_update_description"
            }
        ]
    }

    insert_into_db("roles", pic_record)


def main():
    """Main function that creates roles for a given organization.
    """

    parser = argparse.ArgumentParser(
        description='Create roles in the database'
    )

    parser.add_argument(
        '--organization_id',
        type=str,
        help='Organization id to create role for',
        required=True
    )

    args = parser.parse_args()

    create_roles(args.organization_id)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
