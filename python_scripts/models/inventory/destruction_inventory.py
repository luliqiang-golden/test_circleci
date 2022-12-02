"""This module contains database schema model for inventory type = destruction inventory table"""

import json
from sqlalchemy import Integer
from models.activity import Activity
from models.inventory import Inventory
from models.signature import Signature
from models.taxonomy_options import TaxonomyOptions
from utils.decimal_encoder import DecimalEncoder
from app import db



class DestructionInventory(Inventory):

    def __init__(self, organization_id, created_by, destruction_inventory_id):

        self.created_by = created_by
        
        self.organization_id = organization_id

        self.destruction_inventory_activity = (Activity.query
                                          .filter(Activity.name == 'queue_for_destruction')
                                          .filter(Activity.data['to_inventory_id'].astext.cast(Integer) == destruction_inventory_id)
                                          .filter(Activity.organization_id == organization_id).one_or_none())

        self.destruction_inventory = (Inventory.query
                                 .filter(Inventory.organization_id == organization_id)
                                 .filter(Inventory.id == self.destruction_inventory_activity.data['to_inventory_id']).one_or_none())

        self.original_inventory = (Inventory.query
                                 .filter(Inventory.organization_id == organization_id)
                                 .filter(Inventory.id == self.destruction_inventory_activity.data['from_inventory_id']).one_or_none())

        self.destruction_inventory_stats = Inventory.serialize_inventory_stats(self.destruction_inventory.stats)
        self.original_inventory_stats = Inventory.serialize_inventory_stats(self.original_inventory.stats)
        
        self.original_inventory_history = Inventory.get_all_activities_by_inventory_id(self.original_inventory.id)
        
        # plants is the default value because the only scenario where from_qty_unit is null is when a destruction of plant is done wihtout the inventory adjustment option
        self.destruction_inventory_type = self.destruction_inventory_activity.data.get('from_qty_unit', 'plants')

    def dequeue_destruction_inventory(self, data):

        dequeue_from_destruction_activity = DestructionInventory.__save_dequeue_activity(self, data)
        
        Signature.create_signature(dequeue_from_destruction_activity.id, 
                                   self.organization_id, 
                                   self.created_by,
                                   'witness_1', data.get('witness_1'), dequeue_from_destruction_activity.id)
        
        Signature.create_signature(dequeue_from_destruction_activity.id, 
                                   self.organization_id, 
                                   self.created_by,
                                   'witness_2', data.get('witness_2'), dequeue_from_destruction_activity.id)

        if(self.destruction_inventory_stats.get('unit') == self.original_inventory_stats.get('unit')):
            if(self.destruction_inventory_type != 'seeds' and self.destruction_inventory_type != 'plants'):
                DestructionInventory.__dequeue_equal_types_inventory_adjustment(self, dequeue_from_destruction_activity)
            else:
                DestructionInventory.__dequeue_different_types_inventory_adjustment(self, dequeue_from_destruction_activity)
        else:
            if(self.destruction_inventory_type == 'seeds' and self.original_inventory_stats.get('unit') == 'seeds'):
                DestructionInventory.__dequeue_seeds_inventory_adjustment(self, dequeue_from_destruction_activity)
            elif(self.destruction_inventory_type == 'plants' and self.original_inventory_stats.get('unit') == 'plants'):
                DestructionInventory.__dequeue_plants_inventory_adjustment(self, dequeue_from_destruction_activity)
            else:
                DestructionInventory.__dequeue_different_types_inventory_adjustment(self, dequeue_from_destruction_activity)
        
        Activity.delete_activities(self.destruction_inventory_activity.id, self.organization_id, self.created_by, 'queue_for_destruction', data.get('reason_for_dequeue'))
        
        return dequeue_from_destruction_activity
        
    def __dequeue_seeds_inventory_adjustment(self, dequeue_from_destruction_activity):

        original_qty = float(self.original_inventory_stats.get('qty') + dequeue_from_destruction_activity.data['to_qty'])
        original_stats = Inventory.deserialize_inventory_stats(self.organization_id, self.original_inventory_stats.get('unit'), original_qty)
        setattr(self.original_inventory, 'stats', json.loads(json.dumps(original_stats, cls=DecimalEncoder)))

        data = {
                "unit": self.original_inventory_stats.get('unit'),
                "quantity": original_qty,
                "inventory_id": self.original_inventory.id,
                "activity_id": dequeue_from_destruction_activity.id,
                "activity_name": 'dequeue_from_destruction', 
                "invetory_type": self.original_inventory.type
        }

        Activity.save_activities(self.organization_id, data, self.created_by, 'inventory_adjustment', dequeue_from_destruction_activity.id)

        destruction_stats = Inventory.deserialize_inventory_stats(self.organization_id, self.destruction_inventory_stats.get('unit'), 0)
        setattr(self.destruction_inventory, 'stats', json.loads(json.dumps(destruction_stats, cls=DecimalEncoder)))

        data = { 
                "unit": self.destruction_inventory_stats.get('unit'),
                "quantity": 0.0,
                "inventory_id": self.destruction_inventory.id,
                "activity_id": dequeue_from_destruction_activity.id,
                "activity_name": 'dequeue_from_destruction', 
                "invetory_type": self.destruction_inventory.type
        }

        Activity.save_activities(self.organization_id, data, self.created_by, 'inventory_adjustment', dequeue_from_destruction_activity.id)

        db.session.commit()

    def __dequeue_plants_inventory_adjustment(self, dequeue_from_destruction_activity):

        check_original_inventory_flowering_stage = DestructionInventory.__check_update_stage_flowering_for_plants(self.original_inventory_history)

        original_qty = float(self.original_inventory_stats.get('qty') + dequeue_from_destruction_activity.data['to_qty'])
        original_stats = Inventory.deserialize_inventory_stats(self.organization_id, self.original_inventory_stats.get('unit'), original_qty)
        setattr(self.original_inventory, 'stats', json.loads(json.dumps(original_stats, cls=DecimalEncoder)))

        data = {
                "unit": self.original_inventory_stats.get('unit'),
                "quantity": original_qty,
                "inventory_id": self.original_inventory.id,
                "activity_id": dequeue_from_destruction_activity.id,
                "activity_name": 'dequeue_from_destruction', 
                "invetory_type": self.original_inventory.type
        }

        Activity.save_activities(self.organization_id, data, self.created_by, 'inventory_adjustment', dequeue_from_destruction_activity.id)

        destruction_stats = Inventory.deserialize_inventory_stats(self.organization_id, self.destruction_inventory_stats.get('unit'), 0)
        setattr(self.destruction_inventory, 'stats', json.loads(json.dumps(destruction_stats, cls=DecimalEncoder)))

        data = { 
                "unit": self.destruction_inventory_stats.get('unit'),
                "quantity": 0.0,
                "inventory_id": self.destruction_inventory.id,
                "activity_id": dequeue_from_destruction_activity.id,
                "activity_name": 'dequeue_from_destruction', 
                "invetory_type": self.destruction_inventory.type
        }
        
        Activity.save_activities(self.organization_id, data, self.created_by, 'inventory_adjustment', dequeue_from_destruction_activity.id)
        
        if(check_original_inventory_flowering_stage):
            if(check_original_inventory_flowering_stage.timestamp > self.destruction_inventory_activity.timestamp):
                check_original_inventory_flowering_stage.data['qty'] = int(original_qty)
                db.session.query(Activity).filter(Activity.id == check_original_inventory_flowering_stage.id).update({
                        'data': json.loads(json.dumps(check_original_inventory_flowering_stage.data, cls=DecimalEncoder))
                })

        db.session.commit()

    def __dequeue_different_types_inventory_adjustment(self, dequeue_from_destruction_activity):

        stats = Inventory.deserialize_inventory_stats(self.organization_id, self.destruction_inventory_type, dequeue_from_destruction_activity.data['to_qty'])
        attributes = self.original_inventory.attributes
        
        if(self.destruction_inventory_type != 'seeds' and self.destruction_inventory_type != 'plants'):
            taxonomy_options = (db.session.query(TaxonomyOptions).filter(TaxonomyOptions.name == self.destruction_inventory_type)
                                                  .filter(TaxonomyOptions.organization_id == self.organization_id).one_or_none())
            
            attributes['stage'] = taxonomy_options.data['stages'][-1]
        
        else:
            attributes['stage'] = 'planning'
        
        db.session.query(Inventory).filter(Inventory.id == self.destruction_inventory.id).update({
                'type': 'batch',
                'data': json.loads(json.dumps(self.original_inventory.data, cls=DecimalEncoder)),
                'stats': json.loads(json.dumps(stats, cls=DecimalEncoder)),
                'attributes':  json.loads(json.dumps(attributes, cls=DecimalEncoder))
        })

        data = {
                "unit": self.destruction_inventory_type,
                "quantity": dequeue_from_destruction_activity.data['to_qty'],
                "inventory_id": self.destruction_inventory.id,
                "activity_id": dequeue_from_destruction_activity.id,
                "activity_name": 'dequeue_from_destruction', 
                "invetory_type": self.destruction_inventory.type
        }

        Activity.save_activities(self.organization_id, data, self.created_by, 'inventory_adjustment', dequeue_from_destruction_activity.id)

        if(self.destruction_inventory_type == 'plants'):
                check_original_inventory_flowering_stage = DestructionInventory.__check_update_stage_flowering_for_plants(self.original_inventory_history)
                data = {
                    'qty': dequeue_from_destruction_activity.data['to_qty'],
                    'unit': 'plants',
                    'to_stage': 'planning',
                    'inventory_id': self.destruction_inventory.id
                }
                Activity.save_activities(self.organization_id, data, self.created_by, 'update_stage')
                if(check_original_inventory_flowering_stage):
                    if(check_original_inventory_flowering_stage.timestamp < self.destruction_inventory_activity.timestamp):
                        check_original_inventory_flowering_stage.data['qty'] = check_original_inventory_flowering_stage.data['qty'] - dequeue_from_destruction_activity.data['to_qty']
                        db.session.query(Activity).filter(Activity.id == check_original_inventory_flowering_stage.id).update({
                                'data': json.loads(json.dumps(check_original_inventory_flowering_stage.data , cls=DecimalEncoder))
                        })
        
        db.session.commit()

    def __dequeue_equal_types_inventory_adjustment(self, dequeue_from_destruction_activity):
        
        Inventory.inventory_adjustment_different_inventories_same_unit(self.organization_id, 
                                           self.created_by, 
                                           dequeue_from_destruction_activity.data['from_inventory_id'],
                                           dequeue_from_destruction_activity.data['to_inventory_id'], 
                                           dequeue_from_destruction_activity.data['to_qty'],
                                           'dequeue_from_destruction',
                                           dequeue_from_destruction_activity.id)

    def __check_update_stage_flowering_for_plants(original_inventory_history):
        for entry in original_inventory_history:
            if(entry.name == 'update_stage' and entry.data['to_stage'] == 'flowering'):
                return (Activity.query
                                .filter(Activity.id == entry.id).one_or_none())
        return None

    def __save_dequeue_activity(self, data):

        dequeue_from_destruction_activity = Activity.save_activities(organization_id = self.organization_id, 
                                 data = {
                                        'to_qty': float(self.destruction_inventory_activity.data.get('from_qty', 0)),
                                        'variety': self.destruction_inventory_activity.data.get('variety'),
                                        'from_qty': float(self.destruction_inventory_activity.data.get('to_qty')),
                                        'to_qty_unit': self.destruction_inventory_type,
                                        'from_qty_unit': self.destruction_inventory_stats.get('unit'),
                                        'to_inventory_id': int(self.destruction_inventory_activity.data.get('from_inventory_id')),
                                        'from_inventory_id': int(self.destruction_inventory_activity.data.get('to_inventory_id')),
                                        'reason_for_dequeue': data.get('reason_for_dequeue'),
                                        'witness_1': data.get('witness_1'),
                                        'witness_2': data.get('witness_2'),
                                 },
                                 created_by = self.created_by,
                                 name = 'dequeue_from_destruction',
                                 parent_id=self.destruction_inventory_activity.id)
        
        return dequeue_from_destruction_activity