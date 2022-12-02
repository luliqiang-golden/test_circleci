"""Class for batch, variety and greenhouse projected yields"""
from collections import Counter, defaultdict
from flask import jsonify
from flask_restful import Resource
from db_functions import get_stages_from_db, select_resource_from_db
from auth0_authentication import requires_auth

class BatchStages(Resource):

    start_stats = ['seeds', 'plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled']
    stages = ['germinating', 'propagation', 'harvesting', 'drying', 'curing', 'extracting_crude_oil', 'distilling', 'final_extraction']

    def get_stages_from_type(self, start_type, to_type): 
        # TODO - this entire end point has to be revamped. this if statment checks the new endtypes. 
        if to_type not in self.start_stats:
            return ['planning', 'final_extraction','qa']
        else:
            from_index = self.start_stats.index(start_type)
            to_index = self.start_stats.index(to_type)
            start_stages = None
            if from_index <= 1:
                start_stages = ['propagation', 'vegetation', 'flowering', 'harvesting']
            else:
                start_stages = []
            if from_index == 0: 
                start_stages = ['germinating'] + start_stages
            if from_index == 2:
                start_stages = ['harvesting'] + start_stages
            if from_index == 3:
                start_stages = ['drying'] + start_stages
            start_stages = ['planning'] + start_stages
            if start_type == to_type:
                return ['planning', self.stages[from_index], 'qa']
            elif to_type == 'plants':
                return start_stages + ['qa']
            elif from_index <= 3 and to_index >= 5:
                return start_stages +  self.stages[5 : to_index + 1] + ['qa']
            else:
                return start_stages + self.stages[max(from_index, 3) : to_index + 1] + ['qa']
    
    def compute_stage_lengths(self, activities, start_type, end_type):
        batch_stage_mapping = defaultdict(dict)

        for activity in activities:
            inventory_id = int(activity["inventory_id"])
            timestamp = activity["timestamp"]
            to_stage = activity["to_stage"]

            batch_stage_mapping[inventory_id][to_stage] = timestamp

        default_stages = self.get_stages_from_type(start_type, end_type)
        stage_lengths = Counter()
        stage_counts = Counter()
        ids = batch_stage_mapping.keys()
        for i in ids:
            batch_stages = batch_stage_mapping[i].keys()

            for cur_stage in batch_stages:
                if cur_stage not in default_stages:
                    continue

                index = default_stages.index(cur_stage)
                if index == 0:
                    continue

                prev_stage = default_stages[index-1]
                if prev_stage not in batch_stage_mapping[i]:
                    continue
                delta = batch_stage_mapping[i][cur_stage] - \
                    batch_stage_mapping[i][prev_stage]

                stage_lengths[prev_stage] += delta.days
                stage_counts[prev_stage] += 1

        for stage in stage_counts.keys():
            stage_lengths[stage] /= stage_counts[stage]
            stage_lengths[stage] = int(stage_lengths[stage])

        return stage_lengths

    @requires_auth
    def get(self, current_user, organization_id, batch_id):
        inventory = select_resource_from_db(
            'Inventories', batch_id, organization_id)
        if not inventory:
            return jsonify({"error": "Specified batch does not exist"})

        # Get production type from batch plan
        variety= inventory["variety"]
        start_type = None
        end_type = None
        if "plan" in inventory and isinstance(inventory["plan"], dict):
            start_type = inventory["plan"]["start_type"]
            end_type = inventory["plan"]["end_type"]

        response = {}

        update_stage_activities = get_stages_from_db(
            organization_id=organization_id,
            variety=variety
        )

        stage_lengths = self.compute_stage_lengths(
            update_stage_activities,
            start_type,
            end_type
        )

        response = stage_lengths

        return jsonify(response)
