
from flask import Blueprint, request
from flask.helpers import make_response
from flask.json import jsonify
from class_errors import ClientBadRequest
from auth0_authentication import requires_auth

import copy
from copy import deepcopy
from app import db
import simplejson as json

from models.activity import Activity
from models.inventory import Inventory
from controllers import BaseController
from serializer.activities.revert_destruction import RevertDestructionsSchemaPostRequest, RevertDestructionsSchemaResponse
from serializer.activity import ActivitiesSchemaGetResponse
from db_functions import execute_query_into_db, select_from_db

revert_destructions_schema_response = RevertDestructionsSchemaResponse()
revert_destructions_schema_post_request = RevertDestructionsSchemaPostRequest()
activities_schema_get_response = ActivitiesSchemaGetResponse()


class RevertDestructionsCollection(BaseController):
    @requires_auth
    def post(self, current_user, organization_id):

        params = self.serialize(revert_destructions_schema_post_request, request.get_json())

        data = {
            'destruction_inventories': params.get('destruction_inventories'),
            'reason_for_reversion': params.get('reason_for_reversion'),
            'witness_1': params.get('witness_1'),
            'witness_2': params.get('witness_2'),
        }

        for destruction_inventory in params.get('destruction_inventories'):
            complete_destruction_activity = self.deserialize_queryset(activities_schema_get_response, Activity.get_complete_destruction_activity_by_id(organization_id,destruction_inventory))[0]
            inventory_adjustment_activity = self.deserialize_queryset(activities_schema_get_response, Activity.get_inventory_adjustment_activity_by_id(organization_id,destruction_inventory))[0]
            destruction_inventory_id = complete_destruction_activity['data']['from_inventory_id']
            destruction_qty = complete_destruction_activity['data']['from_qty']
            destruction_qty_unit = complete_destruction_activity['data']['from_qty_unit']
            self._update_destruction_inventory(destruction_inventory_id, destruction_qty, destruction_qty_unit, True)
            self._delete_from_destroy_material(organization_id, destruction_inventory_id)
            Activity.delete_activities(complete_destruction_activity['id'], organization_id, current_user.get('user_id'), 'complete_destruction', params.get('reason_for_reversion'))
            Activity.delete_activities(inventory_adjustment_activity['id'], organization_id, current_user.get('user_id'), 'inventory_adjustment', params.get('reason_for_reversion'))
        
        revert_activity = Activity.save_activities(organization_id, data, current_user.get('user_id'), 'revert_destrucion')

        response = self.deserialize_object(revert_destructions_schema_response, revert_activity)

        return make_response(jsonify(response), 201)

    
    def _serialize_stats(self, stats):
        '''Serializes stats of inventory'''
        return eval(json.dumps(stats))

    def _update_destruction_inventory(self, destruction_inventory_id, qty, unit, increment = False):
        '''Updates destruction_inventory stats column'''
        destruction_inventory = Inventory.query.get(destruction_inventory_id)    
        destruction_inventory.stats = deepcopy(destruction_inventory.stats)
        destruction_inventory.attributes = deepcopy(destruction_inventory.attributes)

        if (increment):
            with db.session.no_autoflush:
                if unit in ['plants', 'seeds', 'g-wet']:
                    destruction_inventory.stats[unit] = float(destruction_inventory.stats.get(unit)) + float(qty)
                elif unit in ['crude', 'distilled']:
                    destruction_inventory.stats['g-oil'][unit] = float(destruction_inventory.stats.get('g-oil').get(unit)) + float(qty)
                elif unit in ['dry', 'cured']:
                    destruction_inventory.stats['g-dry'][unit] = float(destruction_inventory.stats.get('g-dry').get(unit)) + float(qty)
                else:
                    destruction_inventory.stats['g-extract'] = {unit: float(destruction_inventory.stats.get('g-extract').get(unit)) + float(qty)}
        else:
            with db.session.no_autoflush:
                if unit in ['plants', 'seeds', 'g-wet']:
                    destruction_inventory.stats[unit] = float(qty)
                elif unit in ['crude', 'distilled']:
                    destruction_inventory.stats['g-oil'] = {"crude":0, "distilled":0}
                    destruction_inventory.stats['g-oil'][unit] = float(qty)
                elif unit in ['dry', 'cured']:
                    destruction_inventory.stats['g-dry'] = {"dry":0, "cured":0}
                    destruction_inventory.stats['g-dry'][unit] = float(qty)
                else:
                    destruction_inventory.stats['g-extract'] = {unit: float(qty)}
                
        destruction_inventory.stats = self._serialize_stats(destruction_inventory.stats)
        destruction_inventory.attributes['status'] = 'undestroyed'
        setattr(destruction_inventory, 'attributes', json.loads(json.dumps(destruction_inventory.attributes)))
        db.session.commit()
        return {}
    
    
    def _delete_from_destroy_material(self, organization_id, destruction_inventory_id):

        '''Deletes object from completed_queue_destruction_activities array in destroy_material activity by given destruction_inventory_id'''

        params = {
            "destruction_inventory_id": destruction_inventory_id,
            "organization_id": organization_id
        }

        query = '''

           UPDATE activities

            SET data = jsonb_set(data, '{completed_queue_destruction_activities}', (

                SELECT COALESCE(jsonb_agg(element), '[]'::jsonb)

                FROM jsonb_array_elements(data -> 'completed_queue_destruction_activities') element

                WHERE element ->> 'from_inventory_id' <> '%(destruction_inventory_id)s'

                )

            )

            WHERE 

            id = (SELECT id FROM activities 

                WHERE name ='destroy_material' 

                AND data->'completed_queue_destruction_activities' @> '[{"from_inventory_id": "%(destruction_inventory_id)s"}]')

            AND

            organization_id = %(organization_id)s


        ''' % params

        return execute_query_into_db(query)


# Make blueprint for revert_destructions API
revert_destructions_bp = Blueprint('revert_destructions', __name__)

# Define url_patterns related to revert_destructions API here
revert_destructions = RevertDestructionsCollection.as_view('revert_destructions')
revert_destructions_bp.add_url_rule('/revert-destructions', view_func=revert_destructions, methods=['POST'])