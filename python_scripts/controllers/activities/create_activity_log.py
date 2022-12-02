'''This resource module controls API related to create activity log activity'''

from serializer.activities.create_activity_log import CreateActivityLogSchemaPostRequest, CreateActivityLogSchemaResponse, CreateActivityLogSchemaPutRequest, CreateActivityLogSchemaDeleteRequest 
from auth0_authentication import requires_auth
from flask.helpers import make_response
from controllers import BaseController
from flask import Blueprint, request
from models.activity import Activity
from flask.json import jsonify

create_activity_log_schema_response = CreateActivityLogSchemaResponse()
create_activity_log_schema_post_request = CreateActivityLogSchemaPostRequest()
create_activity_log_schema_put_request = CreateActivityLogSchemaPutRequest()
create_activity_log_schema_delete_request = CreateActivityLogSchemaDeleteRequest()

class CreateActivityLogCollection(BaseController):
    @requires_auth
    def post(self, current_user, organization_id):

        params = self.serialize(create_activity_log_schema_post_request, request.get_json())

        data = {
            'description': params.get('description'),
            'detail': params.get('detail'),
            'inventory_id': params.get('inventory_id'),
            'uploads': params.get('uploads')
        }

        activity = Activity.save_activities(organization_id, data, current_user.get('user_id'), 'create_activity_log')
        
        response = self.deserialize_object(create_activity_log_schema_response, activity)
        
        return make_response(jsonify(response), 201)

    @requires_auth
    def put(self, current_user, organization_id, activity_id):

        params = self.serialize(create_activity_log_schema_put_request, request.get_json())

        data = {
            'description': params.get('description'),
            'detail': params.get('detail'),
            'inventory_id': params.get('inventory_id'),
            'uploads': params.get('uploads')
        }

        activity = Activity.update_activities(activity_id, organization_id, data, current_user.get('user_id'), 'create_activity_log', params.get('reason_for_modification'), params.get('timestamp'))
        
        response = self.deserialize_object(create_activity_log_schema_response, activity)

        return make_response(jsonify(response), 200)
    
    @requires_auth
    def delete(self, current_user, organization_id, activity_id):
        
        params = self.serialize(create_activity_log_schema_delete_request, request.get_json())
        
        Activity.delete_activities(activity_id, organization_id, current_user.get('user_id'), 'create_activity_log', params.get('reason_for_modification'))
        
        return make_response(jsonify({}), 200)


# Make blueprint for create activity log API
create_activity_log_bp = Blueprint('create_activity_log', __name__)

# Define url_patterns related to create activity log API here
create_activity_log = CreateActivityLogCollection.as_view('create_activity_log')
create_activity_log_bp.add_url_rule('/create_activity_log', view_func=create_activity_log, methods=['POST'])
create_activity_log_bp.add_url_rule('/create_activity_log/<int:activity_id>', view_func=create_activity_log, methods=['PUT', 'DELETE'])