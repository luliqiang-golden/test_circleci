'''This resource module controls API related to backdate activities'''

from models.inventory import Inventory
from models.activity import Activity
from serializer.activities.backdate_activity import BackdateActivitiesSchemaPutRequest
from auth0_authentication import requires_auth
from flask.helpers import make_response
from controllers import BaseController
from flask import Blueprint, request
from flask.json import jsonify

backdate_activities_schema_put_request = BackdateActivitiesSchemaPutRequest()

class BackdateActivitiesCollection(BaseController):

    @requires_auth
    def put(self, current_user, organization_id):

        data = self.serialize(backdate_activities_schema_put_request, request.get_json())

        result = Activity.backdate_activity(organization_id, current_user.get('user_id'), data['activity_ids'], data['timestamp'], data['reason_for_modification'])

        for act in result:
            Inventory.backdate_inventory_by_activity_id(organization_id, data['timestamp'], act)

        return self.get_success_response(data=[])


# Make blueprint for backdate activities API
backdate_activity_bp = Blueprint('backdate_activity', __name__)

# Define url_patterns related to backdate activities API here
backdate_activity = BackdateActivitiesCollection.as_view('backdate_activity')
backdate_activity_bp.add_url_rule('/backdate_activity', view_func=backdate_activity, methods=['PUT'])
