""" Add IPM to all plants in a room """

from activities.activity_handler_class import ActivityHandler
from db_functions import select_from_db


class PlantsAddIPM(ActivityHandler):
    """ Add IPM to all plants in a room """

    required_args = {
        'organization_id',
        'room',
        'prepared_by',
        'added_by',
        'ipm_subtype',
        'container_qty',
        'container_unit',
        'pest',
        'quantity',
        'qty_unit',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Get all inventories in the room and add to activity"""

        cls.check_required_args(args)
        
        ipm_inventories = cls.get_inventories_by_room(args['organization_id'], args['room'])

        if len(ipm_inventories) == 0:
            raise ClientBadRequest({
                "code":
                "plants_add_ipm_no_inventories",
                "description":
                "There is no inventory in this room"
            }, 400)

        for inv in ipm_inventories:
            if inv['type'] == 'batch':
                if args.get('batch') == None:
                    args['batch'] = []
                
                args['batch'].append(str(inv['id']))

            if inv['type'] == 'mother':
                if args.get('mother') == None:
                    args['mother'] = []
                
                args['mother'].append(str(inv['id']))

            if inv['type'] == 'received inventory':
                if args.get('received inventory') == None:
                    args['received inventory'] = []
                
                args['received inventory'].append(str(inv['id']))
            

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }

    def get_inventories_by_room(org, room):
        params = { 'organization_id': org, 'room': room }

        query = '''
            SELECT * 
            FROM inventories As a
            WHERE a.organization_id = %(organization_id)s AND a.attributes->>'room' = %(room)s AND CAST(a.stats->>'plants' AS decimal)>0
            '''

        return select_from_db(query, params)
