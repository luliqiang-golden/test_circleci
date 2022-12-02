"""API Server Entrypoint"""
from flask import jsonify
from flask_talisman import Talisman
from flask_restful import Api

from class_organizations import Organizations, Organization
from class_clients import Clients, Client
from class_products import Products, Product
from class_inventories import Inventories, Inventory, InventoriesByType, BatchRecord, DestructionsHistory
from class_activities import Activities, Activity, ActivitiesById, MothersInventoryFromMotherBatch, ActivitiesByInventory
from class_taxonomies import Taxonomies, Taxonomy
from class_uploads import Uploads, Upload, UploadVersions
from class_users import Users, UserLoggedIn, User, UserLogin
from class_roles import Roles, Role, ActivitiesList, TablesList
from class_taxonomy_options import TaxonomyOption, TaxonomyOptions
from class_rooms import Rooms, Room
from class_rules import Rules, Rule
from class_labels import GetLabel, PreviewLabel
from class_equipment import EquipmentCollection, EquipmentResource
from class_analytics import Analytics, AccountingInventoriesAnalyticsCost, AccountingSupplyAnalyticsCost
from class_yield import HistoricYield, BatchYield, VarietyYield
from class_skus import SKUs, SKU
from class_crm_account import CRMAccounts, CRMAccount
from class_stages import BatchStages
from class_orders import Orders, Order
from class_order_items import OrderItems, OrderItem
from class_shipments import Shipments, Shipment
from class_capas import Capas, Capa
from class_capa_links import CapaLinks, CapaLink
from class_capa_actions import CapaActions, CapaAction
from class_consumable_classes import ConsumableClasses, ConsumableClass
from class_consumable_lots import ConsumableLots, ConsumableLot
from class_transactions import Transactions, Transaction
from class_transaction_allocations import TransactionAllocations, TransactionAllocation
from class_errors import ClientBadRequest, EngineError, AuthError, DatabaseError
from class_me import Me
from class_recalls import Recall, Recalls, RecallDetails
from class_sops import Sops, Sop
from class_sop_log import SopLogs
from class_sop_versions import SopVersions, SopVersion, UploadSopVersion
from class_departments import Departments, Department
from class_sop_assignments import SopAssignments, SopSignatures
from class_notifications import Notifications
from class_deviation_reports import DeviationReports, DeviationReport, DeviationReportsWithAssignments, DeviationReportWithAssignments
from class_deviation_reports_assignments import DeviationReportsAssignments, DeviationReportsAssignment
from class_external_crm_account import ExternalCrmAccounts, ExternalCrmAccount
from class_external_order import ExternalOrders, ExternalOrder
from class_external_order_item import ExternalOrderItems, ExternalOrderItem
from class_external_shipment import ExternalShipments, ExternalShipment
from class_external_webhooks import WebhookSubscription, WebhookUnsubscription
from class_external_sr_fax import BucketUpload
from class_invoices import Invoices, Invoice, GenerateInvoice
from class_taxes import Taxes

from app import app, db
from admin import config_admin
from db_functions import DATABASE, get_tables
from dotenv import load_dotenv

load_dotenv('.env')  # pylint: disable=C0413


# Import Classes for Routes defined below


# Define Flask app
Talisman(app)
app.config['PROPAGATE_EXCEPTIONS'] = True  # Flask-Restful suppresses errors :(
config_admin(app, db)

# gets all tables and its columns
get_tables()


# Error handling formatter for auth0_authentication
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    DATABASE.dedicated_connection().rollback()
    return response


# Error handling formatter for class_users and class_roles
@app.errorhandler(ClientBadRequest)
def handle_does_not_exist_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    DATABASE.dedicated_connection().rollback()
    return response


# Error handling formatter for rule_engine
@app.errorhandler(EngineError)
def handle_engine_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    DATABASE.dedicated_connection().rollback()
    return response


# Error handling formatter for db_functions
@app.errorhandler(DatabaseError)
def handle_db_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    DATABASE.dedicated_connection().rollback()
    return response


@app.teardown_request
def rollback_db_on_exception(exception=None):
    if exception:
        DATABASE.dedicated_connection().rollback()


@app.before_request
def begin_db_transaction():
    DATABASE.dedicated_connection().begin()


@app.after_request
def commit_db(req):
    DATABASE.dedicated_connection().commit()
    return req


# Actually setup the Api resource routing here
# add optional organization filter to routes to cut down records returned
api = Api(app, prefix='/v1', catch_all_404s=True)  # pylint: disable=C0103

# Me (current user)
api.add_resource(Me, '/me')

# Organizations
api.add_resource(Organizations, '/organizations')  # get all, insert new
api.add_resource(Organization,
                 '/organizations/<organization_id>')  # get / update single

# Clients
api.add_resource(Clients, '/organizations/<organization_id>/clients')
api.add_resource(Client,
                 '/organizations/<organization_id>/clients/<client_id>')

# Products
api.add_resource(Products, '/organizations/<organization_id>/products')
api.add_resource(Product,
                 '/organizations/<organization_id>/products/<product_id>')

# Inventories
api.add_resource(Inventories, '/organizations/<organization_id>/inventories')
api.add_resource(InventoriesByType,
'/organizations/<organization_id>/inventories/type/<inventory_type>',

'/organizations/<organization_id>/inventories/type/<inventory_type>/archive/<archive_type>')
api.add_resource(DestructionsHistory, '/organizations/<organization_id>/destructions-history')
api.add_resource(Inventory,
                 '/organizations/<organization_id>/inventories/<inventory_id>')
api.add_resource(BatchRecord,
                 '/organizations/<organization_id>/inventories/<inventory_id>/batch_record')

# Activities
api.add_resource(Activities, '/organizations/<organization_id>/activities')
api.add_resource(Activity,
                 '/organizations/<organization_id>/activities/<activity_id>')
api.add_resource(ActivitiesById,
                 '/organizations/<organization_id>/activities-by-id/<table_id>/<table_type>')
api.add_resource(ActivitiesByInventory,
                 '/organizations/<organization_id>/activities_by_inventory/<inventory_id>',
                 '/organizations/<organization_id>/activities_by_inventory/<inventory_id>/parent/<parent>')

# ActivitiesList
api.add_resource(ActivitiesList, '/organizations/<organization_id>/activities-list')

api.add_resource(MothersInventoryFromMotherBatch, '/organizations/<organization_id>/mothers-inventory-from-mother-batch/<mother_batch_id>')

# TablesList
api.add_resource(TablesList, '/organizations/<organization_id>/tables-list')

# Taxonomies
api.add_resource(Taxonomies, '/organizations/<organization_id>/taxonomies')
api.add_resource(Taxonomy,
                 '/organizations/<organization_id>/taxonomies/<taxonomy_id>')

# Taxonomy Options
api.add_resource(
    TaxonomyOptions,
    '/organizations/<organization_id>/taxonomies/<taxonomy_id>/options')
api.add_resource(
    TaxonomyOption,
    '/organizations/<organization_id>/taxonomy-options/<option_id>')

# Uploads
api.add_resource(Uploads, '/uploads',
                 '/organizations/<organization_id>/uploads')
api.add_resource(Upload, '/uploads/<upload_id>',
                 '/organizations/<organization_id>/uploads/<upload_id>')
api.add_resource(UploadVersions, '/uploads/<upload_id>/versions',
                 '/organizations/<organization_id>/uploads/<upload_id>/versions')

# Users
api.add_resource(Users, '/organizations/<organization_id>/users')
api.add_resource(User, '/organizations/<organization_id>/users/<user_id>')
api.add_resource(UserLoggedIn, '/organizations/<organization_id>/user')
api.add_resource(UserLogin, '/login')

# Roles
api.add_resource(Roles, '/organizations/<organization_id>/roles')
api.add_resource(Role, '/organizations/<organization_id>/roles/<role_id>')

# Rooms
api.add_resource(Rooms, '/rooms', '/organizations/<organization_id>/rooms')
api.add_resource(Room, '/rooms/<room_id>',
                 '/organizations/<organization_id>/rooms/<room_id>')

# Rules
api.add_resource(Rules, '/organizations/<organization_id>/rules')
api.add_resource(Rule, '/organizations/<organization_id>/rules/<rule_id>')

# Equipment
api.add_resource(EquipmentCollection,
                 '/organizations/<organization_id>/equipment')
api.add_resource(EquipmentResource,
                 '/organizations/<organization_id>/equipment/<equipment_id>')

# Labels
api.add_resource(GetLabel,
                '/organizations/<organization_id>/label/<label_id>/<label_type>/<label_format>/<object_id>',
                '/organizations/<organization_id>/label/<label_id>/<label_type>/<label_format>/<object_id>/number_of_labels/<number_of_labels>',
                 '/organizations/<organization_id>/label/<label_id>/<label_type>/<label_format>/<object_id>/number_of_labels/<number_of_labels>/show_number/<show_number>/<start_number>/<out_of>')
api.add_resource(PreviewLabel,
                 '/organizations/<organization_id>/preview-label/<dpmm>/<size>')

# Analytics
api.add_resource(Analytics, '/organizations/<organization_id>/analytics')
api.add_resource(AccountingInventoriesAnalyticsCost,
        '/organizations/<organization_id>/analytics/accounting/inventory/group-by/<group_by>',
        '/organizations/<organization_id>/analytics/accounting/inventory/group-by/<group_by>/<variety>')
api.add_resource(AccountingSupplyAnalyticsCost, '/organizations/<organization_id>/analytics/accounting/supply/month/<month>')

# Yield
api.add_resource(
    HistoricYield, '/organizations/<organization_id>/yield/historic')
api.add_resource(
    BatchYield, '/organizations/<organization_id>/yield/batch/<batch_id>')
api.add_resource(
    VarietyYield, '/organizations/<organization_id>/yield/variety/<variety>')

# CRM Account
api.add_resource(CRMAccounts, '/organizations/<organization_id>/crm-accounts')
api.add_resource(
    CRMAccount, '/organizations/<organization_id>/crm-accounts/<crm_account_id>')

# Orders
api.add_resource(Orders, '/organizations/<organization_id>/orders')
api.add_resource(
    Order, '/organizations/<organization_id>/orders/<order_id>')

# Order Items
api.add_resource(OrderItems, '/organizations/<organization_id>/order-items')
api.add_resource(
    OrderItem, '/organizations/<organization_id>/order-items/<order_item_id>')

# Capas
api.add_resource(Capas, '/organizations/<organization_id>/capas')
api.add_resource(
    Capa, '/organizations/<organization_id>/capas/<capa_id>')

# Capas Links
api.add_resource(CapaLinks, '/organizations/<organization_id>/capa-links')
api.add_resource(
    CapaLink, '/organizations/<organization_id>/capa-links/<capa_link_id>')

# Capas Actions
api.add_resource(CapaActions, '/organizations/<organization_id>/capa-actions')
api.add_resource(
    CapaAction, '/organizations/<organization_id>/capa-actions/<capa_action_id>')

# Recalls
api.add_resource(Recalls, '/organizations/<organization_id>/recalls')
api.add_resource(
    Recall, '/organizations/<organization_id>/recalls/<recall_id>')
api.add_resource(
    RecallDetails, '/organizations/<organization_id>/recalls/<recall_id>/detail')

# Sops
api.add_resource(Sops, '/organizations/<organization_id>/sops')
api.add_resource(SopLogs, '/organizations/<organization_id>/sops/logs')
# api.add_resource(Sop, '/organizations/<organization_id>/sops/<sop_id>')

# Sop Versions
api.add_resource(SopVersions, '/organizations/<organization_id>/sops/<sop_id>/versions')
api.add_resource(SopVersion, '/organizations/<organization_id>/sops/<sop_id>/versions/<version_number>')
api.add_resource(UploadSopVersion, '/organizations/<organization_id>/uploads/sops/<sop_id>/versions')

# Sop Assignments
api.add_resource(SopAssignments, '/organizations/<organization_id>/sops/<sop_id>/assignments')
api.add_resource(SopSignatures, '/organizations/<organization_id>/sops/signatures')

# Departments
api.add_resource(Departments, '/organizations/<organization_id>/departments')
api.add_resource(Department, '/organizations/<organization_id>/departments/<department_id>')

# Notifications
api.add_resource(Notifications, '/organizations/<organization_id>/notifications')


# Shipments
api.add_resource(Shipments, '/organizations/<organization_id>/shipments')
api.add_resource(Shipment, '/organizations/<organization_id>/shipments/<shipment_id>')

# Consumable Lots
api.add_resource(
    ConsumableLots, '/organizations/<organization_id>/consumable-lots')
api.add_resource(
    ConsumableLot, '/organizations/<organization_id>/consumable-lots/<consumable_lot_id>')

# Consumable Classes
api.add_resource(
    ConsumableClasses, '/organizations/<organization_id>/consumable-classes')
api.add_resource(
    ConsumableClass, '/organizations/<organization_id>/consumable-classes/<consumable_class_id>')


# Transactions
api.add_resource(Transactions, '/organizations/<organization_id>/transactions')
api.add_resource(
    Transaction, '/organizations/<organization_id>/transactions/<transaction_id>')

# Transaction Allocations
api.add_resource(TransactionAllocations,
                 '/organizations/<organization_id>/transaction-allocations')
api.add_resource(
    TransactionAllocation, '/organizations/<organization_id>/transaction-allocations/<transaction_allocation_id>')

# Stages
api.add_resource(
    BatchStages, '/organizations/<organization_id>/stages/batch/<batch_id>')

# Deviation Reports
api.add_resource(DeviationReports, '/organizations/<organization_id>/deviation-reports')
api.add_resource(
    DeviationReport, '/organizations/<organization_id>/deviation-reports/<deviation_report_id>')

# Deviation Reports Assignments
api.add_resource(DeviationReportsAssignments, '/organizations/<organization_id>/deviation-reports-assignments')
api.add_resource(
    DeviationReportsAssignment, '/organizations/<organization_id>/deviation-reports-assignments/<deviation_report_assignment_id>')

api.add_resource(DeviationReportsWithAssignments, '/organizations/<organization_id>/deviation-reports-with-assignments')
api.add_resource(
    DeviationReportWithAssignments, '/organizations/<organization_id>/deviation-reports-with-assignments/<deviation_report_with_assignments_id>')

# Third party Endpoints for CRM Accounts
api.add_resource(ExternalCrmAccounts, '/organizations/<organization_id>/external_crm_accounts')
api.add_resource(ExternalCrmAccount, '/organizations/<organization_id>/external_crm_accounts/<crm_account_id>')

# Third party Endpoints for External Orders
api.add_resource(ExternalOrders, '/organizations/<organization_id>/external_orders')
api.add_resource(ExternalOrder, '/organizations/<organization_id>/external_orders/<order_id>')

# Third party Endpoints for External Order Items
api.add_resource(ExternalOrderItems, '/organizations/<organization_id>/external_order_items')
api.add_resource(ExternalOrderItem, '/organizations/<organization_id>/external_order_items/<order_item_id>')

# Third party Endpoints for External Shipments
api.add_resource(ExternalShipments, '/organizations/<organization_id>/external_shipments')
api.add_resource(ExternalShipment, '/organizations/<organization_id>/external_shipments/<shipment_id>')


# SRFax endpoint
api.add_resource(BucketUpload, '/organizations/<organization_id>/sr_fax')

# Webhook endpoints
api.add_resource(WebhookSubscription, '/webhooks/subscribe')
api.add_resource(WebhookUnsubscription, '/webhooks/unsubscribe/<webhook_record_id>')

# Invoices endpoints
api.add_resource(Invoices, '/organizations/<organization_id>/invoices')
api.add_resource(Invoice, '/organizations/<organization_id>/invoices/<invoice_id>')
api.add_resource(GenerateInvoice, '/organizations/<organization_id>/invoices/<invoice_id>/generate-invoice')

# Taxes
api.add_resource(Taxes, '/organizations/<organization_id>/taxes')

if __name__ == '__main__':
    app.run(debug=True)
