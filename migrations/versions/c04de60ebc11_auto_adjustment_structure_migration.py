"""auto adjustment structure migration

Revision ID: c04de60ebc11
Revises: 5b0fc11811ef
Create Date: 2022-06-08 14:44:21.344828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c04de60ebc11'
down_revision = '5b0fc11811ef'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
        """
        
        CREATE TABLE activities_mapping 
        (
            id bigserial NOT NULL,
            "timestamp" timestamptz NOT NULL DEFAULT now(),
            "name" varchar NOT NULL,
            friendly_name varchar NOT NULL,
            is_editable bool DEFAULT FALSE,
            is_deletable bool DEFAULT FALSE,
            is_visible bool DEFAULT TRUE,
            CONSTRAINT activities_mapping_name_key UNIQUE (name),
            CONSTRAINT activities_mapping_pkey PRIMARY KEY (id)
        );

        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_activity_log', 'Create Activity Log', TRUE, TRUE, TRUE);


        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_create_assignment','Deviation Report Create Assignment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_action_cancel','Capa Action Cancel',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_branch_count','Metrics Collect Branch Count',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_add_pesticide','Plants Add Pesticide',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_fallback_tax','Update Fallback Tax',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('crm_account_attach_document','Crm Account Attach Document',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_order','Create Order',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_update_shipping_address','Shipment Update Shipping Address',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_oil_weight','Batch Record Oil Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_upload_formats','Org Update Upload Formats',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('lab_result_received','Lab Result Received',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_internodal_space','Metrics Collect Internodal Space',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_bud_harvest_weight','Batch Record Bud Harvest Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_temperature_scale','Org Update Temperature Scale',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_use_batch_name_column_as_link','Org Update Use Batch Name Column As Link',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_status_update','Deviation Report Status Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_uploaded_new_version','Sop Uploaded New Version',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_metric_system','Org Update Metric System',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_assignment_delete','Sop Assignment Delete',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_license_id','Org Update License Id',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_batch_name','Update Batch Name',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_fallback_tax_value','Org Update Fallback Tax Value',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_mother_status','Update Mother Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sku_update_status','Sku Update Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_bud_density','Metrics Collect Bud Density',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('compost_material','Compost Material',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_assign_user','Sop Assign User',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('consumable_lot_destroy_items','Consumable Lot Destroy Items',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_collected','Shipment Collected',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_lot_item','Create Lot Item',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_plan_update','Batch Plan Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_batch','Create Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_add_fertilizer','Plants Add Fertilizer',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('receive_consumable_lot','Receive Consumable Lot',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('crm_account_update_status','Crm Account Update Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('germinate_seeds','Germinate Seeds',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_subscribe_entry','Create Subscribe Entry',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_update_description','Capa Update Description',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_upload','Update Upload',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_item_update','Order Item Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_deviation_report','Create Deviation Report',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_transaction_total_amount','Update Transaction Total Amount',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_room','Update Room',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_assignment_sign','Sop Assignment Sign',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_date_time_format','Org Update Date Time Format',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_rule','Update Rule',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('lot_update_cbd','Lot Update Cbd',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('transfer_batch_plant_to_mother_batch','Transfer Batch Plant To Mother Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('transfer_inventory','Transfer Inventory',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_cancel_item','Order Cancel Item',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_harvest_weight','Batch Record Harvest Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_create_note','Deviation Report Create Note',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_qa_review','Batch Qa Review',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_currency','Org Update Currency',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('complete_oil_extraction','Complete Oil Extraction',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_height','Metrics Collect Height',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_dry_weight','Batch Record Dry Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_facility_details','Org Update Facility Details',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_shipment','Create Shipment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('approve_received_inventory','Approve Received Inventory',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_payment_status','Order Payment Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('recall_close','Recall Close',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_close','Capa Close',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_equipment','Create Equipment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_pinch','Plants Pinch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('received_inventory_return','Received Inventory Return',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('receive_inventory','Receive Inventory',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_date_format','Org Update Date Format',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('recall_update_detail','Recall Update Detail',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_trichome_color','Metrics Collect Trichome Color',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('propagate_seeds','Propagate Seeds',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_attach_document','Order Attach Document',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('department_create','Department Create',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('recall_active','Recall Active',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_add_link','Capa Add Link',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_add_item','Order Add Item',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_crm_account_status','Update Crm Account Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_link_disable','Capa Link Disable',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_signature','Create Signature',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_prune','Plants Prune',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_external_order','Create External Order',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_closed','Shipment Closed',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sample_update_test_result','Sample Update Test Result',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update_type','Order Update Type',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_version_update','Sop Version Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_extracted_weight','Batch Record Extracted Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('merge_batch','Merge Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_sku','Create Sku',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('admin_adjustment','Admin Adjustment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('salvage_batch','Salvage Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_cured_weight','Batch Record Cured Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_final_extracted_weight','Batch Record Final Extracted Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update','Order Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_crude_oil_weight','Batch Record Crude Oil Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('consumable_lot_use_items','Consumable Lot Use Items',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update_description','Order Update Description',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_rule','Create Rule',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('queue_for_destruction','Queue For Destruction',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('inventory_adjustment','Inventory Adjustment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('crm_account_create_note','Crm Account Create Note',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_stage','Update Stage',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_equipment','Update Equipment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_bud_diameter','Metrics Collect Bud Diameter',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('user_update_enabled','User Update Enabled',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update_account','Order Update Account',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_record_deficiency','Metrics Record Deficiency',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_action_update','Capa Action Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_mother_batch','Create Mother Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_action_close','Capa Action Close',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_recall','Create Recall',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_flush','Plants Flush',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_add_link','Sop Add Link',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_crm_account','Update Crm Account',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_set_status','Sop Set Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('transfer_mother_plants_to_mother_batch','Transfer Mother Plants To Mother Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('split_batch','Split Batch',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('crm_account_update','Crm Account Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('consumable_class_update_status','Consumable Class Update Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_consumable_lot_activity_log','Create Consumable Lot Activity Log',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_attach_document','Deviation Report Attach Document',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('unset_room','Unset Room',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_packaged','Shipment Packaged',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_update_shipped_date','Shipment Update Shipped Date',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_update_tracking_number','Shipment Update Tracking Number',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('lab_sample_sent','Lab Sample Sent',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_final_yield','Batch Record Final Yield',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_item_add_shipment','Order Item Add Shipment',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('complete_destruction','Complete Destruction',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('send_processor','Send Processor',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('lot_update_thc','Lot Update Thc',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_add_action','Capa Add Action',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_shipped','Shipment Shipped',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_delivered','Shipment Delivered',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_create_note','Order Create Note',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_add_link','Deviation Report Add Link',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_item_map_to_lot_item','Order Item Map To Lot Item',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('user_update_role','User Update Role',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_dismiss','Capa Dismiss',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('consumable_lot_update_status','Consumable Lot Update Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_consumable_class','Create Consumable Class',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update_status','Order Update Status',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_add_note','Capa Add Note',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sop_assign_department','Sop Assign Department',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('merge_lot','Merge Lot',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sample_sent_to_lab','Sample Sent To Lab',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_lot','Create Lot',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_record_distilled_oil_weight','Batch Record Distilled Oil Weight',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('external_order_add_item','External Order Add Item',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_sample','Create Sample',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('order_update_due_date','Order Update Due Date',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_add_ipm','Plants Add Ipm',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('complete_drying','Complete Drying',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_bud_size','Metrics Collect Bud Size',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_theme','Org Update Theme',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('deviation_report_assignment_status_update','Deviation Report Assignment Status Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('propagate_cuttings','Propagate Cuttings',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('receive_processor','Receive Processor',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('record_transaction','Record Transaction',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_mother','Create Mother',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_sanitation_activity','Create Sanitation Activity',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sample_lab_result_received','Sample Lab Result Received',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_invoice','Create Invoice',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_capa','Create Capa',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_initiate','Capa Initiate',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('shipment_update_delivered_date','Shipment Update Delivered Date',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('record_transaction_allocation','Record Transaction Allocation',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('sku_update','Sku Update',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('harvest_plants','Harvest Plants',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('create_crm_account','Create Crm Account',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('destroy_material','Destroy Material',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('batch_visual_inspection','Batch Visual Inspection',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('consumable_lot_return_items','Consumable Lot Return Items',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('send_to_extraction','Send To Extraction',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('org_update_enable_signature','Org Update Enable Signature',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('update_inventory_name','Update Inventory Name',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('capa_approve_action_plan','Capa Approve Action Plan',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('metrics_collect_bud_moisture','Metrics Collect Bud Moisture',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('user_create','User Create',FALSE, FALSE, TRUE);
        INSERT INTO activities_mapping (name, friendly_name, is_editable, is_deletable, is_visible) VALUES ('plants_defoliate','Plants Defoliate',FALSE, FALSE, TRUE);


        ALTER TABLE activities
        ADD COLUMN edited bool DEFAULT FALSE,
        ADD COLUMN deleted bool DEFAULT FALSE;

        CREATE TYPE history_actions AS ENUM ('UPDATE', 'DELETE');

        CREATE TABLE public.activities_history (
        id bigserial NOT NULL,
        organization_id int4 NOT NULL,
        changed_by int4 NOT NULL,
        changed_at timestamptz NOT NULL DEFAULT now(),
        "name" varchar NOT NULL,
        "action" history_actions NOT NULL,
        old_data jsonb NOT NULL,
        new_data jsonb NULL,
        old_timestamp timestamptz NOT NULL,
        new_timestamp timestamptz NULL,
        reason_for_modification varchar,
        activity_id int8 NULL,
        CONSTRAINT activities_history_pkey PRIMARY KEY (id)
    );

        ALTER TABLE public.activities_history ADD CONSTRAINT activity_history_org FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE RESTRICT ON UPDATE RESTRICT;
        ALTER TABLE public.activities_history ADD CONSTRAINT activity_history_user FOREIGN KEY (changed_by) REFERENCES public.users(id) ON DELETE RESTRICT ON UPDATE RESTRICT;




        DROP FUNCTION f_activities_from_inventory(bigint);

        CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
        RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, edited bool, deleted bool, changed_at timestamp with time zone, changed_by integer, reason_for_modification text, inventory_id bigint)
        LANGUAGE plpgsql
        AS $function$
                begin
                return QUERY
                    select act.id,
                    act.organization_id,
                    act.created_by,
                    act."timestamp",
                    act."name",
                    act."data",
                    act."edited",
                    act."deleted",
                    MAX(ah.changed_at),
                    MAX(ah.changed_by),
                    MAX(ah.reason_for_modification),
                    CASE 
                        WHEN 
                        cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                        THEN 
                        cast(act.data->>'inventory_id' as bigint)
                        ELSE 
                        inv_id 
                    END
                    as inventory_id from activities as act
                    LEFT JOIN activities_history ah 
                    ON act.id = ah.activity_id
                    where
                        (concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
                        inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
                        inv_id = cast(act.data->>'to_inventory_id' as integer) or
                        inv_id = cast(act.data->>'inventory_id'as integer) or
                        inv_id = cast(act.data->>'related_inventory_id' as integer) or
                        inv_id = cast(act.data->>'linked_inventory_id' as integer))
                        GROUP BY act.id, act.organization_id, act.created_by, act."timestamp", act."name", act."data", act."edited", act."deleted";

                END;
                $function$
        ;
        
        GRANT ALL ON TABLE activities_mapping TO api_server;
        GRANT ALL ON TABLE activities_mapping TO dev_users;
        GRANT ALL ON TABLE activities_mapping TO postgres;
        
        
        
        GRANT ALL ON TABLE activities_history TO api_server;
        GRANT ALL ON TABLE activities_history TO dev_users;
        GRANT ALL ON TABLE activities_history TO postgres;
        
        
        """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        """ 
        
        
DROP TABLE activities_mapping;

DROP TABLE activities_history;

ALTER TABLE activities 
DROP COLUMN edited,
DROP COLUMN deleted;

DROP TYPE history_actions;

DROP FUNCTION f_activities_from_inventory(bigint);

CREATE OR REPLACE FUNCTION public.f_activities_from_inventory(inv_id bigint)
        RETURNS TABLE(id bigint, organization_id integer, created_by integer, "timestamp" timestamp with time zone, name character varying, data jsonb, inventory_id bigint)
        LANGUAGE plpgsql
        AS $function$
                begin
                return QUERY
                    select act.id,
                        act.organization_id,
                        act.created_by,
                        act."timestamp",
                        act."name",
                        act."data",
                    CASE 
                        WHEN 
                        cast(act.data->>'inventory_id' as bigint) IS NOT NULL 
                        THEN 
                        cast(act.data->>'inventory_id' as bigint)
                        ELSE 
                        inv_id 
                    END
                    as inventory_id from activities as act 
                    where
                        (concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'batch') when 'array' then act.data->'batch' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'mother') when 'array' then act.data->'mother' else '[]' end))::varchar[]) or
                        concat('"',(cast(inv_id as varchar)),'"') =  any(array(select jsonb_array_elements(case jsonb_typeof(act.data->'from_inventory_id') when 'array' then act.data->'from_inventory_id' else '[]' end))::varchar[]) or
                        inv_id = cast((case jsonb_typeof(act.data->'from_inventory_id') when 'array' then '0' else act.data->>'from_inventory_id' end) as integer) or
                        inv_id = cast(act.data->>'to_inventory_id' as integer) or
                        inv_id = cast(act.data->>'inventory_id'as integer) or
                        inv_id = cast(act.data->>'related_inventory_id' as integer) or
                        inv_id = cast(act.data->>'linked_inventory_id' as integer));

                END;
                $function$
        ;
        
        
        """
    )
