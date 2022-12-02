"""Endpoints for Consumable Classes"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource

from auth0_authentication import requires_auth


class ConsumableClasses(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        query = '''
            SELECT cc.*,
            (
                SELECT COALESCE (SUM (cl.current_qty), 0)
                FROM consumable_lots AS cl
                WHERE cl.class_id = cc.id
            )   AS current_qty
            FROM consumable_classes cc
            ORDER BY id DESC'''
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='consumable_classes',
            query = query)



class ConsumableClass(Resource):

    # Read single Consumable Class by id
    @requires_auth
    def get(self, current_user, consumable_class_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=consumable_class_id,
            organization_id=organization_id,
            resource='consumable_classes')
