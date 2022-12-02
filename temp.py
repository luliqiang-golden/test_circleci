"""Script for testing during development"""
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "python_scripts"))

from db_functions import select_from_db

# from rule_validators.stage_validation import validate

# to_sum = db_functions.select_inventory_sum(organization_id, 'to', inventory_id,
#                                            'g-dry') or 0

# from_sum = db_functions.select_inventory_sum(organization_id, 'from',
#                                              inventory_id, 'g-dry') or 0

# print(to_sum, from_sum, to_sum - from_sum)

# condition = {
#     'condition_type': 'stage_validation',
#     'inventory_id_field': 'inventory_id',
#     'field': 'to_stage'
# }

# args = {'organization_id': 1, 'inventory_id': 16,
#         'to_stage': 'propagation'}

# validate(condition, args)



query = '''
    select act.*
    from inventories as inv
    left join activities as act
        on cast(act.data->>'inventory_id' as numeric) = cast(inv.id as numeric) 
            or cast(act.data->>'to_inventory_id' as numeric) = cast(inv.id as numeric) 
            or cast(act.data->>'from_inventory_id' as numeric) = cast(inv.id as numeric) 
            or cast(act.data->>'related_inventory_id' as numeric) = cast(inv.id as numeric)
    -- 	left join signatures as sig
    -- 		on sig.activity_id = act.id
    where inv.id in (863)
    order by act.id asc
    '''
result = select_from_db(query)
arr = []
for res in result:
    arr.append(res['id'])
print(arr)