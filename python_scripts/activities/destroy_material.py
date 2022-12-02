"""Destroy material, completing queued destruction activities"""

from db_functions import select_collection_from_db, update_into_db, select_from_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
from stats.class_stats import Stats


class DestroyMaterial(ActivityHandler):
    """
    Activity to destroy material, completing queued destruction activities

    :param name: Name of the activity
    :param completed_queue_destruction_activities: list of inventories to destroy
    
    :returns: An object containing the activity_id and affected_rows

    :raises: 400 invalid_completed_queue_destruction_activities
    :raises: 400 missing_from_inventory_id
    :raises: 403 destruction_already_completed 
    """

    required_args = {
        'name',
        'completed_queue_destruction_activities',
    }


    @classmethod
    def do_activity(cls, args, current_user):
        """Destroy material, completing queued destruction activities"""

        cls.check_required_args(args)

        # this is all done as a transaction so we can commit the main activity and then test the
        # individual ones, rolling back everything if necessary

        if args['completed_queue_destruction_activities'] == 'destroy all':
            args['completed_queue_destruction_activities'] = cls.get_destroy_all_info(args['organization_id'], cls)
        
        return cls.destroy_material(cls, args)
        


    def get_destroy_all_info(org, cls):
        params = { 'organization_id': org }

        query = '''
            SELECT * 
            FROM inventories As a
            WHERE a.organization_id = %(organization_id)s AND a.attributes->>'status' = 'undestroyed' AND a.type = 'destruction inventory'
            '''
        undestroyed_inv = select_from_db(query, params)
        completed_queue_destruction_activities = []

        for inv in undestroyed_inv:
            stats =  Stats.serialize_stats(inv['stats'])

            completed_queue_destruction_activities.append({
                'from_inventory_id': inv['id'],
                'from_qty': stats['qty'],
                'from_qty_unit': stats['unit'],
                'to_status': 'destroyed',
                })
        
        return completed_queue_destruction_activities



    
    def destroy_material(cls, args) :
        destruction_activity_result = cls.insert_activity_into_db(args)

        activities = args.pop('completed_queue_destruction_activities')

        try:
            activities = [{
                **args,
                **activity,
                'name': 'complete_destruction',             
                'destroy_material_activity_id': str(destruction_activity_result['id']),
            } for activity in activities]
        except TypeError:
            raise ClientBadRequest({
                "code":
                "invalid_completed_queue_destruction_activities",
                "description":
                "completed_queue_destruction_activities must be an array"
            }, 400)

        # throw an error if any of the queued destruction activities have already been completed
        for activity in activities:
            try:
                filters = [
                    (
                        'attributes:status',
                        '=',
                        'destroyed',
                    ),
                    (
                        'id',
                        '=',
                        activity['from_inventory_id'],
                    ),
                ]
            except KeyError:
                raise ClientBadRequest({
                    "code":
                    "missing_from_inventory_id",
                    "description":
                    "from_inventory_id is required for each destruction activity"
                }, 400)

            _, count = select_collection_from_db(
                'inventories', args['organization_id'], filters=filters)

            if count['count'] != 0:
                raise ClientBadRequest({
                    "code":
                    "destruction_already_completed",
                    "description":
                    "Queued destruction item {} has already been completed".format(
                        activity['from_inventory_id'])
                }, 403)

        affected_rows = 0
        for activity in activities:
            activity['destroyed_date'] = args['destroyed_date']
            # Activity handler changes status here
            cls.insert_activity_into_db(activity)
            if not activity['destroyed_date']:                
                raise ClientBadRequest({
                        "code":
                        "complete_destruction_missing_destroyed_date",
                        "description":
                        "destroyed_date is required"
                    }, 403)
            update_db_result = update_into_db('inventories', activity['from_inventory_id'], {'destroyed_date': activity['destroyed_date']})
            affected_rows += update_db_result['affected_rows'];

        return {
            "activity_id": destruction_activity_result["id"],
            "affected_rows": affected_rows,
        }

    