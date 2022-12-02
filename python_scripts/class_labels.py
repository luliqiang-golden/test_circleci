"""Get label functionality"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '\\python_scripts\\labels')
# sys.path.append('C:\\apps\\seed-to-sale-api\\python_scripts\\labels')

from flask import request, Response
from flask_restful import Resource 
import requests

from class_errors import ClientBadRequest
from db_functions import select_resource_from_db
from auth0_authentication import requires_auth

from labels.class_label_factory import LabelFactory

class GetLabel(Resource):
    """Return specified label that client can send to local printer
    """
    @requires_auth
    def get(self, current_user, organization_id, label_id, label_type, label_format,  object_id, number_of_labels = 1, show_number = "False", start_number = 1,  out_of = 1):
        """Gets label by ID, passes it to a label handler, returns the filled-in template
        """
        label_class = LabelFactory.get_instance(label_id, label_type, label_format, object_id, number_of_labels, show_number, start_number, out_of, organization_id)
        label_formatted = label_class.do_formatting()
        return {'template': label_formatted}

        
class PreviewLabel(Resource):

    @requires_auth
    def post(self, current_user, organization_id, dpmm, size):
        url = "http://api.labelary.com/v1/printers/{0}/labels/{1}/0/".format(dpmm, size)
    
        response = requests.post(url, request.data)

        if response.status_code == 200:
            return Response(response=response.content, status=200, content_type="image/png")

        raise ClientBadRequest(
            {
                "code": "label_preview_error",
                "message": "Could not generate the label preview"
            }, 502
        )
