"""Class for activities resources and collections"""

from flask_restful import Resource
from flask import jsonify, request

from resource_functions import get_collection, get_resource
from resource_functions import prep_args

from db_functions import select_from_db, rehydrate_resource

from auth0_authentication import requires_auth
from class_errors import ClientBadRequest

from activities import ACTIVITIES


class Activities(Resource):
    """Class for activities endpoint"""

    # Read all client records
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get a collection of activities"""
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Activities')

    @requires_auth
    def post(self, current_user, organization_id=None):
        """Create a new activity"""
        args = prep_args('Activities', organization_id, current_user)

        if 'name' not in args:
            raise ClientBadRequest({
                "code": "missing_required_fields",
                "message": "Must specify activity name"
            }, 400)

        try:
            module = ACTIVITIES[args['name']]
        except KeyError:
            raise ClientBadRequest({
                "code": "invalid_activity",
                "message": "The specified activity does not exist"
            }, 400)

        result = module.do_activity(args, current_user)

        return jsonify(result)


class Activity(Resource):
    """Class for activity resource endpoint"""

    @requires_auth
    def get(self, current_user, activity_id, organization_id=None):
        """Get a single activity resource"""
        return get_resource(
            current_user=current_user,
            resource_id=activity_id,
            organization_id=organization_id,
            resource='Activities')


class ActivitiesById(Resource):
    """" Class to get all activities associated with an id of a batch or a mother"""

    @requires_auth
    def get(self, current_user, organization_id=None, table_id=None, table_type=None):
        """Get a single activity resource"""
        activities = self.get_activities_by_id(
            organization_id=organization_id,
            table_id=table_id,
            table_type=table_type)
        
        activity_ids_str = self.get_activity_ids_str(activities)
        
        filter_build = [('id', '=', activity_ids_str)]

        results = get_collection(current_user=current_user, organization_id=organization_id, resource='activities', filters=filter_build)

        return results

    def get_activities_by_id(self, organization_id=None, table_id=None, table_type=None):
        str_table_id = '"{}"'.format(table_id)
        if table_type == 'inventory_item':
            params = {'str_table_id': str_table_id, 'organization_id': organization_id, 'table_id': table_id}

            # query searches for ids as a string and a number because activities enter in ids inconsistently
            query = '''
                SELECT * 
                FROM activities As a
                WHERE (a.data->'batch' @> %(str_table_id)s or a.data->'mother' @> %(str_table_id)s 
                or a.data->>'inventory_id' = %(table_id)s or a.data->>'inventory_id' = %(str_table_id)s
                or a.data->>'to_inventory_id' = %(table_id)s or a.data->>'to_inventory_id' = %(str_table_id)s 
                or ARRAY(SELECT jsonb_array_elements(case jsonb_typeof(a.data->'from_inventory_id') when 'array' then a.data->'from_inventory_id' else a.data->'from_inventory_id' || '[]' end))::varchar[] && ARRAY[%(table_id)s, %(str_table_id)s]::varchar[]
                or a.data->>'linked_inventory_id' = %(table_id)s or a.data->>'linked_inventory_id' = %(str_table_id)s
                or a.data->>'related_inventory_id' = %(table_id)s or a.data->>'related_inventory_id' = %(str_table_id)s) 
                and organization_id = %(organization_id)s
                order by a.timestamp DESC
                '''
        if query:
            results = select_from_db(query, params)
            results = [rehydrate_resource(row) for row in results]

            return results
    
    @staticmethod
    def get_activity_ids_str(activities_array):
        result_ids_array = []
        for activity in activities_array:
            result_ids_array.append(activity['id'])
        return '|'.join( result_ids_array)

class MothersInventoryFromMotherBatch(Resource):
    """" Class to get all mothers in a mother batch """
    @requires_auth
    def get(self, request, mother_batch_id, organization_id=None):

        params = {}
        params['organization_id'] = organization_id
        params['mother_batch_id'] = mother_batch_id

        query = '''
        select * from activities
        where organization_id = %(organization_id)s and name = 'transfer_mother_plants_to_mother_batch' and data->>'to_inventory_id' = %(mother_batch_id)s
        order by id
        limit 
        (select count(*) from activities where name = 'transfer_mother_plants_to_mother_batch' and data->>'to_inventory_id' = %(mother_batch_id)s)-
        (select count(*) from inventories where type = 'destruction inventory' and data->>'from_inventory_id' = %(mother_batch_id)s)
        '''
        result = None
        if query:
            result = select_from_db(query, params)
        
        return result




class ActivitiesByInventory(Resource):

    """Class for activities related to an inventory endpoint"""

    @requires_auth
    def get(self, current_user, inventory_id, parent = 'false', organization_id=None):

        """Get a collection of activities based on an inventory"""

        parent_query = ""
        if (eval(parent.title())):
            parent_query = self.get_parent_query(inventory_id, parent_query)

        query =  """
        select * from (
            {0}
            select act.* 
            from f_activities_from_inventory({1}) as act
        ) as t1
        """.format(parent_query, inventory_id)

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            query=query,
            paginate=True,
            where=False,
            resource='Activities')

    def get_parent_query(self, inventory_id, parent_query):
        '''Returns parent query'''

        param = {"inventory_id": int(inventory_id)}
        activity_name_by_inv_type = {
            'lot item': 'create_lot_item',
            'lot': 'create_lot',
            'batch': 'split_batch'
        }
        query = """
            select 
                case 
                    when jsonb_typeof(a.data->'from_inventory_id') = 'array' then a.data->'from_inventory_id'
                    else to_jsonb(array[a.data->>'from_inventory_id']::varchar[])
                end parent_ids,
                a.timestamp 
            from f_activities_from_inventory(%(inventory_id)s) as a
            where a.name in ('split_batch', 'create_lot', 'create_lot_item')
        """
        result = select_from_db(query=query, params=param)
        current_inventory_type = self.get_current_inventory_type(param["inventory_id"])
        if (result):
            result = result[0]
            parent_ids = result["parent_ids"]
            parent_timestap = result["timestamp"]
            for parent_id in parent_ids:
                parent_query += """
                    select act_parent.* 
                    from f_activities_from_inventory({0}) as act_parent
                    where act_parent.timestamp < '{1}' and {0} > 0
                    and act_parent.name <> '{2}'
                    union
                """.format(parent_id, parent_timestap, activity_name_by_inv_type[current_inventory_type])
        return parent_query

    def get_current_inventory_type(self, inventory_id):
        '''Returns inventory type based on given inventory_id'''

        query = """select * from inventories where id={0}""".format(inventory_id)
        result = select_from_db(query=query)[0]["type"]
        return result

