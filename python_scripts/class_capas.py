"""Endpoints for Capas"""
from flask_restful import Resource
from resource_functions import get_collection, get_resource
from auth0_authentication import requires_auth


class Capas(Resource):

    # Read all
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='capas')


class Capa(Resource):

    # Read single Capa by id
    @requires_auth
    def get(self, current_user, capa_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=capa_id,
            organization_id=organization_id,
            resource='capas')
