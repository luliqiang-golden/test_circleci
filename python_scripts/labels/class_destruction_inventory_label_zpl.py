
from labels.class_label_base_zpl import LabelBaseZpl
from labels.class_inventory_label_zpl import InventoryLabelZpl
import json
from db_functions import select_from_db
from stats.class_stats import Stats


class DestructionInventoryLabelZpl(LabelBaseZpl):
    def _select_data(self, table_name, object_id, organization_id):
        params = {'id': object_id, 'organization_id': organization_id}

        query = '''
            select i.*, a.data->>'from_inventory_id' as from_inventory_id,
            a.data->>'to_qty' as qty
            from inventories i
            inner join activities a on i.id = cast(a.data->>'to_inventory_id' as integer)
            where i.type = 'destruction inventory'
                and i.id = %(id)s
                and i.organization_id=%(organization_id)s
        '''

        result = select_from_db(query, params)

        if (result):
            return result[0]

    def _format_fields(self, data):

        destruction_inventory = super()._format_fields(data)

        serialized_stats = Stats.serialize_stats(destruction_inventory['stats'])

        singular_units = ['seeds' ,'plants', 'g-wet']

        if serialized_stats['unit'] in singular_units:
            destruction_inventory['unit'] = "{0} {1}".format(serialized_stats['qty'], serialized_stats['unit'])
        else:
            destruction_inventory['unit'] = "{0} {1}-{2} {3}".format(
            serialized_stats['qty'], serialized_stats['metric_mass'], serialized_stats['type'], serialized_stats['unit'])

        destruction_inventory["from_inventory_id"] = destruction_inventory["from_inventory_id"]

        return destruction_inventory
