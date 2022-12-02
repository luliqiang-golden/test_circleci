"""Class for batch, variety and greenhouse projected yields"""
from collections import Counter, defaultdict
from datetime import timedelta
from flask import jsonify
from flask_restful import Resource
from decimal import Decimal
from datetime import datetime
from stats.class_stats import Stats
from db_functions import (
    select_resource_from_db,
    get_total_plants_from_db,
    get_total_qty_from_db,
    get_total_units_from_db,
    get_final_yield_from_db,
    get_latest_yield_from_db,
    get_all_batches_from_db,
    get_incomplete_batches_from_db
)
from auth0_authentication import requires_auth
from resource_functions import prep_filters

def calculate_total_qty(data, return_days=None):
    """Calculates the total quantity from a list of activities

    Arguments:
        data {list} -- List containing activities to calculate total quantity for

    Returns:
        Decimal -- Total quantity of the list of activities
    """

    total = 0
    difference = 0
    for activity in data:
        if 'to_qty' not in activity:
            continue
        if 'name' in activity and activity['name'] != 'queue_for_destruction':
            add_qty = activity['to_qty']
            total += float(add_qty)
        else:
            reduce_qty = activity['to_qty']
            total -= float(reduce_qty)

        if 'batch_created' in activity:
            difference += (activity['batch_completed'] - activity['batch_created']).seconds

    if return_days and len(data)>0:
        return (total, difference/len(data))
    return total

def get_batch_yield(organization_id, variety, stage, batch_id, record_activity_name):

    batch_yield = get_latest_yield_from_db(
        organization_id=organization_id,
        variety=variety,
        stage=stage,
        batch_id=batch_id,
        activity_name=record_activity_name
    )

    return batch_yield

def get_variety_units(organization_id, variety, start_type, end_type, stage):

    variety_units_added = get_total_units_from_db(
        organization_id=organization_id,
        variety=variety,
        start_type=start_type,
        end_type=end_type,
        stage=stage,
        units_added=True
    )

    variety_units_reduced = get_total_units_from_db(
        organization_id=organization_id,
        variety=variety,
        start_type=start_type,
        end_type=end_type,
        stage=stage,
        units_added=False
    )

    return (variety_units_added, variety_units_reduced)
# this class is not being used, so im not going to touch it.
class HistoricYield(Resource):
    """Class that is responsible for historic yield requests for the organization

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """

    @requires_auth
    def get(self, current_user, organization_id):
        """Calculates the historic yield for the organization

        Arguments:
            current_user {dict} -- Current user that is querying the API
            organization_id {int} -- Organization id that is being queried on

        Returns:
            flask.Response -- A response containing the projected yield as a json
        """

        filters = []
        filters += prep_filters()

        production_type = None
        varieties = None
        for ftr in filters:
            if ftr[0] == 'production_type':
                production_type = ftr[2]
            elif ftr[0] == 'varieties':
                varieties = ftr[2].split("|")

        units = None
        if production_type == 'dry':
            units = 'g-dry'
        elif production_type == 'oil':
            units = 'g-oil'

        final_yields = get_final_yield_from_db(
            organization_id=organization_id,
            varieties=varieties,
            units=units
        )

        historic_yields = []
        for yld in final_yields:
            dry_yield = 0
            oil_yield = 0
            if yld['to_qty_unit'] == 'g-dry':
                dry_yield = yld['to_qty']
            elif yld['to_qty_unit'] == 'g-oil':
                oil_yield = yld['to_qty']

            batch_yield = {
                'id': yld['to_inventory_id'],
                'variety': yld['variety'],
                'dry_yield': dry_yield,
                'oil_yield': oil_yield,
                'end_date': yld['timestamp']
            }

            historic_yields.append(batch_yield)

        return jsonify({"yields": historic_yields})

class BatchYield(Resource):
    """Class that is responsible for batch yield requests

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """

    @requires_auth
    def get(self, current_user, organization_id, batch_id):
        """Calculates/Fetches the projected yield for a given batch

        Arguments:
            current_user {dict} -- Current user that is querying the API
            organization_id {int} -- Organization id that is being queried on
            batch_id {int} -- Batch id to get actual/projected yield for

        Returns:
            flask.Response -- A response containing the projected yield as a json
        """

        resource = 'Inventories'
        stats_class = Stats(organization_id)

        inventory = select_resource_from_db(resource, batch_id, organization_id)
        if not inventory:
            response = {"type": "projected", "yield": None}
            return jsonify(response)

        start_type = inventory['plan']['start_type']
        end_type = inventory['plan']['end_type']

        serialized_stats = Stats.serialize_stats(inventory['stats'])
        stats_obj = stats_class.get_stats_object_by_name(serialized_stats['unit'])
        stats_end_type =  stats_class.get_stats_object_by_name(end_type)

        variety = inventory['variety']
        batch_id = inventory['id']
        record_activity_name = stats_obj['activity']
        stage = stats_end_type['stages'][-1]

        total_units = serialized_stats["qty"]
        
        batch_plants = total_units

        # check the yield of the current batch
        batch_yield = get_batch_yield(organization_id, variety, stage, batch_id,
                        record_activity_name)
        if batch_yield:
            response = {"type": "projected", "yield": None}
            return jsonify(response)

        # projected yield
        else:
            # check the total units present in a variety 
            variety_units_added, variety_units_reduced = get_variety_units(organization_id, variety,
                start_type, end_type, stage)

            # get the total yield for this variety 
            variety_yield = get_latest_yield_from_db(
                organization_id=organization_id,
                variety=variety,
                stage=stage,
                activity_name=record_activity_name
            )

            # Return undefined yield if there are no units or yield for the variety, or no units
            #  for the batch
            if not variety_units_added or not variety_yield or not batch_plants:
                return jsonify({
                    "yield": None,
                    "type": "projected"
                })

            variety_units_added = calculate_total_qty(variety_units_added)
            variety_units_reduced = calculate_total_qty(variety_units_reduced)

            # remove the units destroyed to get an accurate projected yield
            variety_units = variety_units_added - variety_units_reduced

            variety_yield = calculate_total_qty(variety_yield)

            yield_per_plant = variety_yield / variety_units

            return jsonify({
                "type": "projected",
                "yield": round(yield_per_plant * float(batch_plants), 2)
            })

class VarietyYield(Resource):
    """Class that is responsible for variety yield requests

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """

    @requires_auth
    def get(self, current_user, organization_id, variety):
        """Calculates/Fetches the projected yield for a given variety

        Arguments:
            current_user {dict} -- Current user that is querying the API
            organization_id {int} -- Organization id that is being queried on
            variety {str} -- Variety to calculate yield for

        Returns:
            flask.Response -- A response containing the projected yield as a json
        """

        filters = []
        filters += prep_filters()

        production_type = None
        for f in filters:
            if f[0] == 'production_type':
                production_type = f[2]

        units = None
        if production_type == 'dry':
            units = 'g-dry'
        elif production_type == 'oil':
            units = 'g-oil'

        total_plants = get_total_plants_from_db(
            organization_id=organization_id,
            variety=variety,
            production_type=production_type
        )

        final_yield = get_final_yield_from_db(
            organization_id=organization_id,
            variety=variety,
            units=units
        )

        if not total_plants or not final_yield:
            return jsonify({"yield_per_plant": None})

        variety_plants = calculate_total_qty(total_plants)
        variety_yield = calculate_total_qty(final_yield)

        yield_per_plant = variety_yield / variety_plants

        return jsonify({"yield_per_plant": yield_per_plant})
