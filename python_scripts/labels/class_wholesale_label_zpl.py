
from datetime import datetime
from labels.class_label_base_zpl import LabelBaseZpl
from db_functions import select_from_db
from class_errors import EngineError
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


class WholesaleLabelZpl(LabelBaseZpl):
    def _get_data(self, table_name, object_id, organization_id):

        params = {'organization_id': organization_id, 'lot_item_id': object_id}

        query = '''
            select lot.id as lot_id, lot_item.id as lot_item_id, lot_item.data->>'sku_name' as sku_name, 
            to_char(act.timestamp, 'YYYY-MM-DD') as harvest_date, to_char(lot_item.timestamp, 'YYYY-MM-DD') as lot_item_creation_date
                from inventories as lot_item
                left join inventories as lot on lot.id = cast(lot_item.data->>'from_inventory_id' as integer) and lot.type='lot' and lot.organization_id = lot_item.organization_id
                left join inventories as batch_mother on concat('"',(cast(batch_mother.id as varchar)),'"') = any(ARRAY(SELECT jsonb_array_elements(case jsonb_typeof(lot.data->'from_inventory_id') when 'array' then lot.data->'from_inventory_id' else '[]' end))::varchar[])
                and batch_mother.type in ('batch','mother') and batch_mother.organization_id = lot.organization_id 
                left join activities as act on cast(act.data->>'inventory_id' as integer) = batch_mother.id and act.name = 'update_stage'  and act.data->>'to_stage'='harvesting' and act.organization_id = batch_mother.organization_id
                left join skus as sku on sku.name = lot_item.data->>'sku_name' and sku.organization_id = lot_item.organization_id and sku.sales_class = 'wholesale'
            where lot_item.type = 'lot item' and lot_item.organization_id = %(organization_id)s and lot_item.id = %(lot_item_id)s 
        '''

        try:
            wholesale_object = select_from_db(query, params)
            result = wholesale_object[0]
            result['current_date'] = datetime.today().strftime('%Y-%m-%d')
            return result
        except:
            raise Exception('Could not find data for this id')
