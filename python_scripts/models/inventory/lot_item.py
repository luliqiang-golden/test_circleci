"""This module contains database schema model for inventory type = lot item table"""
from datetime import datetime
from sqlalchemy import String
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import String

from models.inventory import Inventory
from app import db
from copy import deepcopy
import simplejson as json
import pytz
from sqlalchemy.orm import reconstructor
from class_errors import ClientBadRequest
from models.activity import Activity
from models.inventory import Inventory
from models.signature import Signature
from models.skus import Skus
from models.taxonomy_options import TaxonomyOptions
from models.user import User
from models.webhook import Webhook



class LotItem(Inventory):
    
    @reconstructor
    def __init__(self):
        
        """Constructor of this class"""
        setattr(self, 'type', 'lot item')
    
    def lot_item_report(self, organization_id, request_args):
        query_set = (Inventory.query.
                     with_entities(Inventory.id.label('ID'),
                                   Inventory.attributes['room'].label('Room'),
                                   Inventory.variety.label('Variety'),
                                   Inventory.data['sku_name'].label('SKU'),
                                   Inventory.data['from_inventory_id'].label('Source Lot'),
                                   Inventory.stats.label('Quantity'),
                                   Inventory.stats.label('Unit')).
                     filter(Inventory.stats != {}).
                     filter(Inventory.type == 'lot item').
                     filter(Inventory.organization_id == organization_id))
        
        if 'id' in request_args:
            query_set = query_set.filter(cast(Inventory.id, String).like(request_args['id']  +'%'))
        if 'variety' in request_args:
            query_set = query_set.filter(Inventory.variety == request_args['variety'])
        if 'from_inventory_id' in request_args:
            query_set = query_set.filter(cast(Inventory.data['from_inventory_id'], String).like(request_args['from_inventory_id']))
        
        query_set = query_set.all()
        
        formatted_query_set = []

        for entry in query_set:
            _set = {
                'ID': entry['ID'],
                'Variety': entry['Variety'],
                'SKU': entry['SKU'],
                'Quantity': None,
                'Unit':None,
                'Room': entry['Room'],
                'Source Lot': entry['Source Lot'],
                
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

    def transfer_lot_to_lot_items(self, created_by, organization_id, params, lot_id):
        '''main method to execute business logic'''
        available_lot_quantity = self._get_available_lot_qty(lot_id, params.get('unit'))
        quantity = self._get_sku_target_quantity(params.get('sku_id'), params.get('lot_item_quantity'), available_lot_quantity)
        self._check_lot_creation_time(organization_id, lot_id, params.get('timestamp'))
        user = User.query.filter_by(email=params.get('approved_by'), organization_id=organization_id).first()
        if user:
            lot_items = self._create_lot_item_bulk(created_by, organization_id, params, quantity, lot_id)
            self._update_room_bulk(created_by, organization_id, params.get('to_room'), lot_items.get('lot_items'), params.get('timestamp'))
            self._transfer_inventory_bulk(organization_id, created_by, params.get('unit'), quantity, lot_id, lot_items.get('lot_items'), available_lot_quantity, params.get("timestamp"))
            self._create_signatures_bulk(organization_id, created_by, lot_items.get('activities'), 'Approved By', user, params)
            return {"data": lot_items, "message":"success"}
        raise ClientBadRequest({
                "code": "bad_request",
                "message": f"User does not exists for {params.get('approved_by')} in organization #{organization_id}"
            }, 400)

    def _check_lot_creation_time(self, organization_id, lot_id, timestamp):
        
        lot = (Inventory.query
               .filter(Inventory.id == lot_id)
               .filter(Inventory.organization_id == organization_id)).one_or_none()
        
        utc=pytz.UTC
        
        if(timestamp < lot.timestamp):
            raise ClientBadRequest({
                "code": "bad_request",
                "message": f"lot item timestamp shouldn't be earlier than lot creation time ({lot.timestamp})"
            }, 400)
        elif(timestamp > utc.localize(datetime.now())):
            raise ClientBadRequest({
                "code": "bad_request",
                "message": f"lot item timestamp shouldn't be in the future"
            }, 400)

    def _create_lot_item_bulk(self, created_by, organization_id, params, qty, lot_id):
        
        variety_id = (TaxonomyOptions.query
                      .filter(TaxonomyOptions.name == params.get('variety'))
                      .filter(TaxonomyOptions.organization_id == organization_id)).first()
        
        if (not variety_id):
            raise ClientBadRequest({
                "code": "bad_request",
                "message": f"Variety does not exists in organization #{organization_id}"
            }, 400) 
            
        seed_weight = 0
        parent_inventory = Inventory.query.filter(Inventory.id == lot_id, Inventory.organization_id == organization_id).one_or_none()
        is_seeds = parent_inventory.stats.get('seeds', None)
        if(parent_inventory.type != 'lot'):
            raise ClientBadRequest({
                "code": "transfer_lot_item_mismatch_source_inventory",
                "description": "Source inventory must be a lot"
            }, 400)
        if (is_seeds):
            seed_weight = float(parent_inventory.attributes['seed_weight'])   
        
        '''creates lot item and relavant activity'''
        lot_items = [
            Inventory(
            organization_id = organization_id,
            created_by = created_by,
            timestamp = params.get("timestamp"),
            type = 'lot item',
            variety = params.get("variety"),
            name = self._generate_inventory_name(params.get('variety')),
            attributes = {"room": params["to_room"]} if not is_seeds else {"room": params["to_room"], "seed_weight": seed_weight},
            data = {
                "sku_id": params.get("sku_id"),
                "sku_name": params.get("sku_name"),
                "from_inventory_id": lot_id
            },
            stats = self._generate_lot_item_stats(qty, params.get("unit"))
        )
        for _ in range(params.get('lot_item_quantity'))
        ]
        db.session.bulk_save_objects(lot_items, return_defaults = True)
        db.session.commit()

        create_lot_item_activities = [
            Activity.save_activities(
                organization_id=organization_id,
                timestamp = params.get("timestamp"),
                data={
                    "variety": params.get("variety"),
                    "variety_id":variety_id.id,
                    "inventory_id": lot_item.id,
                    "from_inventory_id": lot_id,
                    "sku_id": params.get("sku_id"),
                    "sku_name": params.get("sku_name"),
                },
                created_by=created_by, 
                name='create_lot_item',
            )
            for lot_item in lot_items
        ]
        db.session.bulk_save_objects(create_lot_item_activities, return_defaults = True)
        db.session.commit()
        self._update_lot_stats(qty, params, lot_id, params.get('unit'))
        self._update_sku_current_inventory(qty, params)
        sku_detail = self._get_sku_detail(params.get('sku_id'))
        Webhook().firing_webhooks(event='skus.updated', event_data=sku_detail)
        return {
            "lot_items": [lot_item.id for lot_item in lot_items],
            "activities": [activity.id for activity in create_lot_item_activities]
            }

    def _create_signatures_bulk(self, organization_id, created_by, activities, field, user, params):
        '''creates bulk signature and relavant activity'''
        signatures = [
            Signature(
                field=field,
                created_by=created_by, 
                signed_by=user.id,
                timestamp=params.get("timestamp"),
                organization_id=organization_id,
                activity_id=activity_id,
                data={}
            )
            for activity_id in activities
        ]
        db.session.bulk_save_objects(signatures, return_defaults = True)
        db.session.commit()
        signature_activities = [
            Activity(
                organization_id=organization_id,
                created_by=created_by,
                timestamp=params.get('timestamp'),
                name='create_signature',
                data={
                   "field": field,
                    "signed_by" : user.id,
                    "activity_id" : activity_id,
                    "signature_id" : signature.id,
                }
            )
            for signature, activity_id in zip(signatures, activities)
        ]
        db.session.bulk_save_objects(signature_activities, return_defaults = True)
        db.session.commit()
        
    def _transfer_inventory_bulk(self, organization_id, created_by, unit, qty, lot_id, lot_items, available_quantity, timestamp):
        '''creates transfer and inventory adjustment activity'''
        transfer_inventory_activities = self._create_transfer_inventory(created_by, organization_id, unit, lot_items, qty, lot_id, timestamp)
        self._create_lot_adjustment(organization_id, created_by, unit, qty, lot_id, transfer_inventory_activities, available_quantity, timestamp)
        self._create_lot_item_adjustment(organization_id, created_by, unit, qty, transfer_inventory_activities, timestamp)

    def _create_transfer_inventory(self, created_by, organization_id, unit, lot_items, qty, lot_id, timestamp):
        '''Creates transfer inventory activity'''
        transfer_inventory_activities = [
            Activity(
                organization_id=organization_id,
                timestamp = timestamp,
                data={
                    "to_qty": qty,
                    "from_qty": qty,
                    "to_qty_unit": unit,
                    "from_qty_unit": unit,
                    "to_inventory_id": lot_item_id,
                    "from_inventory_id":  lot_id,
                },
                created_by=created_by,
                name='transfer_inventory',
            )
            for lot_item_id in lot_items
        ]
        
        db.session.bulk_save_objects(transfer_inventory_activities, return_defaults=True)
        db.session.commit()
        
        return transfer_inventory_activities

    def _create_lot_adjustment(self, organization_id, created_by, unit, qty, lot_id, transfer_inventory_activities, available_quantity, timestamp):
        '''creates inventory adjustment activity for lot'''
        lot_adjustment_activities = []
        for lot_item in transfer_inventory_activities:
            activity = Activity(
                organization_id=organization_id,
                timestamp = timestamp,
                data = {
                    "unit": unit,
                    "quantity": available_quantity-qty,
                    "inventory_id": lot_item.data['from_inventory_id'],
                    "activity_id": lot_item.id,
                    "activity_name": 'transfer_inventory',
                    "invetory_type": 'lot'
                },
                created_by=created_by,
                name='inventory_adjustment',
                parent_id=lot_item.id
            )
            lot_adjustment_activities.append(activity)
            available_quantity -= qty
        db.session.bulk_save_objects(lot_adjustment_activities, return_defaults=True)
        db.session.commit()

    def _create_lot_item_adjustment(self, organization_id, created_by, unit, qty, transfer_inventory_activities, timestamp):
        '''creates inventory adjustment activity for lot items'''
        lot_item_adjustment_activities = [
            Activity(
                organization_id=organization_id,
                timestamp = timestamp,
                data = {
                    "unit": unit,
                    "quantity": qty,
                    "inventory_id": lot_item.data['to_inventory_id'],
                    "activity_id": lot_item.id,
                    "activity_name": 'transfer_inventory',
                    "invetory_type": 'lot item'
                },
                created_by=created_by,
                name='inventory_adjustment',
                parent_id=lot_item.id
            )
            for lot_item in transfer_inventory_activities
        ]
        db.session.bulk_save_objects(lot_item_adjustment_activities, return_defaults=True)
        db.session.commit()

    def _update_room_bulk(self, created_by, organization_id, to_room, lot_items, timestamp):
        '''Updates room for lot_item'''
        update_room_activities = [
            Activity(
                organization_id=organization_id,
                timestamp = timestamp,
                data={
                    "to_room": to_room,
                    "inventory_id": _id,
                },
                created_by=created_by,
                name='update_room'
            )
            for _id in lot_items
        ]
        db.session.bulk_save_objects(update_room_activities, return_defaults = True)
        db.session.commit()

    def _generate_inventory_name(self, variety):
        '''generates inventory name'''
        return "{0}-{1}-{2}".format(variety, datetime.utcnow().isocalendar()[1], datetime.utcnow().year % 100)

    def _get_sku_target_quantity(self, sku_id, lot_item_quantity, available_lot_quantity):
        '''returns skus target quantity if available'''
        sku = Skus.query.get(sku_id)
        if sku and (sku.target_qty * lot_item_quantity) <= available_lot_quantity:
            return sku.target_qty
        raise ClientBadRequest({
                "code": "bad_request",
                "message": f"Not enough quantity available to create {lot_item_quantity} number of lot_items from sku #{sku_id}"
            }, 400)


    def _get_available_lot_qty(self, lot_id, unit):
        '''Returns available lot quantity'''
        inventory = Inventory.query.get(lot_id)
        if inventory:
            try:
                if unit in ['plants', 'seeds', 'g-wet']:
                    return float(inventory.stats.get(unit))
                elif unit in ['dry', 'cured']:
                    return float(inventory.stats.get('g-dry').get(unit))
                elif unit in ['crude', 'distilled']:
                    return float(inventory.stats.get('g-oil').get(unit))
                else:
                    return float(inventory.stats.get('g-extract').get(unit))
            except Exception as e:
                raise ClientBadRequest(
                    {
                        "code": "bad_request",
                        "message": f"Please provide the correct 'unit_type' for lot #{lot_id}",
                    }, 400
                )
        raise ClientBadRequest({
                "code": "bad_request",
                "message": f"No record found for inventory #{lot_id}"
            }, 400)

    def _generate_lot_item_stats(self, qty, unit):
        '''generates lot_item stats'''
        stats = {}
        if unit in ['plants', 'seeds', 'g-wet']:
            stats[unit] = float(qty)
        elif unit in ['crude', 'distilled']:
            stats['g-oil'] = {"crude":0, "distilled":0}
            stats['g-oil'][unit] = float(qty)
        elif unit in ['dry', 'cured']:
            stats['g-dry'] = {"dry":0, "cured":0}
            stats['g-dry'][unit] = float(qty)
        else:
            stats['g-extract'] = {unit: float(qty)}
        return stats

    def _update_lot_stats(self, qty,params, lot_id, unit):
        '''Updates lot stats'''
        with db.session.no_autoflush:
            total_qty = qty*params.get("lot_item_quantity")
            lot = Inventory.query.get(lot_id)
            lot.stats = deepcopy(lot.stats)
            try:
                if unit in ['plants', 'seeds', 'g-wet']:
                    lot.stats[unit] = float(lot.stats.get(unit)) - float(total_qty)
                elif unit in ['crude', 'distilled']:
                    lot.stats['g-oil'][unit] = float(lot.stats.get('g-oil').get(unit)) - float(total_qty)
                elif unit in ['dry', 'cured']:
                    lot.stats['g-dry'][unit] = float(lot.stats.get('g-dry').get(unit)) - float(total_qty)
                else:
                    lot.stats['g-extract'][unit] = float(lot.stats.get('g-extract').get(unit)) - float(total_qty)
                lot.stats = self._serialize_stats(lot.stats)
                db.session.add(lot)
                db.session.commit()
                affected_rows = 1
                return affected_rows
            except Exception as e:
                raise ClientBadRequest(
                    {
                        "code": "bad_request",
                        "message": f"Please provide the correct 'unit_type' for lot #{lot_id}",
                    }, 400
                )

    def _serialize_stats(self, stats):
        '''Serializes stats of inventory'''
        return eval(json.dumps(stats))

    def _update_sku_current_inventory(self, qty, params):
        '''updates sku current inventory'''
        sku = Skus.query.get(params.get("sku_id"))
        sku.current_inventory +=  params.get("lot_item_quantity")
        db.session.add(sku)
        db.session.commit()

    def _get_sku_detail(self, sku_id):
        sku = Skus.query.get(sku_id)
        return {
            "sku_id": sku.id,
            "name": sku.name,
            "current_inventory": sku.current_inventory,
            "price": float(sku.price),
            "external_sku_variant_id": sku.data.get('external_sku_variant_id'),
            "external_sku_id": sku.data.get('external_sku_id'),
            "id": sku.id,
            "variety": sku.variety
        }

