'''This resource module controls API related to activities mapping'''

from serializer.activities_mapping import ActivitiesMappingSchemaGetResponse
from models.activities_mapping import ActivitiesMapping
from auth0_authentication import requires_auth
from controllers import BaseController
from flask.json import jsonify
from flask import Blueprint


activities_mapping_schema_get_response = ActivitiesMappingSchemaGetResponse()


class ActivitiesMappingCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):

        response = self.deserialize_queryset(activities_mapping_schema_get_response, ActivitiesMapping.get_activities_mapping())
        
        return jsonify(response)

class ActivitiesMappingWeightAdjustment(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):

        response = self.deserialize_queryset(activities_mapping_schema_get_response, ActivitiesMapping.get_activities_weight_adjustment())
        
        return jsonify(response)


activities_mapping_bp = Blueprint('activities_mapping', __name__)
activities_mapping = ActivitiesMappingCollection.as_view('activities_mapping')
activities_mapping_bp.add_url_rule('/activities_mapping', view_func=activities_mapping, methods=['GET'])


activities_mapping_weight_adjustment_bp = Blueprint('activities_mapping_weight_adjustment', __name__)
activities_mapping_weight_adjustment = ActivitiesMappingWeightAdjustment.as_view('activities_mapping_weight_adjustment')
activities_mapping_weight_adjustment_bp.add_url_rule('/activities_mapping_weight_adjustment', view_func=activities_mapping_weight_adjustment, methods=['GET'])