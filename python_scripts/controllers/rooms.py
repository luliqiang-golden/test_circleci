'''This resource module controls API related to rooms'''

from models.rooms import Rooms
from serializer.rooms import RoomsPerSectionSchemaGetResponse
from auth0_authentication import requires_auth
from controllers import BaseController
from flask import Blueprint
from flask.json import jsonify




class RoomsCollection(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id):
        
        result = Rooms.get_all_rooms(organization_id)

        return jsonify(RoomsPerSectionSchemaGetResponse(many=True).dump(result))


# Make blueprint for rooms API
rooms_bp = Blueprint('rooms', __name__)

# Define url_patterns related to rooms API here
rooms = RoomsCollection.as_view('rooms')
rooms_bp.add_url_rule('/rooms_by_zone', view_func=rooms, methods=['GET'])