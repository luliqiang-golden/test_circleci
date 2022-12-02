""" Add fertilizer to plants """

from activities.activity_handler_class import ActivityHandler
from activities.consumable_lot_use_items import ConsumableLotUseItems


class PlantsAddFertilizer(ActivityHandler):
    """ Add fertilizer to plants """

    required_args = {
        'name',
        'inventory_id',
        'water_qty',
        'water_duration',
        'is_nutrients_added',
        'is_ph_modified',
        'added_by',
        'logged_by',
        'organization_id',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Get all nutrients and ph modifiers and call consumable lot use items"""
        cls.check_required_args(args)

        nutrients_consumables_returns = []
        ph_consumables_returns = []

        if args['is_ph_modified']:
            ph_consumables_returns = PlantsAddFertilizer.consumable_lot_use_nutrients_ph(args, args['ph_modifiers'])
        
        if args['is_nutrients_added']:
            nutrients_consumables_returns = PlantsAddFertilizer.consumable_lot_use_nutrients_ph(args, args['nutrients_added'])

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "nutrient_consumables_returns": nutrients_consumables_returns,
            "ph_consumables_returns": ph_consumables_returns,
        }

    @staticmethod
    def consumable_lot_use_nutrients_ph(args, consumable_array):
        consumable_activities_returns = []
        for consumable in consumable_array:

            for consumable_id in consumable['consumableLots']:

                consumable_lot_use_items_data = {
                    'name': 'consumable_lot_use_items',
                    'type': consumable['consumable_object']['type'],
                    'subtype': consumable['consumable_object']['subtype'],
                    'from_consumable_lot_id': consumable_id,
                    'from_amount': consumable['consumableLots'][consumable_id]['amount'],
                    'from_qty': float(consumable['consumableLots'][consumable_id]['qty']),
                    'from_qty_unit': consumable['consumable_object']['unit'],
                    'organization_id': args['organization_id'],
                    'linked_inventory_id': args['inventory_id'],
                    'consumable_class_id': consumable['consumable_object']['id'],
                    'created_by': args['created_by'],
                    'added_by': args['added_by'],
                    'logged_by': args['logged_by'],
                    'timestamp': args['timestamp'],
                }

                consumable_activities_returns.append(ConsumableLotUseItems.do_activity(consumable_lot_use_items_data, {}))
        return consumable_activities_returns
