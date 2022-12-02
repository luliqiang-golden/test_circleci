'''Class for Sops'''

from flask_restful import Resource
from flask import jsonify
from class_errors import EngineError

from db_functions import TABLE_COLUMNS, insert_into_db
from resource_functions import prep_args, get_collection, get_resource
from auth0_authentication import requires_auth
from class_errors import ClientBadRequest
from class_sop_versions import SopVersions
from activities.sop_assign_user import SopAssignUser
from activities.sop_assign_department import SopAssignDepartment

class Sops(Resource):

    @requires_auth
    def get(self, current_user, organization_id=None):

        filters = []

        try:
            resource = 'vw_sops'
        except EngineError:
            filters = [('assigned_to_id', '=', current_user['user_id']), ('status', '!=', 'disabled')]
            resource = 'vw_sop_assignments'
        
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource=resource,
            filters=filters)

    @requires_auth
    def post(self, current_user, organization_id):
        """
        Creates an Sop

        :param name: Name of the sop 
        :param content_type: Content type of the sop
        :param department_id: ID of the department to assign the sop to
        :param assigned_users: A list of IDs of the users to which the sop will be assigned 

        :returns: An object containing the id of the new sop the corresponding activity's id 
        """
        resource = 'sops' 
        args = prep_args(resource, organization_id, current_user)

        if 'content_type' not in args:
            raise ClientBadRequest({
                'code': 'required_field_error',
                'message': 'The "content_type" field is required'
            }, 400)

        if 'name' not in args:
            raise ClientBadRequest({
                'code': 'required_field_error',
                'message': 'The "name" field is required'
            }, 400)

        allowed_content_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if args['content_type'] not in allowed_content_types:
            raise ClientBadRequest({
                'code': 'content_type_error',
                'message': 'The "{}" content-type is not permitted'.format(args['content_type'])
            }, 400)

        record = {
            'name': args['name'],
            'organization_id': organization_id
        }
        db_result = insert_into_db(resource, record)
        ### create activity
        sop_id = db_result.get('id')

        # create new version
        # no need to pass payload since create_new_version uses prep_args which will have the request data
        version_response = SopVersions.create_new_version(current_user, sop_id, organization_id)
        sop_version_id = version_response.get('id')
        
        current_user_id = current_user.get('user_id')
        # set sop department using sop_assign_department activity
        for department in args['departments']:
            activity_args = {
                'sop_id': sop_id,
                'version_id': sop_version_id,
                'department_id': department,
                'created_by_id': args['created_by'],
                'organization_id': args['organization_id']
            }
            SopAssignDepartment.do_activity(activity_args, current_user)

        if 'assignments' not in args or len(args['assignments']) < 1:
            raise ClientBadRequest({
                'code': 'required_field_error',
                'message': 'A list of at least 1 user (to whom the Sop will be assigned) is required'
            }, 400)

        # assign sop to users using sop_assign_user activity
        for assigned_to_id in args['assignments']:
            activity_args = {
                'sop_id': sop_id,
                'version_id': sop_version_id,
                'assigned_to_id': assigned_to_id,
                'created_by_id': args['created_by'],
                'organization_id': args['organization_id']
            }
            SopAssignUser.do_activity(activity_args, current_user)

        return jsonify({
            'sop_id': sop_id,
            'sop_affected_rows': db_result.get('affected_rows'),
            'sop_version_id': sop_version_id,
            'sop_version_affeted_rows': version_response.get('affected_rows'),
            'upload_url': version_response.get('upload_url')
        })

class Sop(Resource):

    @requires_auth
    def get(self, current_user, resource_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            organization_id=organization_id,
            filters=filters,
            resource=resource,
            paginate=False)
