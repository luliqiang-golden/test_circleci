"""Create a mother plant, transfer plant from batch to mother, transfer mother to mother batch"""

from datetime import datetime
from db_functions import select_from_db
from activities.activity_handler_class import ActivityHandler
from activities.create_mother import CreateMother
from activities.propagate_cuttings import PropagateCuttings
from activities.transfer_inventory import TransferInventory
from activities.transfer_mother_plants_to_mother_batch import TransferMotherPlantsToMotherBatch
from activities.update_room import UpdateRoom

class TransferBatchPlantToMotherBatch(ActivityHandler):
    """Activity for creating a mother from a plant in a batch and moving it to a mother batch"""

    required_args = {
        'name',
        'variety',
        'variety_id',
        'from_inventory_id',
        'to_inventory_id',
        'from_qty',
        'to_qty',
        'recorded_by',
        'approved_by',
        'organization_id',
        'created_by',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a mother plant from either a batch or a received inventory"""

        cls.check_required_args(args)

        for _ in range(int(args['to_qty'])):

            """ create new mother for each plant being transferred """
            create_mother_args = {
                'variety': args['variety'],
                'variety_id': args['variety_id'],
                'name': 'create_mother',
                'created_by' : args['created_by'],
                'organization_id': args['organization_id'],
                'timestamp': args['timestamp'] or datetime.datetime.now(),
            }
            mother_id = CreateMother.do_activity(create_mother_args, current_user)

            if args['from_qty'] != 0:

                """ transfer a single plant to the newly created mother """
                transfer_plant_args = {
                    'name': 'transfer_inventory',
                    'to_inventory_id': mother_id['inventory_id'],
                    'from_inventory_id': args['from_inventory_id'],
                    'to_qty_unit': 'plants',
                    'from_qty_unit': 'plants',
                    'to_qty': 1,
                    'from_qty': 1,
                    'organization_id': args['organization_id'],
                    'created_by': args['created_by'],
                    'mother_type': 'plants',
                    'timestamp': args['timestamp'] or datetime.datetime.now(),
                }
                TransferInventory.do_activity(transfer_plant_args, current_user)

            else:
                propagate_cuttings_data = {
                    'name': 'propagate_cuttings',
                    'to_inventory_id': mother_id['inventory_id'],
                    'from_inventory_id': args['from_inventory_id'],
                    'to_qty': 1,
                    'to_qty_unit': 'plants',
                    'organization_id': args['organization_id'],
                    'created_by': args['created_by'],
                    'timestamp': args['timestamp'] or datetime.datetime.now(),
                }
                PropagateCuttings.do_activity(propagate_cuttings_data, current_user)

            """ Transfer each mother to the appropriate mother batch """
            transfer_mother_args = {
                'name' : 'transfer_mother_plants_to_mother_batch',
                'to_inventory_id' : args['to_inventory_id'],
                'from_inventory_id' : mother_id['inventory_id'],
                'organization_id': args['organization_id'],
                'created_by': args['created_by'],
                'timestamp': args['timestamp'] or datetime.datetime.now(),
            }

            TransferMotherPlantsToMotherBatch.do_activity(transfer_mother_args, current_user)

            mother_batch = get_mother_batch_room(args["organization_id"], args['to_inventory_id'])
            
            update_mother_room_args = {
                "name": "update_room",
                "organization_id": args['organization_id'],
                "created_by": args['created_by'],
                "inventory_id": mother_id['inventory_id'],
                "to_room": mother_batch['attributes']['room'],
                "timestamp": args['timestamp'] or datetime.datetime.now(),
            }

            UpdateRoom.do_activity(update_mother_room_args, {})


        result = cls.insert_activity_into_db(args)

        return {
            "activity_id": result["id"]
        }



def get_mother_batch_room(organization_id, mother_batch_id):
    """ function to get mother batch data """
    params = {'organization_id': organization_id, 'id' : mother_batch_id}

    query = '''
    SELECT *
    FROM inventories AS i
    WHERE i.organization_id = %(organization_id)s AND i.id = %(id)s
    '''

    mother_batch_object = select_from_db(query, params)
    return mother_batch_object[0]
