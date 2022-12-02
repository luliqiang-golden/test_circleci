'''This resource module controls API related to skus'''

from flask import Blueprint, request
from flask.helpers import make_response
from flask.json import jsonify
from auth0_authentication import requires_auth
from models.order_item import OrderItem
from controllers import BaseController
from serializer.skus import SkusSchema
from serializer.skus import SkusUpdateSchema
from models.skus import Skus
from models.activity import Activity
from models.webhook import Webhook

from app import db
from sqlalchemy.exc import SQLAlchemyError

from class_errors import ClientBadRequest

sku_schema = SkusSchema()
sku_update_schema = SkusUpdateSchema()
class SkusCollection(BaseController):

    @requires_auth
    def post(self, current_user, organization_id):
        """Example Payload for this API Method
            {
                "reserved": 0,
                "status": "enabled",
                "external_sku_id": 7084611764382,
                "external_sku_variant_id": 41487046377630,
                "name": "Gelato 33 - 3.5g Test",
                "organization_id": 1,
                "package_type": "packaged",
                "price": 40.00,
                "sales_class": "patient",
                "target_qty": 7.0,
                "target_qty_unit": "dry",
                "variety": "3.5g",
                "product_type": "shopify"
            }
        """
        
        params = request.get_json()
        created_by = current_user.get("user_id")
        params["organization_id"] = organization_id
        params["created_by"] = created_by
        data = self.serialize(sku_schema, params)
        
        sku_data, product_type = Skus.format_post_request(data, params)

        result, message = Skus.add_sku(sku_data, data, created_by, organization_id) 
        
        if result:    
            sku_data_webhook = Skus.get_sku_detail_for_webhook(sku_data.id)
            Activity.save_activities(organization_id, sku_data_webhook, created_by, "create_sku", parent_id = None, edited = False, deleted = False, timestamp = None)
            
            if not product_type:
                Webhook().firing_webhooks('skus.created', sku_data_webhook)
                
            return jsonify({"message":"Sku added successfully", "sku_id": sku_data.id}), 200            
        else:
            ClientBadRequest({"message": f"Sku addition failed!", "error": message}, 404)
        
    
    @requires_auth
    def get(self, current_user, organization_id):

        '''Returns list of all the skus present in table'''
        
        queryset, query, pagination = Skus.format_get_request(request.args, organization_id)
            
        data = self.deserialize_queryset(sku_schema, queryset)

        return self.get_success_response(data, query, pagination)

class SkusResource(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id, sku_id):
        obj = Skus.query.get(sku_id)
        data = self.deserialize_object(sku_schema, obj)
        return jsonify(data), 200
    
    @requires_auth
    def delete(self, current_user, organization_id, sku_id):
        Skus.query.filter_by(id=sku_id).delete()
        db.session.commit()
        return self.get_success_response({"operation": "SKU deleted successfully."})

    @requires_auth
    def patch(self, current_user, organization_id, sku_id):
        """Example Payload for this API Method
            {
                "reserved": 0,
                "status": "enabled",
                "external_sku_id": 7084611764382,
                "external_sku_variant_id": 41487046377630,
                "name": "Gelato 33 - 3.5g Test",
                "organization_id": 1,
                "package_type": "packaged",
                "price": 40.00,
                "sales_class": "patient",
                "target_qty": 7.0,
                "target_qty_unit": "dry",
                "variety": "3.5g",
                "product_type": "shopify"
            }
        """
        params = request.get_json()
        obj = Skus.query.get(sku_id)
        obj.data = dict(obj.data)
        obj.attributes = dict(obj.attributes)
        created_by = current_user.get("user_id")
        
        org_data = self.deserialize_object(sku_schema, obj)
        data = self.serialize(sku_update_schema, params)
        
        update_data, only_external_sku_id = Skus.format_patch_request(org_data, data, params, created_by, organization_id)
        
        try:
            Skus.update_sku(sku_id, update_data)
            sku_data_webhook = Skus.get_sku_detail_for_webhook(sku_id)
            if not only_external_sku_id:
                Webhook().firing_webhooks('skus.updated', sku_data_webhook)
            return jsonify({"message":"Sku updated successfully", "sku_id": sku_id}), 200
        except SQLAlchemyError as e:
            error = str(e.orig)
            ClientBadRequest({"message": f"Sku updation failed!", "error": error}, 404)
        

class SkusAvailableStock(BaseController):

    @requires_auth
    def get(self, current_user, organization_id):

        '''Returns list of all the skus present in table'''

        params = request.args

        queryset = OrderItem.get_available_stock(self, current_user, organization_id, params)

        response = []

        for data in queryset:
            entity_response = {
                'sku_id':  data.sku_id,
                'sku_name': data.sku_name,
                'sku_price': data.sku_price,
                'variety': data.sku_variety,
                'timestamp': data.sku_timestamp,
                'sales_class': data.sku_sales_class,
                'target_qty': data.sku_target_qty,
                'target_qty_unit': data.sku_target_qty_unit,
                'available_stock': int(data.count - data.sku_reserved),
            }
            response.append(entity_response)

        return make_response(jsonify(response), 200)
    
# Make blueprint for skus API
skus_bp = Blueprint('sku', __name__)

# Define url_patterns related to skus API here
skus = SkusCollection.as_view('skus')
skus_bp.add_url_rule('skus', view_func=skus, methods=['POST', 'GET'])

skus_res = SkusResource.as_view('sku_res')
skus_bp.add_url_rule('skus/<sku_id>', view_func=skus_res, methods=['PATCH', 'GET', 'DELETE'])

sku_aval_stocks = SkusAvailableStock.as_view('sku_aval_stocks')
skus_bp.add_url_rule('skus/available-stock', view_func=sku_aval_stocks, methods=['GET'])