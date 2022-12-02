'''This resource module controls API related to notifications'''

from auth0_authentication import requires_auth
from flask.helpers import make_response
from controllers import BaseController
from flask import Blueprint
from flask.json import jsonify
from models.notification import Notification
from serializer.notification import NotificationSchemaGetResponse

notification_schema_get_response = NotificationSchemaGetResponse()

class NotificationCollection(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id):
        
        if(Notification.has_notification(organization_id, current_user['user_id'])):
            response = self.deserialize_object(notification_schema_get_response, Notification.pop_notification(organization_id, current_user['user_id']))
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify(None), 200)



activities_notifications_bp = Blueprint('activities_notifications', __name__)

activities_notifications = NotificationCollection.as_view('activities_notifications')
activities_notifications_bp.add_url_rule('/activities_notifications', view_func=activities_notifications, methods=['GET'])