# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

from random import choice, randint, sample
from db_functions import DATABASE, insert_into_db
from utilities import get_random_date_before_today, update_timestamp

from constants import USER_ID
from activities.create_sku import CreateSKU


def create_skus(org_id, batch_varieties):

    timestamp =  get_random_date_before_today(60, 90)
    # random_quantities = sample(range(50), len(batch_varieties))
    for variety in batch_varieties:
        sku_qty = randint(5, 20)
        sku_name = "{}-{}-{}".format(variety, sku_qty, 'dry')
        target_qty_unit = "dry"
        cannabis_class = "dry cannabis"
        create_sku(org_id, sku_name, variety, cannabis_class, sku_qty, target_qty_unit, timestamp)

    for variety in batch_varieties:
        sku_qty = randint(5, 30)
        sku_name = "{}-{}-{}".format(variety, sku_qty, 'distilled')
        target_qty_unit = "distilled"
        cannabis_class = "oil cannabis"
        create_sku(org_id, sku_name, variety, cannabis_class, sku_qty, target_qty_unit, timestamp)

def create_sku(org_id, name, variety, cannabis_class, target_qty, target_qty_unit, timestamp):
    sku_data = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "create_sku",
      "variety": variety,
      "sku_name": name,
      "sales_class": 'wholesale',
      "cannabis_class": cannabis_class,
      "target_qty": target_qty,
      "target_qty_unit": target_qty_unit,
      "to_status": "enabled",
    }

    result =  CreateSKU.do_activity(sku_data, {})
    update_timestamp('activities', result["activity_id"], timestamp)
    return result
