"""Class to handle requests to merge given lots into one lot"""
from activities.activity_handler_class import ActivityHandler
from db_functions import insert_into_db, DATABASE, select_from_db, update_resource_attribute_into_db
from class_errors import ClientBadRequest
from activities.create_lot import CreateLot
from activities.update_room import UpdateRoom

import psycopg2

class MergeLot(ActivityHandler):
    """Action to merge given lots"""
    required_args = {
        'name',
        'to_room',
        'varieties',
        'lots_to_merge',
        'source_batches',
        'organization_id',
        'created_by',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new lot and merge all the given lots into the new lot"""
        cls.check_required_args(args)
        lot_required_args = {
            'to_qty',
            'from_qty',
            'from_inventory_id',
            'from_inventory_name',
            'variety',
            'to_qty_unit',
            'from_qty_unit',
            'timestamp'
            }

        merging_product_types = set()

        for lot in args['lots_to_merge']:
            if not lot_required_args.issubset(lot):
                raise ClientBadRequest({
                    "code": "merge_lot_missing_lot_data",
                    "description": "Lots being merged must have the following fields: {0}".
                                   format(", ".join(lot_required_args))
                }, 400)


            if lot['from_qty'] != lot['to_qty']:
                raise ClientBadRequest({
                    "code": "merge_lot_qty_mismatch",
                    "description": "Lots being merged with same unit type must have same qty ({0} != {1})".
                                   format(lot['from_qty'], lot['to_qty'])
                }, 400)

            if not all({'id', 'name'}.issubset(variety_args.keys()) for variety_args in args['varieties']):
                raise ClientBadRequest({
                    "code": "merge_lot_missing_variety_id",
                    "description": "Lots being merged must have variety id and name"
                }, 400)
            merging_product_types = merging_product_types.union({lot['from_qty_unit']})

       

        try:
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

            merged_lot_ids = lambda lots: (lot['from_inventory_id'] for lot in lots)

            merged_lot_from_qty = sum(map(lambda lot: lot['from_qty'], args['lots_to_merge']))

            merged_lot_to_qty = sum(map(lambda lot: lot['to_qty'], args['lots_to_merge']))

            merged_lot_unit = args['lots_to_merge'][0]['from_qty_unit']

            create_lot_activity_data = {
                'name': 'create_lot',
                'variety': variety_name,
                'variety_id': variety_id,
                'to_room': args.get('to_room'),
                'from_inventory_id': list(set(merged_lot_ids(args['lots_to_merge']))),
                'merged_inventories': list(set(merged_lot_ids(args['lots_to_merge']))),
                'from_qty': merged_lot_from_qty,
                'to_qty': merged_lot_to_qty,
                'to_qty_unit': merged_lot_unit,
                'from_qty_unit': merged_lot_unit,
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp']
            }
            create_lot_result = CreateLot.do_activity(create_lot_activity_data, {})

            inventory_id = create_lot_result['inventory_id']

            result = {"new_inventory_id": inventory_id, "activity_id": []}
            for lot in args['lots_to_merge']:
                lot['name'] = args['name']
                lot['to_inventory_id'] = inventory_id
                lot['organization_id'] = args['organization_id']
                lot['created_by'] = args['created_by']
                lot['timestamp'] = args['timestamp']
                activity_result = cls.insert_activity_into_db(lot)
                result['activity_id'].append(activity_result["id"])

            if 'oil_density' in args:
                update_resource_attribute_into_db(
                    'inventories', inventory_id, 'g/ml-oil', args['oil_density'])
            DATABASE.dedicated_connection().commit()
            return result
        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest({
                "code": "merge_lot_error",
                "message": "There was an error merging lot. " + error.args[0]
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
        