"""Provides all reporting activities"""
from flask import Blueprint
from flask_restful import Api, Resource

from .lot_items_csv import LotItemsCSV
from .lots_csv import LotsCSV
from .activities_csv import ActivitiesCSV
from .ref_activities_csv import RefActivitiesCSV
from .canada_csv import CanadaCSV
from .client_csv import ClientCSV
from .inventory_csv import InventoryCSV
from .batches_csv import BatchesCSV
from .hcr_breakdown import ReportsHCRBreakdownCSV


reporting_bp = Blueprint('reporting', __name__)
reporting_api = Api(reporting_bp)


reporting_api.add_resource(ActivitiesCSV, '/activities-csv')
reporting_api.add_resource(BatchesCSV, '/batches-csv')
reporting_api.add_resource(RefActivitiesCSV, '/ref-activities-csv')
reporting_api.add_resource(CanadaCSV, '/canada-csv')
reporting_api.add_resource(ClientCSV, '/client-csv')
reporting_api.add_resource(InventoryCSV, '/inventory-csv')
reporting_api.add_resource(LotsCSV, '/lots-csv')
reporting_api.add_resource(LotItemsCSV, '/lot-items-csv')
reporting_api.add_resource(ReportsHCRBreakdownCSV, '/hcr-breakdown-csv')
