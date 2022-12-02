'''This resource module controls API related to activities history'''

from serializer.activities_history import ActivitiesHistorySchemaGetResponse
from models.activities_history import ActivitiesHistory
from auth0_authentication import requires_auth
from controllers import BaseController
from flask.json import jsonify
from flask import Blueprint


activities_history_schema_get_response = ActivitiesHistorySchemaGetResponse()


class ActivitiesHistoryCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id, activity_id = None):
        
        if activity_id:
            response = self.deserialize_queryset(activities_history_schema_get_response, ActivitiesHistory.get_activity_history_by_id(organization_id, activity_id))
        else:
            response = self.deserialize_queryset(activities_history_schema_get_response, ActivitiesHistory.get_all_activity_history(organization_id))
        
        return jsonify(response)


# Make blueprint for activities history API
activities_history_bp = Blueprint('activities_history', __name__)

# Define url_patterns related to activities history API here
activities_history = ActivitiesHistoryCollection.as_view('activities_history')
activities_history_bp.add_url_rule('/activities_history', view_func=activities_history, methods=['GET'])
activities_history_bp.add_url_rule('/activities_history/<int:activity_id>', view_func=activities_history, methods=['GET'])