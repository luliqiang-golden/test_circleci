from flask_restful import Api, Resource
from flask import request, abort, Blueprint, make_response, jsonify
from auth0_authentication import requires_auth
from controllers import BaseController

from models.inventory.batch import Batch
from serializer.batch import *

batch_harvest_whole_plant_schema_post_request = BatchHarvestWholePlantSchemaPostRequest()
batch_harvest_multiple_schema_post_request = BatchHarvestMultipleSchemaPostRequest()
batch_harvest_schema_post_response = BatchHarvestSchemaPostResponse()
batch_merge_harvest_schema_post_request = BatchMergeHarvestSchemaPostRequest()
batch_weight_adjustment_schema_put_request = BatchWeightAdjustmentSchemaPutRequest()
batch_generic_response = BatchGenericResponse()


class RoomBatches(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id):
        
        rooms = request.args.get('rooms')

        result = Batch.get_batches_per_rooms(organization_id, rooms)

        return make_response(jsonify(result), 200)

class GerminateSeeds(Resource):
    @requires_auth
    def post(self, current_user, organization_id, batch_id):
        activity_id=0

        params = request.get_json()
        required_args = ['approved_by', 'recorded_by', 'quantity','timestamp']

        if not all(arg in params for arg in required_args):
            abort(400, description="Missing one of {}".format(', '.join(required_args)))

        batch = Batch.query.get(batch_id)

        if batch is None:
            abort(404, description="Missing batch with id {}".format(batch_id))

        if batch.stats.get('seeds') < params['quantity'] or params['quantity'] < 0:
            abort(403, description='There is more seeds germinated than available')

        if batch.attributes.get('stage') != 'germinating':
            abort(403, description="This batch isn't in the germinating stage")

        return batch.germinate_seed(current_user['user_id'], organization_id, params)

class HarvestWholePlant(BaseController):

    @requires_auth
    def post(self, current_user, organization_id, batch_id):
        params = self.serialize(batch_harvest_whole_plant_schema_post_request, request.get_json())

        batch = Batch.harvest_plant(organization_id, current_user.get('user_id'), 
                                          batch_id, 
                                          params['harvested_quantity'], 
                                          params['checked_by'], 
                                          params['weighed_by'], 
                                          params['approved_by'], 
                                          params['scale_name'],
                                          params['timestamp'])
        
        batch = self.deserialize_object(batch_harvest_schema_post_response, batch)
        
        return make_response(jsonify(batch), 200)

class HarvestMultiple(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id, batch_id):
        
        result = Batch.get_child_inventories_multiple_harvesting_ids(organization_id, batch_id)
        
        batch = self.deserialize_queryset(batch_harvest_schema_post_response, result)
        
        return make_response(jsonify(batch), 200)
    

    @requires_auth
    def post(self, current_user, organization_id, batch_id):

        params = self.serialize(batch_harvest_multiple_schema_post_request, request.get_json())
        
        
        batch = Batch.harvest_multiple(organization_id, current_user.get('user_id'), 
                               batch_id,
                               params['plants_harvested'],
                               params['harvested_quantity'],
                               params['checked_by'],
                               params['weighed_by'],
                               params['approved_by'],
                               params['scale_name'],
                               params['timestamp'])

        
        batch = self.deserialize_object(batch_harvest_schema_post_response, batch)
        
        return make_response(jsonify(batch), 200)

class MergeHarvestMultiple(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id, source_batch_id):
        
        params = self.serialize(batch_merge_harvest_schema_post_request, request.get_json())
        
        batch = Batch.merge_multiple_harvest(organization_id, current_user.get('user_id'), 
                                             source_batch_id,
                                             params['child_batches_ids'],
                                             params['approved_by'],
                                             params['recorded_by'])

        batch = self.deserialize_object(batch_harvest_schema_post_response, batch)
        
        return make_response(jsonify(batch), 200)

    
class WeightAdjustment(BaseController):
    
    @requires_auth
    def put(self, current_user, organization_id, batch_id):
        
        params = self.serialize(batch_weight_adjustment_schema_put_request, request.get_json())
        
        batch = Batch.weight_adjustment(organization_id, current_user.get('user_id'), 
                               batch_id,
                               params['adjusted_weight'],
                               params['approved_by'],
                               params['checked_by'],
                               params['reason_for_modification']
                               )
        
        batch = self.deserialize_object(batch_generic_response, batch)
        
        return make_response(jsonify(batch), 200)

batches_bp = Blueprint('batches', __name__)
api = Api(batches_bp)
api.add_resource(GerminateSeeds, '/<int:batch_id>/germinate-seeds')


harvest_whole_plant_bp = Blueprint('harvest_whole_plant', __name__)
harvest_whole_plant = HarvestWholePlant.as_view('harvest_whole_plant')
harvest_whole_plant_bp.add_url_rule('/<int:batch_id>/harvest_whole_plant', view_func=harvest_whole_plant, methods=['POST'])


harvest_multiple_bp = Blueprint('harvest_multiple', __name__)
harvest_multiple = HarvestMultiple.as_view('harvest_multiple')
harvest_multiple_bp.add_url_rule('/<int:batch_id>/harvest_multiple', view_func=harvest_multiple, methods=['GET', 'POST'])


merge_harvest_multiple_bp = Blueprint('merge_harvest_multiple', __name__)
merge_harvest_multiple = MergeHarvestMultiple.as_view('merge_harvest_multiple')
merge_harvest_multiple_bp.add_url_rule('/<int:source_batch_id>/merge_harvest_multiple', view_func=merge_harvest_multiple, methods=['POST'])


weight_adjustment_bp = Blueprint('weight_adjustment', __name__)
weight_adjustment = WeightAdjustment.as_view('weight_adjustment')
weight_adjustment_bp.add_url_rule('/<int:batch_id>/weight_adjustment', view_func=weight_adjustment, methods=['PUT'])


room_batches_bp = Blueprint('room_batches', __name__)
room_batches = RoomBatches.as_view('room_batches')
room_batches_bp.add_url_rule('/room_batches', view_func=room_batches, methods=['GET'])