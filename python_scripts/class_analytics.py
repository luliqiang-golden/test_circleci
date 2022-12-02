"""Class for batch/variety analytics"""

import re
from collections import defaultdict
from flask import jsonify, request
from flask_restful import Resource
from db_functions import select_collection_from_db, join_inventories_and_activities_from_db, select_from_db

from auth0_authentication import requires_auth
from resource_functions import prep_filters


class Analytics(Resource):
    """Class that is responsible for analytics requests

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """

    # Activity names for analytics
    activity_names = [
        'metrics_collect_height',
        'metrics_collect_branch_count',
        'metrics_collect_internodal_space',
        'metrics_collect_trichrome_color',
        'metrics_collect_bud_diameter',
        'metrics_collect_bud_density',
        'metrics_collect_bud_moisture',
    ]

    @staticmethod
    def compute_average(activities, prop):
        """Computes the average for a property on a list

        Arguments:
            activities {list} -- Activities to compute average on
            prop {str} -- Property to compute average on

        Returns:
            float -- The computed average for all activities for the specified property
        """

        total = 0
        length = len(activities)

        for elm in activities:
            total += float(elm[prop])

        return total / length

    @staticmethod
    def get_start_activities(filters):
        """Get propagate_cuttings and transfer_inventory activities for a batch or a variety

        Arguments:
            filters {list} -- List of filters (query params) for the request

        Returns:
            dict -- Dictionary containing results of the db query as well as
                    info about the type of request (batch or variety)
        """

        result = {}
        for idx, ftr in enumerate(filters):
            filter_name, _, filter_value = ftr

            if filter_name == 'inventory_id':
                start_activities = join_inventories_and_activities_from_db(
                    inventory_id=filter_value
                )

                result['type'] = 'inventory_id'
                result['data'] = start_activities[0] if start_activities else None

                return result

            elif filter_name == 'variety':
                start_activities = join_inventories_and_activities_from_db(
                    variety=filter_value
                )

                result['index'] = idx
                result['type'] = 'variety'
                result['data'] = start_activities

                return result

        return result

    @staticmethod
    def transform_activity(activity):
        """Mutates activity to only contain necessary columns

        Arguments:
            activity {dict} -- Activity represented as a dictionary
        """

        allowed_keys = [
            'days',
            'name',
            'height',
            'branch_count',
            'internodal_space',
            'bud_diameter',
            'bud_density',
            'bud_moisture',
        ]

        all_keys = activity.keys()
        disallowed_keys = (all_keys - allowed_keys)

        for k in disallowed_keys:
            activity.pop(k)

    @staticmethod
    def calculate_activity_averages(activity_ds):
        """Iterates through a data structure containing activities, calculates averages and transforms activities (remove unnecessary columns)

        Arguments:
            activity_ds {defaultdict} -- Activities data structure which maps activity_name -> days -> list of [activity_name] activities for that day

        Returns:
            list -- Activities that have been averaged and transformed (remove unnecessary columns)
        """

        activities = []
        for metric in activity_ds:
            for days in activity_ds[metric]:
                metric_activities = activity_ds[metric][days]

                match = re.match('metrics_collect_(.*)', metric)
                metric_name = match[1]

                average = Analytics.compute_average(metric_activities, metric_name)

                # Modify a single activity to contain the average
                activity = metric_activities[0]
                activity[metric_name] = str(average)

                # Transform activity to only contain required columns
                Analytics.transform_activity(activity)

                activities.append(activity)

        return activities

    @staticmethod
    def modify_batch_activities(activities, start_activity):
        """Mutates activities to contain a 'days' key which indicates the number
           of days elapsed since the propagate_cuttings or transfer_inventory activity for that batch

        Arguments:
            activities {list} -- A list of activities related to analytics
            start_activity {dict} -- The propagate_cuttings or transfer_inventory activity for the batch
        """

        # This is a dictionary of dictionaries (inner dictionary contains lists as values)
        activity_ds = defaultdict(lambda: defaultdict(list))
        for activity in activities:
            days = (activity['timestamp']-start_activity['timestamp']).days
            activity['days'] = days

            name = activity['name']
            activity_ds[name][days].append(activity)

        # Compute averages when there are multiple metrics per day
        return Analytics.calculate_activity_averages(activity_ds)

    @staticmethod
    def compute_variety_averages(activities, start_activities):
        """Computes averages on activities for a variety and adds a 'days' key
           to each activity indicating the days elapsed from that batch's
           propagate_cuttings or transfer_inventory timestamp to the activity timestamp

        Arguments:
            activities {list} -- Analytics activities for the variety
            start_activities {list} -- propagate_cuttings or transfer_inventory activities for the variety

        Returns:
            list -- Activities that contain averages for the variety
        """

        # Mapping from inventory id to the corresponding propagate_cuttings or transfer_inventory timestamp
        start_activities_dict = {}
        for start_activity in start_activities:
            start_activities_dict[start_activity['to_inventory_id']] = start_activity

        # This is a dictionary of dictionaries (inner dictionary contains lists as values)
        activity_ds = defaultdict(lambda: defaultdict(list))
        for activity in activities:
            if activity['inventory_id'] not in start_activities_dict:
                continue

            start_activity = start_activities_dict[activity['inventory_id']]

            days = (activity['timestamp']-start_activity['timestamp']).days
            activity['days'] = days

            name = activity['name']
            activity_ds[name][days].append(activity)

        # Compute averages for a variety
        return Analytics.calculate_activity_averages(activity_ds)

    @requires_auth
    def get(self, current_user, organization_id):
        """Fetches collection of activities that correspond to analytics

        Arguments:
            current_user {dict} -- Current user that is querying the API
            organization_id {int} -- Organization id that is being queried on

        Returns:
            flask.Response -- A response containing the analytics activities as a json
        """

        resource = 'Activities'

        # Filter to only get metrics related activities
        filters = [('name', '=', '|'.join(self.activity_names))]
        filters += prep_filters()

        per_page = None

        page = request.args.get('page', 1, type=int)

        filtered = self.get_start_activities(filters)
        if not filtered or not filtered['data']:
            return jsonify(page=page, per_page=per_page, total=0, data=[])

        # Queries with the variety filter need to modify the filters
        if filtered['type'] == 'variety':
            index = filtered['index']
            # Remove variety filter from filters
            filters.pop(index)

            # Filter by batch ids which contain the queried variety
            inventory_ids = [inventory['to_inventory_id'] for inventory in filtered['data']]
            filters.append(('inventory_id', '=', '|'.join(map(str, inventory_ids))))

        activities, count = select_collection_from_db(
            resource,
            organization_id,
            page=page,
            per_page=per_page,
            filters=filters,
        )

        if filtered['type'] == 'inventory_id':
            activities = self.modify_batch_activities(activities, filtered['data'])
        elif filtered['type'] == 'variety':
            activities = self.compute_variety_averages(activities, filtered['data'])

        return jsonify(
            page=page, per_page=per_page, total=count['count'], data=activities
        )

class AccountingInventoriesAnalyticsCost(Resource):
    """Class responsible for inventories's costs requests

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """
    @requires_auth
    def get(self, current_user, organization_id, group_by, variety= ''):
        """Fetches collection of invnetories's costs for the current year

        Arguments:
            organization_id {int} -- Organization id that is being queried on
            group_by {varchar} -- group by 'type', 'variety', 
            variety {varchar} -- able to filter by variety           

        Returns:
            flask.Response -- A response containing the analytics activities as a json
        """
        params = { 'org_id': organization_id, 'variety': variety, 'group_by': group_by}
        query = '''
            select 
                case
                    when %(group_by)s = 'type' then t2.type
                    when %(group_by)s = 'variety' then t2.variety 
                    when %(group_by)s = 'variety_stats' then t2.variety_stats
                    when %(group_by)s = 'stats' then t2.stats
                end as description,
                
                sum(t2.amount) as cost from (
                    select t1.*, concat(t1.variety,' - ', t1.stats) as variety_stats from (
                        select inv.type, 
                            inv.variety,
                            f_serialize_stats(inv.stats).unit as stats,
                            coalesce(cast(act.data->>'from_amount' as  float), 0) as amount 
                        from inventories as inv
                        inner join activities as act 
                            on act.name = 'consumable_lot_use_items' and 
                            act.data->>'linked_inventory_id' = cast(inv.id as varchar) and 
                            act.organization_id = inv.organization_id
                        where inv.type in ('lot', 'lot item', 'batch', 'sample', 'mother') and
                            (inv.variety = %(variety)s or %(variety)s = '') and	
                            inv.organization_id = cast(%(org_id)s as int) and
                            date_part('year', act.timestamp) = date_part('year', current_date) 

                    ) as t1
            ) as t2
            group by case
                        when %(group_by)s = 'type' then t2.type
                        when %(group_by)s = 'variety' then t2.variety 
                        when %(group_by)s = 'variety_stats' then t2.variety_stats
                        when %(group_by)s = 'stats' then t2.stats
                    end
        '''
          
        return select_from_db(query, params)
       

class AccountingSupplyAnalyticsCost(Resource):
    """Class responsible for supply's costs requests

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """
    @requires_auth
    def get(self, current_user, organization_id, month):
        """Fetches collection of supply's costs for the current year

        Arguments:
            organization_id {int} -- Organization id that is being queried on
            month {int} -- able to filter by month        

        Returns:
            flask.Response -- A response containing the analytics activities as a json
        """
        params = { 'org_id': organization_id, 'month': month  }
        query = '''
            select * from (
                {main_query}
                order by sum(ta.amount) desc
                limit 5
            ) as t1
            union all
            select 'All others' as type, coalesce(sum(t2.cost),0) as cost from (	
                {main_query}
            ) as t2
            left join (
                    {main_query}
                    order by sum(ta.amount) desc
                    limit 5) as t3 on t2.type = t3.type 
            where t3.type is null
        '''.format(main_query = self.get_main_query_accounting_supply())
        return select_from_db(query, params)

    
    @staticmethod
    def get_main_query_accounting_supply():
        """get the main query for account supply cost
        
        Returns:
            query
        """
        return '''
            	select lower(cs.type) as type, sum(ta.amount) as cost 
                    from consumable_classes as cs
                    inner join consumable_lots as cl on cs.id = cl.class_id
                    inner join transaction_allocations as ta on ta.data->>'consumable_lot_id' = cast(cl.id as varchar) and cs.organization_id = ta.organization_id
                    inner join transactions as trans on trans.id =ta.transaction_id and cs.organization_id = trans.organization_id 
                where date_part('year', ta.timestamp) = date_part('year', current_date) and
                    date_part('month', ta.timestamp) = %(month)s and
                    cs.organization_id = %(org_id)s
                group by lower(cs.type)
        '''


