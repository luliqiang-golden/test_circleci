'''Class for Sop versions'''

import datetime
from flask import jsonify
from flask_restful import Resource
from cloud_storage import CloudStorage

from auth0_authentication import requires_auth
from db_functions import TABLE_COLUMNS, insert_into_db
from resource_functions import prep_args, get_collection, get_resource
from class_errors import ClientBadRequest
from activities.sop_assign_department import SopAssignDepartment
from activities.sop_assign_user import SopAssignUser
from activities.sop_uploaded_new_version import SopUploadedNewVersion
from time import strftime

class SopVersions(Resource):

    @requires_auth
    def get(self, current_user, sop_id, organization_id=None):
        resource = 'vw_sop_versions'

        filters = [('sop_id', '=', sop_id)]

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource=resource,
            filters=filters)

    @staticmethod
    def create_new_version(current_user, sop_id, organization_id):
        resource = 'sop_versions'
        # check rules and args here??? or in the post???
        # move require args outside???
        # add requires auth???
        args = prep_args('sop_versions', organization_id, current_user)
        args['sop_id'] = sop_id

        required_args = {
            'description'
        }

        # if args doesn't have all of required args
        if required_args - set(args):
            raise ClientBadRequest(
                {
                    'code': 'missing_required_fields',
                    'description': 'Missing one of {}'.format(
                        ', '.join(required_args))
                }, 400)

        # get list of columns in the sop_versions table and copy them from the args object over into a record object
        columns = [col for col in TABLE_COLUMNS.get(resource) if col not in ['id']] 
        record = {k:args[k] for k in columns if args.get(k)}
        db_result = insert_into_db(resource, record)
        sop_version_id = db_result.get('id')

        timestamp = strftime("%Y-%m-%dT%H:%M:%S")

        blob = CloudStorage.get_blob('{0}/sops/{1}/{2}'.format(organization_id, sop_id, timestamp))

        signed_url = blob.generate_signed_url(
        datetime.timedelta(minutes=5),
        method='PUT',
        content_type=args['content_type'])

        print(signed_url)

        db_result['upload_url'] = signed_url
        return db_result

    @requires_auth
    def post(self, current_user, sop_id, organization_id):
        """
        Creates an Sop Version

        :param sop_id: ID of the sop 
        :param description: Description of the sop version

        :returns: An object containing the id of the new sop the corresponding activity's id 
        """
        db_result = self.create_new_version(current_user, sop_id, organization_id)
        
        sop_version_id = db_result.get('id')

        resource = 'sop_versions'
        
        current_user_id = current_user.get('user_id')
        args = prep_args(resource, organization_id, current_user)

        activity_args = {
            'sop_id': sop_id,
            'sop_version_id': sop_version_id,
            'organization_id': organization_id,
            'created_by': args['created_by']
        }
        SopUploadedNewVersion.do_activity(activity_args, current_user)
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
            'sop_version_id': sop_version_id,
            'sop_version_affeted_rows': db_result.get('affected_rows'),
            'upload_url': db_result.get('upload_url')
        })

class SopVersion(Resource):

    # a bit weird since instead of using version_id, this endpoint uses sop_id and version_number
    # (IMO) makes more sense to the user to read a url that is sops/32/versions/3 
    # insetad of sop_versions/58 or sops/32/versions/58 since its not the 58th version but the 3rd
    # thus get_collection with filters is used instead of get_resource since get_resource only takes id

    @requires_auth
    def get(self, current_user, sop_id, version_number, organization_id=None):

        resource = 'vw_sop_versions'

        filters = [('sop_id', '=', sop_id),
                    ('version_number', '=', version_number)]

        collection = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource=resource,
            filters=filters,
            paginate=False)

        # collection should always contain 1 sop
        sop = collection[0]

        # reformat properties for client use
        sop['version_id'] = sop['id']
        del sop['id']

        return sop

class UploadSopVersion(Resource):
    """Uploads version endpoint"""

    @requires_auth
    def get(self, current_user, sop_id, organization_id):
        """
        Get versions list with urls
        @return: object would look; 
        {
            'urls':[
                {
                    'timestamp':'2018-11-21T14:13:39', 
                    'url':'https://storage.googleapis.com/s2s_uploads_dev/1/48/2018-11-21T14%3A13%3A39?'
                }
            ]
        }
        """

        resource = 'uploads'

        db_result = {}

        blob_list = CloudStorage.list_sop_blobs(organization_id, sop_id)

        blobs = []

        for blob_object in blob_list:
            blob = CloudStorage.get_blob(blob_object.name)
            timestamp = blob_object.name.replace(
                "{0}/sops/{1}/".format(organization_id, sop_id), '')
            signed_url = blob.generate_signed_url(
                datetime.timedelta(minutes=5),
                method="GET")
            blobs.append({'url': signed_url, 'timestamp': timestamp})

        db_result['urls'] = blobs
        return jsonify(db_result)
