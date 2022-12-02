"""Class for Uploads resources"""

import datetime
from flask_restful import Resource
from flask import jsonify

from db_functions import insert_into_db, update_into_db, select_resource_from_db

from resource_functions import prep_args, get_collection

from auth0_authentication import requires_auth
from class_errors import ClientBadRequest

from cloud_storage import CloudStorage

from time import strftime


class Uploads(Resource):
    """Uploads Collection Endpoints"""

    # def get(self, *args, **kwargs):
    #     abort(405)

    # @requires_auth
    # def get(self, current_user, organization_id=None):
    #     """Read all Upload records"""
    #     return get_collection(
    #         current_user=current_user,
    #         organization_id=organization_id,
    #         resource='Uploads')

    @requires_auth
    def post(self, current_user, organization_id=None):
        """Provision a new upload and get a time-limited upload url"""

        resource = 'Uploads'

        args = prep_args(resource, organization_id, current_user)

        if "content_type" not in args:
            raise ClientBadRequest(
                {
                    "code": "required_field_error",
                    "message": "The 'content_type' field is required"
                }, 400)

        if "name" not in args:
            raise ClientBadRequest(
                {
                    "code": "required_field_error",
                    "message": "The 'name' field is required"
                }, 400)

        allowed_content_types = ['image/jpeg', 'image/png',
                                 'application/pdf', 'application/vnd.ms-excel', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/txt', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']

        if args["content_type"] not in allowed_content_types:
            raise ClientBadRequest({
                "code":
                "content_type_error",
                "message":
                "The '{}' content-type is not permitted".format(
                    args["content_type"])
            }, 400)

        db_result = insert_into_db(resource, args)

        #timestamp = strftime("%Y-%m-%dT%H:%M:%S")

        upload_object = args
        #upload_object['timestamp'] = timestamp

        activity_object = {
            "name": "update_upload",
            "organization_id": organization_id,
            "created_by": args['created_by'],
            "upload_data": upload_object,
            "upload_id": db_result['id'],
            "timestamp": args['timestamp'] or datetime.datetime.now(),
        }

        insert_into_db('Activities', activity_object)

        blob = CloudStorage.get_blob("{0}/{1}/{2}".format(organization_id,
                                                          db_result['id'], args['timestamp'] or datetime.datetime.now()))

        # https://googlecloudplatform.github.io/google-cloud-python/0.20.0/storage-blobs.html#google.cloud.storage.blob.Blob.generate_signed_url
        signed_url = blob.generate_signed_url(
            datetime.timedelta(minutes=5),
            method="PUT",
            content_type=args["content_type"])

        db_result['upload_url'] = signed_url

        # send back the results with the new id
        return jsonify(db_result)

    @requires_auth
    def get(self, current_user, organization_id=None):
        resource = 'Uploads'

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource=resource)


class Upload(Resource):
    """Uploads Resource Endpoints"""

    @requires_auth
    def get(self, current_user, upload_id, organization_id):
        """Get the latest version"""
        resource = 'uploads'
        db_result = select_resource_from_db(
            resource,
            upload_id,
            organization_id,
        )

        blob_list = CloudStorage.list_blobs(organization_id, upload_id)

        timestamps = []

        for blob_object in blob_list:
            timestamps.append(blob_object.name.replace(
                "{0}/{1}/".format(organization_id, upload_id), ''))

        timestamp = max(timestamps)

        blob = CloudStorage.get_blob("{0}/{1}/{2}".format(organization_id,
                                                          db_result['id'], timestamp))

        signed_url = blob.generate_signed_url(
            datetime.timedelta(minutes=5),
            method="GET")

        db_result['url'] = signed_url

        return jsonify(db_result)

    @requires_auth
    def patch(self, current_user, upload_id, organization_id):
        """Update metadata"""

        resource = 'Uploads'

        args = prep_args(resource, organization_id, current_user)

        db_result = update_into_db(resource, upload_id, args)

        activity_object = {
            "name": "update_upload",
            "organization_id": organization_id,
            "created_by": args['created_by'],
            "upload_data": args,
            "upload_id": upload_id
        }

        insert_into_db('Activities', activity_object)
        # send back the results with the new id
        return jsonify(db_result)


class UploadVersions(Resource):
    """Uploads version endpoint"""

    @requires_auth
    def get(self, current_user, upload_id, organization_id):
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
        db_result = {}

        blob_list = CloudStorage.list_blobs(organization_id, upload_id)

        blobs = []

        for blob_object in blob_list:
            blob = CloudStorage.get_blob(blob_object.name)
            timestamp = blob_object.name.replace(
                "{0}/{1}/".format(organization_id, upload_id), '')
            signed_url = blob.generate_signed_url(
                datetime.timedelta(minutes=5),
                method="GET")
            blobs.append({'url': signed_url, 'timestamp': timestamp})

        db_result['urls'] = blobs
        return jsonify(db_result)

    @requires_auth
    def post(self, current_user, upload_id, organization_id):
        """Upload a new version to given upload_id"""
        resource = 'Uploads'

        args = prep_args(resource, organization_id, current_user)

        if "content_type" not in args:
            raise ClientBadRequest(
                {
                    "code": "required_field_error",
                    "message": "The 'content_type' field is required"
                }, 400)

        if "name" not in args:
            raise ClientBadRequest(
                {
                    "code": "required_field_error",
                    "message": "The 'name' field is required"
                }, 400)

        allowed_content_types = ['image/jpeg', 'image/png',
                                 'application/pdf', 'application/vnd.ms-excel', 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']

        if args["content_type"] not in allowed_content_types:
            raise ClientBadRequest({
                "code":
                "content_type_error",
                "message":
                "The '{}' content-type is not permitted".format(
                    args["content_type"])
            }, 400)

        timestamp = strftime("%Y-%m-%dT%H:%M:%S")

        blob = CloudStorage.get_blob("{0}/{1}/{2}".format(organization_id,
                                                          upload_id, timestamp))

        signed_url = blob.generate_signed_url(
            datetime.timedelta(minutes=5),
            method="PUT",
            content_type=args["content_type"])

        db_result = {}
        db_result['upload_url'] = signed_url

        # send back the results with the new id
        return jsonify(db_result)
