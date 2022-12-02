'''This module contains database schema model for for inventory type = lot table'''

from sqlalchemy.sql.functions import func
from models.inventory import Inventory
from sqlalchemy.orm import aliased, reconstructor
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import String

from models.skus import Skus
from models.inventory.lot_item import LotItem
from datetime import datetime
from class_errors import ClientBadRequest
from models.signature import Signature
from models.activity import Activity
from app import db
import simplejson as json
from copy import deepcopy

class Lot(Inventory):
    
    @reconstructor
    def __init__(self):
        
        '''Constructor of this class'''
        setattr(self, 'type', 'lot')
        
    def get_available_lot_items(self, created_by, organization_id, queryparams):
        
        lot_item = aliased(LotItem)

        queryset = (
                Lot.query
                .with_entities(Lot.id.label('lot_id'), 
                               Lot.name.label('lot_name'), 
                               Lot.timestamp.label('lot_timestamp'), 
                               Skus.id.label('sku_id'),
                               Skus.name.label('sku_name'), 
                               func.count().label('count'))
                .join(lot_item, Lot.id == lot_item.data['from_inventory_id'].astext.cast(Integer))
                .join(Skus, Skus.id == lot_item.data['sku_id'].astext.cast(Integer))
                .filter(lot_item.data['order_item_id'] == None)
                .group_by(Lot.id, Lot.name, Skus.id, Skus.name)
                .order_by(Lot.timestamp.asc())
        )

        if queryparams.get('min_timestamp'):
            queryset = queryset.filter(Lot.timestamp>=queryparams.get('min_timestamp'))
        if queryparams.get('max_timestamp'):
            queryset = queryset.filter(Lot.timestamp<=queryparams.get('max_timestamp'))
        if queryparams.get('name'):
            queryset = queryset.filter(Lot.name.like(queryparams.get('name')))
        if queryparams.get('sku_id'):
            queryset = queryset.filter(Skus.id==queryparams.get('sku_id'))
        if queryparams.get('min_items_available'):
            queryset = queryset.having(func.count()>=int(queryparams.get('min_items_available')))

        queryset = queryset.all()

        return queryset


    def map_order_item_to_lots(order_item_quantity, all_lots):
        lots = []
        for data in all_lots:
            if order_item_quantity < data.count:
                lots.append({"id": data.lot_id, "quantity_selected":order_item_quantity})
                order_item_quantity -= order_item_quantity
                break
            else:
                lots.append({"id": data.lot_id, "quantity_selected":data.count})
                order_item_quantity -= data.count

        return order_item_quantity, lots
    
    def transfer_production_to_existing_lot(self, created_by, organization_id, params, inventory_id):
        ''' transfer_to_existing_lot '''

        source_inventory = (
            Inventory.query
            .with_entities(
                Inventory.data['from_inventory_id'].label('from_inventory_id'))
            .filter(
                (Inventory.id == params.get('to_inventory_id')),
                (Inventory.variety == params.get('variety'))
            )
        ).all()

        """ merge arrays using compression """
        source_inventory = [x for xs in source_inventory for x in xs]
    
        if (int(params.get('from_inventory_id')) not in source_inventory):
            raise ClientBadRequest({
                "code":
                "transfer_lot_mismatch_source_inventory",
                "description":
                "Lot transfers must have the same source inventory ({0} not in {1})".
                format(params.get('from_inventory_id'), source_inventory)
            }, 400)
        

        if 'to_qty' in params and 'merged_inventories' not in params:
            transfer_inventory_id = self._transfer_inventory(created_by, organization_id, params, inventory_id, params.get('to_inventory_id'), True)
            Signature.create_signature(transfer_inventory_id,organization_id,created_by,'Weighed By',params.get('weighed_by'), timestamp=params.get('timestamp'))
            Signature.create_signature(transfer_inventory_id,organization_id,created_by,'Checked By',params.get('checked_by'), timestamp=params.get('timestamp'))
            Signature.create_signature(transfer_inventory_id,organization_id,created_by,'Approved By',params.get('approved_by'), timestamp=params.get('timestamp'))

        self._update_stats(params, inventory_id, params.get('to_inventory_id'), True)

        return {
            "inventory_id": params.get('to_inventory_id'),
            "activity_id": transfer_inventory_id
        }


    def transfer_inventory_to_lot(self, created_by, organization_id, params, inventory_id):
        '''Main function to create transfer received inventory'''
        create_lot = self._create_lot(created_by, organization_id, params, inventory_id)
        self._update_room(created_by, organization_id, params, inventory_id)
        if 'to_qty' in params and 'merged_inventories' not in params:
            self._transfer_inventory(created_by, organization_id, params, inventory_id, create_lot.get('inventory_id'))
        Signature.create_signature(create_lot.get('activity_id'),organization_id,created_by,'Weighed By',params.get('weighed_by'), timestamp=params.get('timestamp'))
        Signature.create_signature(create_lot.get('activity_id'),organization_id,created_by,'Checked By',params.get('checked_by'), timestamp=params.get('timestamp'))
        Signature.create_signature(create_lot.get('activity_id'),organization_id,created_by,'Approved By',params.get('approved_by'), timestamp=params.get('timestamp'))
        return create_lot

    def _create_lot(self, created_by, organization_id, params, inventory_id):
        '''Creates lot from recieved inventory'''
        data_field = {"variety_id":  params.get("variety_id"), "from_inventory_id": inventory_id}
        if 'external_product_id' in params:
            data_field['external_product_id'] = params['external_product_id']
        if "merged_inventories" in params:
            data_field["merged_inventories"] = params["merged_inventories"] 
            
        seed_weight = 0
        parent_inventory = Inventory.query.filter(Inventory.id == inventory_id, Inventory.organization_id == organization_id).one_or_none()
        is_seeds = parent_inventory.stats.get('seeds', None)
        if(parent_inventory.type != 'batch' and parent_inventory.type != 'received inventory'):
            raise ClientBadRequest({
                "code": "transfer_lot_mismatch_source_inventory",
                "description": "Source inventory must be a batch or received inventory"
            }, 400)
        if (parent_inventory.type == "batch" and is_seeds):
            seed_weight = float(parent_inventory.attributes['seed_weight'])
        if (parent_inventory.type == "received inventory" and is_seeds):
            seed_weight = float(parent_inventory.data['seed_weight'])        

        inventory = Inventory(
            organization_id = organization_id,
            created_by = created_by,
            type = 'lot',
            variety = params.get("variety"),
            name = self._generate_inventory_name(params),
            attributes = {"room": params["to_room"]} if not is_seeds else {"room": params["to_room"], "seed_weight": seed_weight},	
            data = data_field,
            stats = {},
            timestamp = params.get("timestamp"),
        )
        db.session.add(inventory)
        db.session.commit()
        activity_data = {
            "variety": params.get("variety"),
            "variety_id":params.get("variety_id"),
            "inventory_id": inventory.id,
            "from_inventory_id": inventory_id,
        }
        self._update_stats(params, inventory_id, inventory.id)
        create_lot_activity = Activity.save_activities(organization_id, activity_data, created_by, 'create_lot', timestamp=params.get("timestamp"))
        return {
            "inventory_id": inventory.id,
            "activity_id": create_lot_activity.id
        }

    def _update_room(self, created_by, organization_id, params, inventory_id):
        '''Updates room for lot'''
        update_room_activity_data = {
            "to_room": params.get("to_room"),
            "inventory_id": inventory_id
        }
        update_room_activity_id = Activity.save_activities(organization_id, update_room_activity_data, created_by, 'update_room', timestamp=params.get("timestamp"))
        return update_room_activity_id

    def _transfer_inventory(self, created_by, organization_id, params, inventory_id, to_inventory_id, increment_inv_ajustment = False):
        '''Makes inventory adjustment'''
        if params.get('from_qty_unit') != params.get('to_qty_unit'):
            raise ClientBadRequest({
                "code":
                "transfer_unit_mismatch",
                "description":
                "Inventory transfers must have the same units ({0} != {1})".
                format(params.get('from_qty_unit'), params.get('to_qty_unit'))
            }, 400)
        if (params.get('from_qty') != params.get('to_qty')) and params.get('mother_type') != 'clones':
            raise ClientBadRequest({
                "code":
                "transfer_qty_mismatch",
                "description":
                "Inventory transfers with same unit type must have same qty ({0} != {1})".
                format(params.get('from_qty'), params.get('to_qty'))
            }, 400)
        transfer_inventory_activity_data = {
            "to_qty": params.get("to_qty"),
            "from_qty": params.get("to_qty"),
            "to_qty_unit": params.get("to_qty_unit"),
            "from_qty_unit": params.get("from_qty_unit"),
            "to_inventory_id": to_inventory_id,
            "from_inventory_id":  inventory_id
        }
        transfer_inventory_activity = Activity.save_activities(organization_id, transfer_inventory_activity_data, created_by, 'transfer_inventory', timestamp=params.get("timestamp"))

        if (increment_inv_ajustment):
            Inventory.create_inventory_adjustment(
                organization_id,
                created_by,
                params.get('from_qty_unit'), 
                self._get_available_qty(inventory_id, params.get('from_qty_unit')) - params.get('from_qty'),
                inventory_id,
                'transfer_inventory',
                'received inventory',
                transfer_inventory_activity.id,
                timestamp=params.get('timestamp')
            )
            Inventory.create_inventory_adjustment(
                organization_id,
                created_by,
                params.get('to_qty_unit'), 
                self._get_available_qty(to_inventory_id, params.get('from_qty_unit')) + params.get('from_qty'),
                to_inventory_id,
                'transfer_inventory',
                'lot',
                transfer_inventory_activity.id,
                timestamp=params.get('timestamp')
            )
        else:
            Inventory.create_inventory_adjustment(
                organization_id,
                created_by,
                params.get('from_qty_unit'), 
                self._get_available_qty(inventory_id, params.get('from_qty_unit')),
                inventory_id,
                'transfer_inventory',
                'received inventory',
                transfer_inventory_activity.id,
                timestamp=params.get('timestamp')
            )
            Inventory.create_inventory_adjustment(
                organization_id,
                created_by,
                params.get('to_qty_unit'),
                params.get('to_qty'),
                to_inventory_id,
                'transfer_inventory',
                'lot',
                transfer_inventory_activity.id,
                timestamp=params.get('timestamp')
            )
        return transfer_inventory_activity.id

    def lots_report(self, organization_id, request_args):
        query_set = (Inventory.query.
                     with_entities(Inventory.id.label('ID'),
                                   Inventory.name.label('Name'),
                                   Inventory.variety.label('Variety'),
                                   Inventory.attributes['room'].label('Room'),
                                   Inventory.stats.label('Quantity'),
                                   Inventory.stats.label('Unit')).
                     filter(Inventory.stats != {}).
                     filter(Inventory.type == 'lot').
                     filter(Inventory.organization_id == organization_id).
                     order_by(Inventory.timestamp.desc()))
        if 'id' in request_args:
            query_set = query_set.filter(cast(Inventory.id, String).like(request_args['id']  +'%'))
        if 'variety' in request_args:
            query_set = query_set.filter(Inventory.variety == request_args['variety'])
        query_set = query_set.all()

        formatted_query_set = []

        for entry in query_set:
            _set = {
                'ID': entry['ID'],
                'Name': entry['Name'],
                'Variety': entry['Variety'],
                'Quantity': None,
                'Unit': None,
                'Room': entry['Room'],
            }
            stats = []
            for key_1, value_1 in entry['Unit'].items():
                if isinstance(value_1, dict):
                    for key_2, value_2 in value_1.items():
                        if isinstance(value_2, dict):
                            for key_3, value_3 in value_2.items():
                                stats.append({'unit': key_3, 'quantity': value_3})
                        else:
                            stats.append({'unit': key_2, 'quantity': value_2})
                else:
                    stats.append({'unit': key_1, 'quantity': value_1})

            stats = sorted(stats, key=lambda d: d['quantity'], reverse=True)

            _set['Unit'] = [stat['unit'] for stat in stats][0]
            _set['Quantity'] = [stat['quantity'] for stat in stats][0]
            formatted_query_set.append(_set)

        if 'archive' in request_args and request_args.get('archive') == 'true':
            return formatted_query_set
        else:
            return [f for f in formatted_query_set if f['Quantity'] > 0]

    def _generate_inventory_name(self, params):
        '''Generates inventory name'''
        if params.get('lot_name'):
            return params.get('lot_name')  
        else:
            return "{0}-{1}-{2}".format(params.get("variety"), datetime.now().isocalendar()[1], datetime.now().year % 100)

    def _update_stats(self, params, from_inventory_id, to_inventory_id, increment = False):
        '''Updates stats column value for original and lot inventory'''
        inventory = Inventory.query.get(from_inventory_id)
        unit = params.get('from_qty_unit')
        available_qty = self._get_available_qty(from_inventory_id, unit)
        if params.get('from_qty') > available_qty:
            raise ClientBadRequest({
                "code": "transfer_invalid_qty",
                "description": f"Not enough qty available in stock, please fill qty less than or equal to {available_qty}"
            }, 400)
        self._update_original_inventory_stats(params, inventory, unit)
        self._update_lot_stats(params, to_inventory_id, unit, increment)
        
    
    def _get_available_qty(self, inventory_id, unit):
        '''Returns available quantity of original inventory'''
        inventory = Inventory.query.get(inventory_id)
        if unit in ['plants', 'seeds', 'g-wet', 'purchasedHemp']:
            return float(inventory.stats.get(unit))
        elif unit in ['dry', 'cured']:
            return float(inventory.stats.get('g-dry').get(unit))
        elif unit in ['crude', 'distilled']:
            return float(inventory.stats.get('g-oil').get(unit))
        else:
            return float(inventory.stats.get('g-extract').get(unit))

    def _serialize_stats(self, stats):
        '''Serializes stats of inventory'''
        return eval(json.dumps(stats))

    def _update_original_inventory_stats(self, params, inventory, unit):
        '''Updates original inventory stats column'''
        with db.session.no_autoflush:
            inventory.stats = deepcopy(inventory.stats)
            if unit in ['plants', 'seeds', 'g-wet', 'purchasedHemp']:
                inventory.stats[unit] = float(inventory.stats.get(unit)) - float(params.get('from_qty'))
            elif unit in ['crude', 'distilled']:
                inventory.stats['g-oil'][unit] = float(inventory.stats.get('g-oil').get(unit)) - float(params.get('from_qty'))
            elif unit in ['dry', 'cured']:
                inventory.stats['g-dry'][unit] = float(inventory.stats.get('g-dry').get(unit)) - float(params.get('from_qty'))
            else:
                inventory.stats['g-extract'][unit] = float(inventory.stats.get('g-extract').get(unit)) - float(params.get('from_qty'))
            inventory.stats = self._serialize_stats(inventory.stats)
            db.session.add(inventory)
            db.session.commit()
            affected_rows = 1
            return affected_rows

    def _update_lot_stats(self, params, lot_inventory_id, unit, increment = False):
        '''Updates lot inventory stats column'''
        lot_inventory = Inventory.query.get(lot_inventory_id)    
        lot_inventory.stats = deepcopy(lot_inventory.stats)

        if (increment):
            with db.session.no_autoflush:
                if unit in ['plants', 'seeds', 'g-wet']:
                    lot_inventory.stats[unit] = float(lot_inventory.stats.get(unit)) + float(params.get('to_qty'))
                elif unit in ['crude', 'distilled']:
                    lot_inventory.stats['g-oil'][unit] = float(lot_inventory.stats.get('g-oil').get(unit)) + float(params.get('to_qty'))
                elif unit in ['dry', 'cured']:
                    lot_inventory.stats['g-dry'][unit] = float(lot_inventory.stats.get('g-dry').get(unit)) + float(params.get('to_qty'))
                else:
                    lot_inventory.stats['g-extract'] = {unit: float(lot_inventory.stats.get('g-extract').get(unit)) + float(params.get('to_qty'))}
        else:
            with db.session.no_autoflush:
                if unit in ['plants', 'seeds', 'g-wet']:
                    lot_inventory.stats[unit] = float(params.get('to_qty'))
                elif unit in ['crude', 'distilled']:
                    lot_inventory.stats['g-oil'] = {"crude":0, "distilled":0}
                    lot_inventory.stats['g-oil'][unit] = float(params.get('to_qty'))
                elif unit in ['dry', 'cured']:
                    lot_inventory.stats['g-dry'] = {"dry":0, "cured":0}
                    lot_inventory.stats['g-dry'][unit] = float(params.get('to_qty'))
                else:
                    lot_inventory.stats['g-extract'] = {unit: float(params.get('to_qty'))}
                
        lot_inventory.stats = self._serialize_stats(lot_inventory.stats)
        db.session.add(lot_inventory)
        db.session.commit()
        affected_rows = 1
        return affected_rows
