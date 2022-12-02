'''This resource module controls API related to bulk activities'''

import threading
from auth0_authentication import requires_auth
from flask.helpers import make_response
from controllers import BaseController
from flask import Blueprint, request
from flask.json import jsonify
from models.activity import Activity

from serializer.activities.bulk_activities import BulkActivitiesSchema

bulk_activities_schema_request = BulkActivitiesSchema()

class BulkActivitiesCollection(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id):
        
        params = self.serialize(bulk_activities_schema_request, request.get_json())
        
        threading.Thread(target=Activity.bulk_activity_handle, args=(organization_id, current_user, params['batch_list'], params['activity'])).start()
        
        return make_response(jsonify({"message": "success"}), 200)


bulk_activities_bp = Blueprint('bulk_activities', __name__)

bulk_activities = BulkActivitiesCollection.as_view('bulk_activities')
bulk_activities_bp.add_url_rule('/bulk_activities', view_func=bulk_activities, methods=['POST'])