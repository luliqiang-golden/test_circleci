"""Validate that a file has been uploaded when an upload ID is supplied"""

from class_errors import EngineError
import db_functions
from cloud_storage import CloudStorage


def validate(condition, args, current_user):
    """
    Validate that an upload actually exists for the given upload id,
    and that the content type matches
    {
        "condition_type": "upload_validation",
        "field": "upload_id",
        "content-type": "image/jpeg" # Optional
    }
    """
    if condition['condition_type'] != "upload_validation":
        raise EngineError({
            "error":
            "upload_validation_condition_error",
            "description":
            'Condition sent to upload_validation handler, but is not a upload_validation condition'
        }, 500)

    if 'field' not in condition:
        raise EngineError({
            "error":
            "upload_validation_condition_error",
            "description":
            "'field' is a required field for upload_validation conditions"
        }, 403)

    if condition['field'] not in args:
        raise EngineError({
            "error":
            "upload_validation_condition_error",
            "description":
            "Attempting to validate '{}' field but it was not found in the activity data".
            format(condition['field'])
        }, 403)

    if 'organization_id' not in args:
        raise EngineError({
            "error":
            "upload_validation_condition_error",
            "description":
            "'organization_id' is a required field for upload_validation conditions"
        }, 403)

    upload_db_resource = db_functions.select_resource_from_db(
        'uploads', args[condition['field']], args['organization_id'])

    if not upload_db_resource:
        raise EngineError({
            "error":
            "upload_validation_upload_error",
            "description":
            "There is no upload {}".format(args[condition['field']])
        }, 403)

    if 'upload_exists' not in upload_db_resource or upload_db_resource['upload_exists'] != 'True':

        blob = CloudStorage.get_blob("{0}/{1}".format(
            upload_db_resource['organization_id'], upload_db_resource['id']))

        if blob.exists():
            args = {
                "upload_exists": True,
                "created_by": current_user['s2s_id'],
                "organization_id": upload_db_resource['organization_id'],
            }
            db_functions.update_into_db('Uploads', upload_db_resource['id'],
                                        args)
        else:
            raise EngineError({
                "error":
                "upload_validation_upload_error",
                "description":
                "There is no file for upload {}".format(
                    args[condition['field']])
            }, 403)
