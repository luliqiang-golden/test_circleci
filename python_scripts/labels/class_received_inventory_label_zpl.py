import json
from labels.class_inventory_label_zpl import InventoryLabelZpl
from db_functions import select_from_db
from class_errors import EngineError
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


class ReceivedInventoryLabelZpl(InventoryLabelZpl):

    def _select_data(self, table_name, object_id, organization_id):
        params = {'id': object_id, 'organization_id': organization_id}

        query = '''
            select i.*, a.data->>'to_qty' as qty, a.data->>'to_qty_unit' as unit, a.data->>'vendor_name' as vendor_name, 
            a.data->>'vendor_lot_number' as vendor_lot_number, a.data->>'net_weight_received' as weight_recieved,
            a.data->>'weighed_by' as weighed_by, a.data->>'checked_by' as checked_by,
            a.data->>'number_of_pieces' as number_of_pieces
            from inventories i
            inner join activities a on i.id = cast(a.data->>'to_inventory_id' as integer)
            where i.type = 'received inventory'
                and i.id = %(id)s
                and i.organization_id=%(organization_id)s
        '''

        result = select_from_db(query, params)
        if (result):
            return result[0]

    def _format_fields(self, data):
        inventory = super()._format_fields(data)
        inventory["quantity_received"] = inventory["qty"]
        inventory["vendor_name"] = inventory["vendor_name"]
        inventory["vendor_lot_number"] = inventory["vendor_lot_number"]
        inventory["weighed_by"] = inventory["weighed_by"]
        inventory["checked_by"] = inventory["checked_by"]
        if "number_of_pieces" in inventory:
            inventory["number_of_pieces"] = inventory["number_of_pieces"]

        return inventory
