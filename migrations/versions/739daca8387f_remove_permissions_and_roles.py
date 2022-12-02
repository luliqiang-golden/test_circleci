"""remove permissions and roles

Revision ID: 739daca8387f
Revises: 1668ea6d6344
Create Date: 2022-02-16 12:16:54.513983

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '739daca8387f'
down_revision = 'e6ae7f9c4554'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
            ALTER TABLE public.users 
            DROP COLUMN IF EXISTS role_id,
            DROP CONSTRAINT IF EXISTS users_role;

            DROP TABLE IF EXISTS public.roles;
        """
    )


def downgrade():
    connection = op.get_bind()
    permissions = [{"object": "activities", "methods": ["GET", "POST", "PATCH"]}, {"object": "alembic_version", "methods": ["GET", "POST", "PATCH"]}, {"object": "audit", "methods": ["GET", "POST", "PATCH"]}, {"object": "audit_detail", "methods": ["GET", "POST", "PATCH"]}, {"object": "capa_actions", "methods": ["GET", "POST", "PATCH"]}, {"object": "capa_links", "methods": ["GET", "POST", "PATCH"]}, {"object": "capas", "methods": ["GET", "POST", "PATCH"]}, {"object": "consumable_classes", "methods": ["GET", "POST", "PATCH"]}, {"object": "consumable_lots", "methods": ["GET", "POST", "PATCH"]}, {"object": "crm_accounts", "methods": ["GET", "POST", "PATCH"]}, {"object": "currencies", "methods": ["GET", "POST", "PATCH"]}, {"object": "departments", "methods": ["GET", "POST", "PATCH"]}, {"object": "deviation_reports", "methods": ["GET", "POST", "PATCH"]}, {"object": "deviation_reports_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "equipment", "methods": ["GET", "POST", "PATCH"]}, {"object": "health_canada_report", "methods": ["GET", "POST", "PATCH"]}, {"object": "inventories", "methods": ["GET", "POST", "PATCH"]}, {"object": "invoices", "methods": ["GET", "POST", "PATCH"]}, {"object": "order_items", "methods": ["GET", "POST", "PATCH"]}, {"object": "orders", "methods": ["GET", "POST", "PATCH"]}, {"object": "organizations", "methods": ["GET", "POST", "PATCH"]}, {"object": "recalls", "methods": ["GET", "POST", "PATCH"]}, {"object": "roles", "methods": ["GET", "POST", "PATCH"]}, {"object": "rooms", "methods": ["GET", "POST", "PATCH"]}, {"object": "rules", "methods": ["GET", "POST", "PATCH"]}, {"object": "sensors_data", "methods": ["GET", "POST", "PATCH"]}, {"object": "shipments", "methods": ["GET", "POST", "PATCH"]}, {"object": "signatures", "methods": ["GET", "POST", "PATCH"]}, {"object": "skus", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "sops", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_versions", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_versions_departments", "methods": ["GET", "POST", "PATCH"]}, {"object": "srfax", "methods": ["GET", "POST", "PATCH"]}, {"object": "stats_taxonomies", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxes", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxonomies", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxonomy_options", "methods": ["GET", "POST", "PATCH"]}, {"object": "transaction_allocations", "methods": ["GET", "POST", "PATCH"]}, {"object": "transactions", "methods": ["GET", "POST", "PATCH"]}, {"object": "uploads", "methods": ["GET", "POST", "PATCH"]}, {"object": "users", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_deviation_reports_with_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_mother_with_mother_batch_id", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_logs", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_notifications", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sops", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_versions", "methods": ["GET", "POST", "PATCH"]}, {"object": "webhook_subscriptions", "methods": ["GET", "POST", "PATCH"]}, {"action": "admin_adjustment"}, {"action": "approve_received_inventory"}, {"action": "batch_record_bud_harvest_weight"}, {"action": "complete_destruction"}, {"action": "batch_record_dry_weight"}, {"action": "split_batch"}, {"action": "batch_record_cured_weight"}, {"action": "batch_record_final_yield"}, {"action": "complete_oil_extraction"}, {"action": "create_activity_log"}, {"action": "create_batch"}, {"action": "create_mother_batch"}, {"action": "transfer_mother_plants_to_mother_batch"}, {"action": "transfer_batch_plant_to_mother_batch"}, {"action": "create_mother"}, {"action": "update_mother_status"}, {"action": "create_rule"}, {"action": "destroy_material"}, {"action": "germinate_seeds"}, {"action": "metrics_collect_branch_count"}, {"action": "metrics_collect_bud_density"}, {"action": "metrics_collect_bud_moisture"}, {"action": "metrics_collect_bud_diameter"}, {"action": "metrics_collect_height"}, {"action": "metrics_collect_internodal_space"}, {"action": "metrics_collect_trichome_color"}, {"action": "metrics_record_deficiency"}, {"action": "org_update_license_id"}, {"action": "org_update_theme"}, {"action": "org_update_date_format"}, {"action": "org_update_date_time_format"}, {"action": "org_update_metric_system"}, {"action": "org_update_temperature_scale"}, {"action": "org_update_currency"}, {"action": "org_update_upload_formats"}, {"action": "org_update_enable_signature"}, {"action": "org_update_use_batch_name_column_as_link"}, {"action": "plants_add_pesticide"}, {"action": "plants_add_fertilizer"}, {"action": "plants_add_ipm"}, {"action": "plants_defoliate"}, {"action": "plants_flush"}, {"action": "plants_prune"}, {"action": "propagate_cuttings"}, {"action": "queue_for_destruction"}, {"action": "receive_inventory"}, {"action": "transfer_inventory"}, {"action": "unset_room"}, {"action": "update_room"}, {"action": "update_rule"}, {"action": "update_stage"}, {"action": "update_inventory_name"}, {"action": "sample_sent_to_lab"}, {"action": "batch_create_sample"}, {"action": "batch_visual_inspection"}, {"action": "create_sku"}, {"action": "sku_update_status"}, {"action": "sample_lab_result_received"}, {"action": "create_lot"}, {"action": "create_lot_item"}, {"action": "sample_update_test_result"}, {"action": "batch_qa_review"}, {"action": "create_crm_account"}, {"action": "crm_account_update_status"}, {"action": "crm_account_update"}, {"action": "crm_account_attach_document"}, {"action": "batch_plan_update"}, {"action": "batch_record_crude_oil_weight"}, {"action": "batch_record_distilled_oil_weight"}, {"action": "crm_account_create_note"}, {"action": "create_order"}, {"action": "create_external_order"}, {"action": "update_external_order"}, {"action": "order_add_item"}, {"action": "order_update_account"}, {"action": "order_cancel_item"}, {"action": "order_attach_document"}, {"action": "order_create_note"}, {"action": "order_update_status"}, {"action": "order_payment_status"}, {"action": "create_shipment"}, {"action": "order_item_add_shipment"}, {"action": "order_item_map_to_lot_item"}, {"action": "shipment_update_shipping_address"}, {"action": "shipment_update_tracking_number"}, {"action": "shipment_packaged"}, {"action": "shipment_update_shipped_date"}, {"action": "shipment_shipped"}, {"action": "shipment_delivered"}, {"action": "shipment_update_delivered_date"}, {"action": "create_capa"}, {"action": "capa_update_description"}, {"action": "capa_initiate"}, {"action": "capa_dismiss"}, {"action": "capa_close"}, {"action": "capa_add_note"}, {"action": "capa_add_link"}, {"action": "capa_link_disable"}, {"action": "capa_add_action"}, {"action": "capa_approve_action_plan"}, {"action": "capa_action_update"}, {"action": "capa_action_cancel"}, {"action": "capa_action_close"}, {"action": "receive_consumable_lot"}, {"action": "consumable_class_update_status"}, {"action": "create_consumable_class"}, {"action": "consumable_lot_use_items"}, {"action": "user_create"}, {"action": "user_update_enabled"}, {"action": "user_update_role"}, {"action": "consumable_lot_destroy_items"}, {"action": "consumable_lot_update_status"}, {"action": "record_transaction"}, {"action": "record_transaction_allocation"}, {"action": "create_recall"}, {"action": "recall_close"}, {"action": "recall_update_detail"}, {"action": "recall_active"}, {"action": "update_transaction_total_amount"}, {"action": "consumable_lot_return_items"}, {"action": "create_signature"}, {"action": "sop_assignment_delete"}, {"action": "sop_assignment_sign"}, {"action": "sop_version_update"}, {"action": "sop_assign_department"}, {"action": "sop_assign_user"}, {"action": "sop_uploaded_new_version"}, {"action": "department_create"}, {"action": "sop_set_status"}, {"action": "create_organization"}, {"action": "org_update_facility_details"}, {"action": "received_inventory_return"}, {"action": "salvage_batch"}, {"action": "lot_update_thc"}, {"action": "lot_update_cbd"}, {"action": "order_update"}, {"action": "order_item_update"}, {"action": "sku_update"}, {"action": "create_deviation_report"}, {"action": "deviation_report_create_assignment"}, {"action": "deviation_report_status_update"}, {"action": "deviation_report_assignment_status_update"}, {"action": "deviation_report_attach_document"}, {"action": "deviation_report_create_note"}, {"action": "merge_batch"}, {"action": "merge_lot"}, {"action": "create_sanitation_activity"}, {"action": "send_to_extraction"}, {"action": "batch_record_final_extracted_weight"}, {"action": "batch_add_additive"}, {"action": "external_order_update_status"}, {"action": "external_order_payment_status"}, {"action": "external_order_update_account"}, {"action": "external_order_create_note"}, {"action": "external_order_attach_document"}, {"action": "external_order_add_item"}, {"action": "external_order_item_update"}, {"action": "external_order_cancel_item"}, {"action": "external_order_item_map_to_lot_item"}, {"action": "external_order_item_add_shipment"}, {"action": "create_external_shipment"}, {"action": "external_shipment_packaged"}, {"action": "external_shipment_shipped"}, {"action": "external_shipment_delivered"}, {"action": "external_shipment_update_shipped_date"}, {"action": "external_shipment_update_delivered_date"}, {"action": "external_shipment_update_tracking_number"}, {"action": "external_shipment_update_shipping_address"}, {"action": "create_external_crm_account"}, {"action": "external_crm_account_update"}, {"action": "batch_add_links"}, {"action": "sop_add_link"}, {"action": "deviation_report_add_link"}, {"action": "create_invoice"}, {"action": "send_processor"}, {"action": "receive_processor"}, {"action": "org_update_fallback_tax_value"}, {"action": "update_fallback_tax"}]
    roles_table = op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String()),
        sa.Column('permissions', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('data', JSONB, default=sa.text("'{}'::jsonb")),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), default=sa.func.now())
    )
    op.add_column('users',
        sa.Column('role_id', sa.Integer, sa.ForeignKey('roles.id'))
    )

    orgs = connection.execute(''' SELECT * FROM organizations ''')

    for org in orgs:
        op.bulk_insert(
            roles_table,
            [
                {"organization_id": org['id'], "name": "Admin", "permissions": permissions, "data": {}, "created_by": 1, "timestamp": "now()"},
            ]
        )

    connection.execute(
        '''
            UPDATE users
            SET role_id = roles.id 
            FROM roles
            WHERE roles.organization_id = users.organization_id
        '''
    )

