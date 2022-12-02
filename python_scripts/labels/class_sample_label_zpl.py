
from class_errors import EngineError
from db_functions import select_resource_from_db
from labels.class_label_base_zpl import LabelBaseZpl
from labels.class_inventory_label_zpl import InventoryLabelZpl
import json
from stats.class_stats import Stats


class SampleLabelZpl(LabelBaseZpl):
    def _get_data(self, table_name, object_id, organization_id):
        sample = super()._get_data(table_name, object_id, organization_id)
        return sample

    def _format_fields(self, data):
        sample = super()._format_fields(data)
        serialized_stats = Stats.serialize_stats(sample['stats'])

        singular_units = ['seeds' ,'plants', 'g-wet']

        if serialized_stats['unit'] in singular_units:
            sample['unit'] = "{0} {1}".format(serialized_stats['qty'], serialized_stats['unit'])
        else:
            sample['unit'] = "{0} {1}-{2} {3}".format(
            serialized_stats['qty'], serialized_stats['metric_mass'], serialized_stats['type'], serialized_stats['unit'])
        
        sample['sample_created'] = sample['timestamp'].strftime("%Y-%m-%d")

        return sample
