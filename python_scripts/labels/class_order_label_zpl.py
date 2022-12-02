import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


from class_errors import EngineError
from db_functions import select_resource_from_db
from labels.class_label_base_zpl import LabelBaseZpl
import json

class OrderLabelZpl(LabelBaseZpl):
    def _get_data(self, table_name, object_id, organization_id):        
        order = super()._get_data(table_name, object_id, organization_id)                
        order['address'] = order['shipping_address']['address1']
        order['city'] = order['shipping_address']['city']
        order['province'] = order['shipping_address']['province']
        order['postalCode'] = order['shipping_address']['postalCode']
        order['country'] = order['shipping_address']['country']
        return order
     

        