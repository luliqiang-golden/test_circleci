import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))



from db_functions import select_from_db
from labels.class_label_base_nicelabel import LabelBaseNiceLabel
import json

class InventoryLabelNiceLabel(LabelBaseNiceLabel):

    def _select_data(self, table_name, object_id, organization_id):

        params = {'organization_id': organization_id, 'table_name': table_name, 'object_id':object_id}

        query = """
            select t1.* ,
                   round((t1.total_cbd_level * t1.lot_item_qty)/t1.initial_lot_qty, 2) as cbd_level,
                   round((t1.total_thc_level * t1.lot_item_qty)/t1.initial_lot_qty, 2) as thc_level
            from (
                select i.name, 
                        i.timestamp as packaged_date,  
                        s.attributes->>'gtin_14' as gtin14,
                        (f_serialize_stats(i.stats)).qty as lot_item_qty,
                        (select sum(cast(a_lot.data->>'to_qty'as decimal)) 
                        from activities a_lot 
                        where a_lot.name = 'transfer_inventory' and 
                                cast(a_lot.data->>'to_inventory_id' as bigint) = i_lot.id) as initial_lot_qty,
                        cast(i_lot.attributes->>'cbd_ratio' as decimal) as total_cbd_Level, 
                        cast(i_lot.attributes->>'thc_ratio' as decimal) as total_thc_level
                from inventories as i 
                inner join activities as a on a.name = 'create_lot_item' and cast(a.data->>'inventory_id' as bigint) = i.id
                inner join inventories as i_lot on i_lot.id = cast(a.data->>'from_inventory_id' as bigint) 
                inner join skus as s on s.id = cast(i.data->>'sku_id' as bigint)
                where i.type ='lot item' and 
                        i.organization_id = %(organization_id)s and
                        i.id = %(object_id)s
                ) as t1
        """

        result = select_from_db(query, params)
        if (result):
            return result[0]
    
    
    def _format_fields(self, data):   
        package = data
        package["packaged_date"] = package["packaged_date"].strftime("%Y-%m-%d") 
        package["name"] = package["name"].title()
        package["number_of_labels"] = self._number_of_labels

        return package

    
     

        