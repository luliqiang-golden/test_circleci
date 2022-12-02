"""Manage our connections to Google Cloud Storage resources"""

from google.cloud import storage
from settings import Settings


class CloudStorage():
    """
    Singleton Class to manage Google Cloud Storage client.
    This will only instantiate a storage client when needed, then reuse it for future requests.
    Usage:

    from cloud_storage import CloudStorage
    myblob = CloudStorage.get_blob('blobname')
    """

    _uploads_bucket_name = Settings.get_setting('UPLOADS_BUCKET')
    _bucket = None

    @staticmethod
    def get_blob(name):
        """Get a blob object for a given name"""
        if not name:
            raise ValueError('Blob name must not be empty')

        if not CloudStorage._bucket:
            CloudStorage._bucket = storage.Bucket(
                storage.Client(), name=CloudStorage._uploads_bucket_name)
        return storage.Blob(name, CloudStorage._bucket)

    @staticmethod
    def list_blobs(organization_id, upload_id):
        bucket_name = storage.bucket.Bucket(
            storage.Client(), name=CloudStorage._uploads_bucket_name)
        return bucket_name.list_blobs(prefix="{0}/{1}/".format(organization_id, upload_id))

    @staticmethod
    def list_sop_blobs(organization_id, sop_id):
        bucket_name = storage.bucket.Bucket(
            storage.Client(), name=CloudStorage._uploads_bucket_name)
        return bucket_name.list_blobs(prefix="{0}/sops/{1}/".format(organization_id, sop_id))
