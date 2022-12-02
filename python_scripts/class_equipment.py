"""Endpoints for equipment"""

from flask import jsonify
from flask_restful import Resource

from resource_functions import get_collection, get_resource
from resource_functions import prep_args
from db_functions import insert_into_db, update_into_db
from class_errors import ClientBadRequest
from auth0_authentication import requires_auth


class EquipmentCollection(Resource):
    """Equipment collection endpoints"""

    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get all equipment for an org"""

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='equipment')

    @requires_auth
    def post(self, current_user, organization_id=None):
        """Insert new equipment"""

        args = prep_args('equipment', organization_id, current_user)

        if args.get('') == 'sensor' and not args.get('default_unit_type'):
            raise ClientBadRequest({
                "code": "missing_required_fields",
                "message": "default_unit_type required for type sensor"
            }, 400)

        db_result = insert_into_db('equipment', args)

        activity = {
            'name': 'create_equipment',
            'equipment_id': db_result['id'],
            'equipment_data': args,
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
        }
        activity_result = insert_into_db('activities', activity)

        db_result['activity_id'] = activity_result['id']

        # send back the results with the new id
        return jsonify(db_result)


class EquipmentResource(Resource):
    """Equipment resource endpoints"""

    @requires_auth
    def get(self, current_user, equipment_id, organization_id=None):
        """Get a specific equipment by id"""
        return get_resource(
            current_user=current_user,
            resource_id=equipment_id,
            organization_id=organization_id,
            resource='equipment')

    @requires_auth
    def patch(self, current_user, equipment_id, organization_id=None):
        """Update an equipment item"""
        args = prep_args('equipment', organization_id, current_user)

        db_result = update_into_db('equipment', equipment_id, args)

        activity = {
            'name': 'update_equipment',
            'equipment_data': args,
            'equipment_id': equipment_id,
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
        }
        activity_result = insert_into_db('activities', activity)

        db_result['activity_id'] = activity_result['id']

        # send back the results with the new id
        return jsonify(db_result)
