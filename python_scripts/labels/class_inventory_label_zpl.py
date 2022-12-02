import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


from stats.class_stats import Stats
from labels.class_label_base_zpl import LabelBaseZpl
import json

class InventoryLabelZpl(LabelBaseZpl):
    def _format_fields(self, data):   
        inventory = data  
        inventory["timestamp"] = inventory["timestamp"].strftime("%Y-%m-%d") 
        inventory["type"] = inventory["type"].title()
       
        serialized_stats = Stats.serialize_stats(inventory["stats"])
        
        singular_units = ['seeds' ,'plants', 'g-wet']

        if serialized_stats["unit"] in singular_units:
            inventory["unit"] = "{0} {1}".format(serialized_stats["qty"], serialized_stats["unit"])
        else:
            inventory["unit"] = "{0} {1}-{2} {3}".format(
            serialized_stats["qty"], serialized_stats["metric_mass"], serialized_stats["type"], serialized_stats["unit"])

        if (inventory["attributes"].get("room")):
            inventory["room"] = inventory["attributes"]["room"]
        else:
            inventory["room"] = "No Room"

        return inventory

            
     

        