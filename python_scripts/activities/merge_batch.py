"""Class to handle requests to merge a batch into another"""
from db_functions import insert_into_db, DATABASE, select_from_db, get_avarage_seed_weight, update_batch_seed_weight, update_resource_attribute_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from activities.create_batch import CreateBatch
from activities.batch_plan_update import BatchPlanUpdate
from activities.update_room import UpdateRoom
from activities.update_stage import UpdateStage
from datetime import datetime

import psycopg2


class MergeBatch(ActivityHandler):
    """Action to merge a batch into another"""

    required_args = {
        'name',
        'to_room',
        'varieties',
        'batch_plan',
        'stage',
        'batches_to_merge',
        'organization_id',
        'created_by',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Merge a batch into another"""
        cls.check_required_args(args)

        batch_required_args = {
            'to_qty',
            'from_qty',
            'from_inventory_id',
            'from_inventory_name',
            'to_qty_unit',
            'from_qty_unit',
            'timestamp',
            }

        merging_product_types = set()

        for batch in args['batches_to_merge']:
            if not batch_required_args.issubset(batch):
                raise ClientBadRequest({
                    "code": "merge_batch_missing_batch_data",
                    "description": "Batches being merged must have the following fields: {0}".
                    format(", ".join(batch_required_args))
                }, 400)

            if batch['from_qty'] != batch['to_qty']:
                raise ClientBadRequest({
                    "code": "merge_batch_qty_mismatch",
                    "description": "Batches being merged with same unit type must have same qty ({0} != {1})".
                    format(batch['from_qty'], batch['to_qty'])
                }, 400)

            if not all({'id', 'name'}.issubset(variety_args.keys()) for variety_args in args['varieties']):
                raise ClientBadRequest({
                    "code": "merge_batch_missing_variety_id",
                    "description": "Batches being merged must have variety id and name"
                }, 400)
            merging_product_types = merging_product_types.union({batch['from_qty_unit']})

        try:
            DATABASE.dedicated_connection().begin()
            if len(args['varieties']) == 1:
                variety_name = args['varieties'][0]['name']
                variety_id = args['varieties'][0]['id']
            else:
                variety_ids = lambda varieties: (variety['id'] for variety in varieties)
                varieties_data = cls.get_merging_varieties_data(list(variety_ids(args['varieties'])), args['organization_id'])
                variety_name = "-".join(sorted(list(variety['name'] for variety in varieties_data['merged_varieties'])))
                variety_id = cls.get_combined_variety_id(list(variety_ids(varieties_data['merged_varieties'])), args['organization_id'])
                if variety_id is None:
                    taxonomy_id = cls.get_taxonomy_id_for_varieties(args['organization_id'])
                    create_variety_result = cls.create_variety(variety_name, varieties_data, taxonomy_id, args['organization_id'], args['created_by'])
                    variety_id = create_variety_result['id']

            merged_batch_ids = lambda batches: (batch['from_inventory_id'] for batch in batches)
            create_batch_activity_data = {
                'name': 'create_batch',
                'variety': variety_name,
                'variety_id': variety_id,
                'merged_inventories': list(set(merged_batch_ids(args['batches_to_merge']))),
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.datetime.now()
            }
            if "custom_name" in args:
                create_batch_activity_data["custom_name"] = args["custom_name"]
            
            create_batch_result = CreateBatch.do_activity(create_batch_activity_data, {})

            inventory_id = create_batch_result['inventory_id']

            batch_plan_update_data = {
                'name': 'batch_plan_update',
                'plan': args['batch_plan'],
                'inventory_id': inventory_id,
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.datetime.now()
                
            }
            BatchPlanUpdate.do_activity(batch_plan_update_data, {})
            

            update_room_activity_data = {
                'name': 'update_room',
                'to_room': args['to_room'],
                'inventory_id': inventory_id,
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.datetime.now()
            }
            UpdateRoom.do_activity(update_room_activity_data, {})

            update_stage_activity_data = {
                'name': 'update_stage',
                'to_stage': args['stage'],
                'inventory_id': inventory_id,
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.datetime.now()
            }
            UpdateStage.do_activity(update_stage_activity_data, {})

            result = {"new_inventory_id": inventory_id, "activity_id": []}
            total_seed_weight = 0
            for batch in args['batches_to_merge']:
                batch['name'] = 'merge_batch'
                batch['to_inventory_id'] = inventory_id
                batch['organization_id'] = args['organization_id']
                batch['created_by'] = args['created_by']
                activity_result = cls.insert_activity_into_db(batch)
                result['activity_id'].append(activity_result["id"])
                if batch['to_qty_unit'] == "seeds":
                    total_seed_weight += batch['seeds_weight']
            if total_seed_weight > 0:
                update_seed_weight_result = update_batch_seed_weight(batch['to_inventory_id'], total_seed_weight)
                result['seed_weight_updated_rows'] = update_seed_weight_result['affected_rows']
            if 'oil_density' in args:
                update_resource_attribute_into_db(
                    'inventories', inventory_id, 'g/ml-oil', args['oil_density'])
            DATABASE.dedicated_connection().commit()
            return result
        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "merge_batch_error",
                "message": "There was an error merging batch. " + error.args[0]
            }, 500)


    def create_variety(name, varieties_data, taxonomy_id, org_id, user_id):
        """Creates a new variety"""
        taxonomy_options = {
            "organization_id": org_id,
            "created_by": user_id,
            "name": name,
            "taxonomy_id": taxonomy_id,
            'strain': varieties_data['merged_strains'],
            'merged_varieties': varieties_data['merged_varieties']
        }
        return insert_into_db("taxonomy_options", taxonomy_options)

    def get_merging_varieties_data(variety_ids, org_id):
        """Get merged varieties & strain infor for the given varieties"""
        query = "SELECT id, name, ARRAY(SELECT jsonb_array_elements(data->'merged_varieties')) as merged_varieties, ARRAY(SELECT jsonb_array_elements_text(data->'strain')) as strain from taxonomy_options WHERE id = ANY(%(variety_ids)s::bigint[]) AND organization_id=%(organization_id)s"
        taxonomy_options_data = select_from_db(query, {'organization_id': org_id, 'variety_ids': variety_ids})
        variety_combination = []
        distinct_varieties = dict()
        strains = []
        for taxonomy in taxonomy_options_data:
            if taxonomy['merged_varieties']:
                variety_combination.extend(taxonomy['merged_varieties'])
            else:
                variety_combination.append({'id': taxonomy['id'], 'name': taxonomy['name']})
            strains.extend(taxonomy['strain'])
        for variety in variety_combination:
            if variety['id'] not in distinct_varieties:
                distinct_varieties.update({variety['id']: variety})
        return {
            'merged_varieties': list(distinct_varieties.values()),
            'merged_strains': list(set(strains))
        }

    def get_combined_variety_id(variety_ids, org_id):
        """Checks if a given variety combination already exists"""
        query = "SELECT id from taxonomy_options where organization_id=%(organization_id)s and ARRAY(SELECT jsonb_array_elements(data->'merged_varieties')->>'id')::int[] <@ %(variety_ids)s and ARRAY(SELECT jsonb_array_elements(data->'merged_varieties')->>'id')::int[] @> %(variety_ids)s LIMIT 1"
        variety_combination_result = select_from_db(query, {'organization_id': org_id, 'variety_ids': variety_ids})
        return variety_combination_result[0]['id'] if variety_combination_result is not None and len(variety_combination_result) > 0 else None

    def get_taxonomy_id_for_varieties(org_id):
        """Get the taxonomy id for given organization"""
        query = "SELECT id from TAXONOMIES where organization_id=%(organization_id)s and name=%(name)s"
        params = {
            'organization_id': org_id,
            'name': 'varieties'
        }
        taxonomy_result = select_from_db(query, params)
        return taxonomy_result[0]['id']
               