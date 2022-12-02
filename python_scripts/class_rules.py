"""Endpoints for rules"""

from flask import jsonify
from flask_restful import Resource

from resource_functions import get_collection, get_resource
from resource_functions import prep_args
from db_functions import insert_into_db, update_into_db
from class_errors import ClientBadRequest

from auth0_authentication import requires_auth


class Rules(Resource):
    """Rules collection endpoints"""

    # Read all rule records
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get all rules for an org"""

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Rules',
        )

    @requires_auth
    def post(self, current_user, organization_id=None):
        """Insert new rule"""

        args = prep_args('rules', organization_id, current_user)

        if 'conditions' not in args:
            raise ClientBadRequest({
                "code": "conditions_not_found",
                "message": "Conditions are required"
            }, 400)

        db_result = insert_into_db('rules', args)

        activity = {
            'name': 'create_rule',
            'rule_id': db_result['id'],
            'rule_data': args,
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
        }
        activity_result = insert_into_db('activities', activity)

        db_result['activity_id'] = activity_result['id']

        # send back the results with the new id
        return jsonify(db_result)


class Rule(Resource):
    """Rules resource endpoints"""

    @requires_auth
    def get(self, current_user, rule_id, organization_id=None):
        """Get a specific rule by id"""
        return get_resource(
            current_user=current_user,
            resource_id=rule_id,
            organization_id=organization_id,
            resource='Rules')

    @requires_auth
    def patch(self, current_user, rule_id, organization_id=None):
        """Insert new rule"""
        args = prep_args('rules', organization_id, current_user)

        if 'conditions' not in args:
            raise ClientBadRequest({
                "code": "conditions_not_found",
                "message": "Conditions are required"
            }, 400)

        db_result = update_into_db('rules', rule_id, args)

        activity = {
            'name': 'update_rule',
            'rule_data': args,
            'rule_id': rule_id,
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
        }
        activity_result = insert_into_db('activities', activity)

        db_result['activity_id'] = activity_result['id']

        # send back the results with the new id
        return jsonify(db_result)
