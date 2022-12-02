"""This module contains base schema for inventory table"""


from class_errors import ClientBadRequest
from models.signature import Signature
from models.activity import Activity
from models.activities_mapping import ActivitiesMapping
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from flask import jsonify
from operator import or_
from app import db
from models.taxonomy_options import TaxonomyOptions
from utils.decimal_encoder import DecimalEncoder
import json

class Inventory(db.Model):

    __tablename__ = 'inventories'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String())
    type = db.Column(db.String())
    variety = db.Column(db.String())
    data = db.Column(JSONB) 
    stats = db.Column(JSONB)
    attributes = db.Column(JSONB)
    is_child = db.Column(db.Boolean, default=False)
    is_parent = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer)

    @property
    def serialize(self):
          return {
            'id': self.id,
            'organization_id': self.organization_id,
            'created_by': self.created_by,
            'timestamp': self.timestamp,
            'name': self.name,
            'type': self.type,
            'variety' : self.variety,
            'data' : self.data,
            'stats' : self.stats,
            'attributes' : self.attributes,
            'is_child': self.is_child,
            'is_parent': self.is_parent,
            'parent_id': self.parent_id
          }

    def find(id):
      res = db.session.query(Inventory).filter(Inventory.id==id)
      return jsonify(json_list=[i.serialize for i in res])

    def create_inventory_adjustment(organization_id, created_by, unit, qtd, inventory_id, activity_name, inventory_type, parent_id = None, timestamp = None):
      data = { 
        "unit": unit, 
        "quantity": qtd,
        "inventory_id": inventory_id, 
        "activity_id": parent_id,
        "activity_name": activity_name, 
        "invetory_type": inventory_type 
      }
      Activity.save_activities(organization_id, data, created_by, 'inventory_adjustment', parent_id, timestamp=timestamp)

    def transfer_inventory(organization_id, created_by, from_inventory_id, to_inventory_id, quantity, approved_by, prepared_by, reviewed_by, parent_id, timestamp):
      
      from_inventory = (Inventory.query
                                 .filter(Inventory.id == from_inventory_id)
                                 .filter(Inventory.organization_id == organization_id)
                                 .one_or_none())
      
      
      to_inventory = (Inventory.query
                                 .filter(Inventory.id == to_inventory_id)
                                 .filter(Inventory.organization_id == organization_id)
                                 .one_or_none())
      
      from_inventory_serialized_stats = Inventory.serialize_inventory_stats(from_inventory.stats)
      to_inventory_serialized_stats =  Inventory.serialize_inventory_stats(to_inventory.stats)
      
      if from_inventory_serialized_stats.get('unit') != to_inventory_serialized_stats.get('unit'):
        raise ClientBadRequest({"message": f"Inventories should be of the same type to transfer process"}, 400)
      
      if from_inventory_serialized_stats.get('qty') - quantity < 0:
        raise ClientBadRequest({"message": f"Origin inventory amount is not enough to transfer"}, 400)
      
      from_inventory_stats = Inventory.deserialize_inventory_stats(organization_id, 
                                                                   from_inventory_serialized_stats.get('unit'), 
                                                                   from_inventory_serialized_stats.get('qty') - quantity)
      
      to_inventory_stats =  Inventory.deserialize_inventory_stats(organization_id, 
                                                                   to_inventory_serialized_stats.get('unit'), 
                                                                   to_inventory_serialized_stats.get('qty') + quantity)
      
      data = {
        "to_qty": float(quantity),
        "variety": from_inventory.variety,
        "from_qty": float(quantity),
        "approved_by": approved_by,
        "prepared_by": prepared_by,
        "reviewed_by": reviewed_by,
        "to_qty_unit": from_inventory_serialized_stats.get('unit'),
        "from_qty_unit": to_inventory_serialized_stats.get('unit'),
        "to_inventory_id": to_inventory_id,
        "from_inventory_id": from_inventory_id
      }
      
      activity = Activity.save_activities(organization_id, data, created_by, 'transfer_inventory', parent_id, timestamp=timestamp)
      
      setattr(from_inventory, 'stats', json.loads(json.dumps(from_inventory_stats, cls=DecimalEncoder)))
      
      Inventory.create_inventory_adjustment(organization_id, created_by, 
                                            from_inventory_serialized_stats.get('unit'), 
                                            float(from_inventory_serialized_stats.get('qty') - quantity), 
                                            from_inventory_id, 
                                            'transfer_inventory', 
                                            from_inventory.type,
                                            activity.id, timestamp)
      
      setattr(to_inventory, 'stats', json.loads(json.dumps(to_inventory_stats, cls=DecimalEncoder)))
      
      Inventory.create_inventory_adjustment(organization_id, created_by,
                                            to_inventory_serialized_stats.get('unit'),
                                            float(quantity),
                                            to_inventory_id,
                                            'transfer_inventory',
                                            to_inventory.type,
                                            activity.id, timestamp)
      
      db.session.commit()

    def adjustment_with_signatures(self, inventory_transition, parent_activity, params):
      Inventory.create_inventory_adjustment(parent_activity.organization_id, parent_activity.created_by, inventory_transition['origin_unit'], inventory_transition['origin_qty'], inventory_transition['origin_id'], parent_activity.name, inventory_transition['origin_type'], parent_activity.id)
      Inventory.create_inventory_adjustment(parent_activity.organization_id, parent_activity.created_by, inventory_transition['destiny_unit'], inventory_transition['destiny_qty'], inventory_transition['destiny_id'], parent_activity.name, inventory_transition['destiny_type'], parent_activity.id)
      Signature.create_signature(parent_activity.id, parent_activity.organization_id, parent_activity.created_by, 'Recorded By', params['recorded_by'], parent_activity.id)
      Signature.create_signature(parent_activity.id, parent_activity.organization_id, parent_activity.created_by, 'Approved By', params['approved_by'], parent_activity.id)

    def inventory_adjustment_different_inventories_same_unit(organization_id, created_by, from_inventory_id, to_inventory_id, quantity, activity_name, parent_id = None):
      
      from_inventory = db.session.query(Inventory).filter(Inventory.id == from_inventory_id).filter(Inventory.organization_id == organization_id).one_or_none()
      to_inventory = db.session.query(Inventory).filter(Inventory.id == to_inventory_id).filter(Inventory.organization_id == organization_id).one_or_none()
      
      from_inventory_current_stats = Inventory.serialize_inventory_stats(from_inventory.stats)
      to_inventory_current_stats = Inventory.serialize_inventory_stats(to_inventory.stats)
      
      from_inventory_adjusted_stats = Inventory.deserialize_inventory_stats(organization_id, from_inventory_current_stats.get('unit'), from_inventory_current_stats.get('qty') - quantity)
      
      if to_inventory_current_stats:
        to_inventory_adjusted_stats = Inventory.deserialize_inventory_stats(organization_id, to_inventory_current_stats.get('unit'), to_inventory_current_stats.get('qty') + quantity)
      else:
        to_inventory_adjusted_stats = Inventory.deserialize_inventory_stats(organization_id, from_inventory_current_stats.get('unit'), quantity)
      
      setattr(from_inventory, 'stats', json.loads(json.dumps(from_inventory_adjusted_stats, cls=DecimalEncoder)))
      setattr(to_inventory, 'stats', json.loads(json.dumps(to_inventory_adjusted_stats, cls=DecimalEncoder)))
      
      Inventory.create_inventory_adjustment(organization_id, 
                                                    created_by, 
                                                    Inventory.serialize_inventory_stats(from_inventory_adjusted_stats).get('unit'), 
                                                    float(Inventory.serialize_inventory_stats(from_inventory_adjusted_stats).get('qty')),
                                                    from_inventory.id,
                                                    activity_name,
                                                    from_inventory.type, 
                                                    parent_id)
      
      Inventory.create_inventory_adjustment(organization_id, 
                                                    created_by, 
                                                    Inventory.serialize_inventory_stats(to_inventory_adjusted_stats).get('unit'), 
                                                    float(Inventory.serialize_inventory_stats(to_inventory_adjusted_stats).get('qty')),
                                                    to_inventory.id,
                                                    activity_name,
                                                    to_inventory.type, 
                                                    parent_id)

      db.session.commit()

    def get_all_activities_by_inventory_id(inventory_id):
      
      activities = db.session.execute("""SELECT act.* FROM inventories AS inv
                                      INNER JOIN activities AS act
                                      ON 
                                      CONCAT('"',(CAST(inv.id as VARCHAR)),'"') = ANY(ARRAY(SELECT jsonb_array_elements(CASE jsonb_typeof(act.data->'from_inventory_id') WHEN 'array' THEN act.data->'from_inventory_id' ELSE '[]' END))::varchar[]) OR
                                      inv.id = CAST((CASE jsonb_typeof(act.data->'from_inventory_id') WHEN 'array' THEN '0' ELSE act.data->>'from_inventory_id' END) AS integer) OR
                                      inv.id = CAST(act.data->>'to_inventory_id' AS integer) OR
                                      inv.id = CAST(act.data->>'inventory_id'as integer)
                                      WHERE inv.id = :inv_id
                                      ORDER BY act.timestamp DESC;""", {'inv_id': inventory_id})

      return activities.mappings().all()

    def deserialize_inventory_stats(organization_id, unit, quantity):
      
      parent = TaxonomyOptions.get_stats_object_by_name(organization_id, unit).parent
        
      if parent:
          return {
              parent: {
                  unit: quantity
              }
          }
      else:
          return {
                  unit: quantity
              }

    def serialize_inventory_stats(stats):

      serialized_stats = []

      for key_1, value_1 in stats.items():
        if isinstance(value_1, dict):
            for key_2, value_2 in value_1.items():
                if isinstance(value_2, dict):
                    for key_3, value_3 in value_2.items():
                        serialized_stats.append({'unit': key_3, 'qty': value_3})
                else:
                    serialized_stats.append({'unit': key_2, 'qty': value_2})
        else:
            serialized_stats.append({'unit': key_1, 'qty': value_1})

      serialized_stats = sorted(serialized_stats, key=lambda d: d['qty'], reverse=True)

      return serialized_stats[0]

    def backdate_inventory_by_activity_id(organization_id, timestamp, activity_id):
      
      act = db.session.query(Activity).filter(Activity.id == activity_id).filter(Activity.organization_id == organization_id).one_or_none()
      activities_create_inventory = ActivitiesMapping.get_activities_create_inventory()
      
      if(any(a.name == act.name for a in activities_create_inventory)):
        inv = (Inventory.query
                .filter(or_(Inventory.id == act.data.get('inventory_id'), Inventory.id == act.data.get('to_inventory_id')))
                .filter(Inventory.organization_id == organization_id)
                .one_or_none()
                )
        
        setattr(inv, 'timestamp', timestamp)
        db.session.commit()
