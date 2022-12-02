import os
import base64
import requests
import textract
from google.cloud import storage
from datetime import datetime

from flask import jsonify
from flask_restful import Resource
from resource_functions import get_collection, get_resource
from auth0_authentication import requires_auth
from resource_functions import prep_args
from db_functions import insert_into_db

URL = 'https://www.srfax.com/SRF_SecWebSvc.php'

action_inbox = "Get_Fax_Inbox"
action_retrieve = "Retrieve_Fax"
action_update_status = "Update_Viewed_Status"


class GoogleCloud:

    def __init__(self):
        pass

    @classmethod
    def upload_blob(self, text, bucket_name='sr-fax', destination_blob_name='sr-fax.pdf'):
        """Uploads a file to the bucket."""

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(text, content_type='application/pdf')

        print(
            "File uploaded to {}.".format(
                destination_blob_name
            )
        )
        return


class SRFax:

    def __init__(self, access_id, access_pwd, caller_id=None,
                 sender_email=None, account_code=None, url=None):

        self.access_id = access_id
        self.access_pwd = access_pwd
        self.caller_id = caller_id
        self.sender_email = sender_email
        self.account_code = account_code
        self.url = url or URL

    def verify_parameters(self, params):
        """Verify that dict values are set"""

        for key in params.keys():
            if params[key] is None:
                raise TypeError('%s not set' % (key))

    def get_fax_inbox(self, period='ALL'):
        params = {
            'action': action_inbox,
            'access_id': self.access_id,
            'access_pwd': self.access_pwd,
            'sPeriod': period,
            'sViewedStatus': "UNREAD"
        }
        self.verify_parameters(params=params)
        response = requests.post(url=self.url, json=params)
        result = response.json()
        return result['Result'] if result.get("Status") == 'Success' else result, response.status_code

    def retrieve_fax(self, file_name, dir='IN'):
        fax_detail_id = file_name.split('|')[1]

        params = {
            'action': action_retrieve,
            'access_id': self.access_id,
            'access_pwd': self.access_pwd,
            'sFaxFileName': file_name,
            'sDirection': dir,
            'sFaxDetailsID': fax_detail_id
        }

        self.verify_parameters(params=params)
        response = requests.post(url=self.url, json=params)
        result = response.json()
        return result['Result'] if result.get("Status") == 'Success' else result, response.status_code

    def update_viewed_status(self, file_name, dir='IN', mark_as='Y'):
        fax_detail_id = file_name.split('|')[1]
        params = {
            'action': action_update_status,
            'access_id': self.access_id,
            'access_pwd': self.access_pwd,
            'sFaxFileName': file_name,
            'sDirection': dir,
            'sFaxDetailsID': fax_detail_id,
            'sMarkasViewed': mark_as
        }

        self.verify_parameters(params=params)
        response = requests.post(url=self.url, json=params)
        result = response.json()
        return 200 if result.get("Status") == 'Success' else 400


class BucketUpload(Resource):
    access_id = os.getenv("SRFAX_ACCESS_ID")
    access_pwd = os.getenv("SRFAX_ACCESS_PWD")

    def post(self, organization_id=1):
        try:

            message = "File Uploaded Successfully"
            sr_fax = SRFax(access_id=self.access_id, access_pwd=self.access_pwd)
            inbox_mails, status_code = sr_fax.get_fax_inbox()
            if status_code == 200:
                for fax in inbox_mails:
                    original_file_name = fax.get('FileName')
                    retrieve_fax, status_code = sr_fax.retrieve_fax(file_name=original_file_name)
                    if status_code == 200:
                        filename = fax.get('FileName').replace('|', '_')
                        content = base64.b64decode(retrieve_fax)
                        with open('temp.pdf', 'wb') as file:
                            file.write(content)

                        text = textract.process(
                            'temp.pdf',
                            method='pdftotext'
                        )

                        os.remove('temp.pdf')
                        print(text)

                        srfax_args = {
                            "file_name": fax.get('FileName'),
                            "receive_status": fax.get('ReceiveStatus'),
                            "epoch_time": fax.get('EpochTime'),
                            "date": fax.get('Date'),
                            "caller_id": fax.get('CallerID'),
                            "remote_id": fax.get('RemoteID'),
                            "pages": fax.get('Pages'),
                            "size": fax.get('Size'),
                            "viewed_status": fax.get('ViewedStatus'),
                            "pdf_content": text.decode("utf-8")
                        }

                        insert_into_db(resource='srfax', args=srfax_args)
                        GoogleCloud.upload_blob(text=content, destination_blob_name=f"{datetime.now().strftime('%Y-%m-%d')}/{filename}.pdf")
                        sr_fax.update_viewed_status(file_name=original_file_name)
            else:
                message = inbox_mails['Result']

        except Exception as e:
            message = "File not uploaded {0}".format(str(e))

        return jsonify({"message": message})

    @requires_auth
    def get(self, current_user, organization_id=1):
        return get_collection(
            current_user=current_user,
            organization_id=None,
            resource='srfax')
