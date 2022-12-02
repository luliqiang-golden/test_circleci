import copy
from datetime import datetime
import json
from models.activities_mapping import ActivitiesMapping
from models.signature import Signature
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.sqltypes import String
from class_errors import ClientBadRequest
from models.inventory import Inventory
from models.activity import Activity
from app import db
from models.rooms import Rooms
from ..taxonomy_options import TaxonomyOptions
from utils.decimal_encoder import DecimalEncoder


class Batch(Inventory):

    def get_batches_per_rooms(organization_id, rooms):

        result = []

        rooms_array = [room.strip() for room in rooms.split(',')]

        query_set = (Inventory.query.
                     with_entities(Inventory.id.label('id'),
                                   Inventory.name.label('name'),
                                   Inventory.stats.label('stats'),
                                   Inventory.data['plan']['end_type'].label('end_type'),
                                   Inventory.attributes['stage'].label('stage'),
                                   Inventory.attributes['room'].label('room'),
                                   Inventory.attributes['salvage_batch'].label('salvage_batch'),
                                   Inventory.data['plan'].label('plan')).
                     join(Rooms, Inventory.attributes['room'].astext == Rooms.name).
                     filter(Inventory.stats != {}).
                     filter(Inventory.type == 'batch').
                     filter(Rooms.id.in_(rooms_array)).
                     filter(Inventory.organization_id == organization_id).
                     order_by(Inventory.timestamp.desc())).all()
        
        for entry in query_set:
            stats = Inventory.serialize_inventory_stats(entry['stats'])
            _set = {
                'id': entry['id'],
                'name': entry['name'],
                'quantity': stats.get('qty'),
                'unit': stats.get('unit'),
                'end_type': entry['end_type'],
                'stage': entry['stage'],
                'room': entry['room'],
                'stats': entry['stats'],
                'salvage_batch': entry['salvage_batch'],
                'plan': entry['plan'],
            }
            
            result.append(_set)

        return result

    def duplicate_batch_empty_stats(organization_id, created_by, original_batch_id, scale_name, timestamp):
        
        original_inventory = (Inventory.query
                      .filter(Inventory.id == original_batch_id)
                      .filter(Inventory.organization_id == organization_id)).one_or_none()
        
        if not original_inventory:
            raise ClientBadRequest({"message": f"Inventory not found"}, 400)  
        
        original_inventory_stats = Inventory.serialize_inventory_stats(original_inventory.stats)
        
        stats = json.loads(json.dumps(Inventory.deserialize_inventory_stats(organization_id, original_inventory_stats.get('unit'), 0)))
        
        duplicated_inventory = Inventory(
            organization_id = organization_id,
            created_by = created_by,
            name = original_inventory.name + " - child",
            type = original_inventory.type,
            variety = original_inventory.variety,
            data = original_inventory.data,
            stats = stats,
            attributes = original_inventory.attributes,
            is_child = True,
            parent_id = original_batch_id,
            timestamp = timestamp,
            )
        
        setattr(original_inventory, 'is_parent', True)

        db.session.add(duplicated_inventory)
        db.session.commit()
        
        create_batch_data = {
            "variety": original_inventory.variety,
            "scale_name": scale_name,
            "variety_id": TaxonomyOptions.get_variety_by_name(organization_id, original_inventory.variety).id,
            "custom_name": original_inventory.name + " - child",
            "inventory_id": duplicated_inventory.id,
            "to_test_status": ""
        }
        
        activity = Activity.save_activities(organization_id, create_batch_data, created_by, 'create_batch', timestamp = timestamp)

        return {'inventory': duplicated_inventory, 'activity': activity}

    def germinate_seed(self, created_by, organization_id, params):
        seeds_quantity = float(self.stats.get('seeds'))
        ungerminated_seeds = float(seeds_quantity - params["quantity"])

        seeds = {
            "quantity": seeds_quantity,
            "ungerminated": ungerminated_seeds
        }

        if (params["quantity"] >= 0):
                queue_for_destruction_activity_id = self.__destroy_ungerminated_seeds(created_by, organization_id, params, seeds)
                germinate_seeds_activity_id = self.__create_germinated_seed(created_by, organization_id, params)

                self.__bind_parent_id(queue_for_destruction_activity_id, germinate_seeds_activity_id)
                return {
                    'queue_for_destruction_activity_id': queue_for_destruction_activity_id,
                    'germinate_seeds_activity_id': germinate_seeds_activity_id,
                }
        else:
            return {
                'queue_for_destruction_activity_id': -1,
                'germinate_seeds_activity_id': -1,
            }

    def __create_germinated_seed(self, created_by, organization_id, params):
        
        plants_qty = float(params['quantity'])

        if (plants_qty > 0):
            self.stats = {
                "seeds": 0.0,
                "plants": plants_qty
            }

            self.attributes['seed_weight'] = float(self.attributes['seed_weight'])
            self.attributes['seeds_weight'] = (float(self.attributes['seed_weight']) * plants_qty)
            flag_modified(self, 'attributes')

            data = {
                "to_qty": plants_qty,
                "scale_name" : params["scale_name"],
                "from_qty": plants_qty,
                "approved_by" : params["approved_by"],
                "recorded_by" : params["recorded_by"],
                "seeds_weight" : float(self.attributes['seeds_weight']),
                "to_qty_unit": "plants",
                "from_qty_unit": "seeds",
                "to_inventory_id": self.id,
                "from_inventory_id": self.id,
                "timestamp": params["timestamp"],
            }
            germinate_seeds_activity = Activity.save_activities(organization_id, data, created_by, 'germinate_seeds')

            inventory_transition = {
                "destiny_qty": plants_qty,
                "destiny_unit": "plants",
                "destiny_id": self.id,
                "destiny_type": self.type,
                "origin_qty": 0,
                "origin_unit": "seeds",
                "origin_id": self.id,
                "origin_type": self.type
            }
            self.adjustment_with_signatures(inventory_transition, germinate_seeds_activity, params)
            return germinate_seeds_activity.id
        else:
            return -1

    def __destroy_ungerminated_seeds(self, created_by, organization_id, params, seeds):

        gwet = float(self.attributes['seed_weight']) * seeds.get('ungerminated')
        
        if seeds.get('ungerminated') > 0:
            self.stats = {
                "seeds": seeds.get('quantity') - seeds.get('ungerminated'),
            }

            self.attributes['seed_weight'] = float(self.attributes['seed_weight'])
            self.attributes['seeds_weight'] = float(self.attributes['seeds_weight']) - gwet
            flag_modified(self, 'attributes')

            to_destruction_inventory = self.__create_destruction_inventory(gwet)
            data = {
                "from_qty": seeds.get('ungerminated'),
                "variety" : self.variety,
                "to_qty" : gwet,
                "scale_name": params["scale_name"],
                "reason_for_destruction": "Ungerminated seeds",
                "to_qty_unit": "g-wet",
                "from_qty_unit": "seeds",
                "from_inventory_id" : self.id,
                "to_inventory_id": to_destruction_inventory.id,
                "approved_by" : params["approved_by"] ,
                "recorded_by" : params["recorded_by"] ,
                "type_of_waste" : "seeds",
                "collected_from": self.attributes['room'],
                "timestamp": params["timestamp"]
            }
            destruction_activity = Activity.save_activities(organization_id, data, created_by, 'queue_for_destruction')

            inventory_transition = {
                "destiny_qty": gwet,
                "destiny_unit": "g-wet",
                "destiny_id": to_destruction_inventory.id,
                "destiny_type": to_destruction_inventory.type,
                "origin_qty": seeds.get('quantity') - seeds.get('ungerminated'),
                "origin_unit": "seeds",
                "origin_id": self.id,
                "origin_type": self.type
            }
            self.adjustment_with_signatures(inventory_transition, destruction_activity, params)
            return destruction_activity.id
        else:
            return -1

    def __create_destruction_inventory(self, gwet):
        inventory_name = "{0}-{1}-{2}".format(
            self.variety,
            datetime.now().isocalendar()[1],
            datetime.now().year % 100,
        )

        data = {'collected_from': self.attributes['room'], 'from_inventory_id': self.id, 'reason_for_destruction': 'Ungerminated seeds'}
        stats = {'g-wet': gwet}
        destruction_inventory = Inventory(name=inventory_name, organization_id=self.organization_id, type='destruction inventory', variety=self.variety, created_by=self.created_by, timestamp=self.timestamp, data=data, stats=stats, attributes={'status': 'undestroyed'})
        db.session.add(destruction_inventory)
        db.session.flush()
        db.session.commit()
        return destruction_inventory

    def __bind_parent_id(self, queue_for_destruction_activity_id, germinate_seeds_activity_id):
        for destruction in db.session.query(Activity).filter(Activity.id == queue_for_destruction_activity_id):
            destruction.parent_id = germinate_seeds_activity_id
            flag_modified(destruction, 'parent_id')
            db.session.add(destruction)
            db.session.commit()

    def batches_report(self, organization_id, request_args):
        query_set = (Inventory.query.
                     with_entities(Inventory.id.label('ID'),
                                   Inventory.name.label('Name'),
                                   Inventory.stats.label('Quantity'),
                                   Inventory.stats.label('Unit'),
                                   Inventory.data['plan']['end_type'].label('End-type'),
                                   Inventory.attributes['stage'].label('Stage'),
                                   Inventory.attributes['room'].label('Room')).
                     filter(Inventory.stats != {}).
                     filter(Inventory.type == 'batch').
                     filter(Inventory.organization_id == organization_id).
                     order_by(Inventory.timestamp.desc()))
        if request_args.get('id'):
            query_set = query_set.filter(cast(Inventory.id, String).like(request_args.get('id')  +'%'))
        if request_args.get('variety'):
            query_set = query_set.filter(Inventory.variety == request_args.get('variety'))
        if request_args.get('plan.end_type'):
            query_set = query_set.filter(Inventory.data['plan', 'end_type'].astext == request_args.get('plan.end_type'))
        if request_args.get('attributes:stage'):
            query_set = query_set.filter(Inventory.attributes['stage'].astext == request_args.get('attributes:stage'))
        if request_args.get('attributes:room'):
            query_set = query_set.filter(Inventory.attributes['room'].astext == request_args.get('attributes:room'))
        query_set = query_set.all()

        formatted_query_set = []

        for entry in query_set:
            _set = {
                'ID': entry['ID'],
                'Name': entry['Name'],
                'Quantity': None,
                'Unit': None,
                'End-type': entry['End-type'],
                'Stage': entry['Stage'],
                'Room': entry['Room'],
            }
            stats = []
            for key_1, value_1 in entry['Unit'].items():
                if isinstance(value_1, dict):
                    for key_2, value_2 in value_1.items():
                        stats.append({'unit': key_2, 'quantity': value_2})
                else:
                    stats.append({'unit': key_1, 'quantity': value_1})
            stats = sorted(stats, key=lambda d: d['quantity'])
            if([stat['unit'] for stat in stats][-1]):
                _set['Unit'] = [stat['unit'] for stat in stats][-1]
                _set['Quantity'] = [stat['quantity'] for stat in stats][-1]
            else:
                _set['Unit'] = [stat['unit'] for stat in stats][0]
                _set['Quantity'] = [stat['quantity'] for stat in stats][0]

            formatted_query_set.append(_set)


        if 'archive' in request_args and request_args.get('archive') == 'true':
            return formatted_query_set
        else:
            return [f for f in formatted_query_set if f['Quantity'] > 0]

    def harvest_plant(organization_id, created_by, inventory_id, harvested_quantity, checked_by, weighed_by, approved_by, scale_name = None, timestamp = None, is_partial = False, parent_inventory_id = None):

        batch = (Inventory.query
                          .filter(Inventory.id == inventory_id)
                          .filter(Inventory.organization_id == organization_id)
                          .one_or_none())

        batch_current_stats = Inventory.serialize_inventory_stats(batch.stats)

        if (batch_current_stats.get('unit') != 'plants' or batch.type != 'batch'):
            raise ClientBadRequest({"message": f"Inventory should be a batch in plants stage"}, 400) 
        
        harvested_batch_stats = Inventory.deserialize_inventory_stats(organization_id, 'g-wet', harvested_quantity)
        
        setattr(batch, 'stats', json.loads(json.dumps(harvested_batch_stats, cls=DecimalEncoder)))
        
        db.session.commit()
        
        batch_record_harvest_weight_data = {
            "to_qty": harvested_quantity,
            "from_qty": float(batch_current_stats.get('qty')),
            "checked_by": checked_by,
            "scale_name": scale_name,
            "description": f'All plants harvested. Harvested weight: {harvested_quantity}g' if not is_partial else f'Child batch created: ID {inventory_id}. Harvested weight: {harvested_quantity}g.',
            "weighed_by": weighed_by,
            "approved_by": approved_by,
            "to_qty_unit": "g-wet",
            "from_qty_unit": batch_current_stats.get('unit'), #must be plants
            "to_inventory_id": inventory_id,
            "from_inventory_id": inventory_id,
            "related_inventory_id": parent_inventory_id
        }
        
        act_name = 'batch_record_harvest_weight'
        
        if is_partial:
            act_name = 'batch_record_harvest_weight_partially'
        
        activity = Activity.save_activities(organization_id, batch_record_harvest_weight_data, created_by, act_name, timestamp = timestamp)
        
        Inventory.create_inventory_adjustment(organization_id, created_by, 'plants', 0, inventory_id, act_name, 'batch', activity.id, timestamp = timestamp)
        Inventory.create_inventory_adjustment(organization_id, created_by, 'g-wet', harvested_quantity, inventory_id, act_name, 'batch', activity.id, timestamp = timestamp)
        
        Signature.create_signature(activity.id, organization_id, created_by, 'Checked By', checked_by, activity.id, timestamp = timestamp)
        Signature.create_signature(activity.id, organization_id, created_by, 'Weighed By', weighed_by, activity.id, timestamp = timestamp)
        Signature.create_signature(activity.id, organization_id, created_by, 'Approved By', approved_by, activity.id, timestamp = timestamp)
        
        return batch

    def harvest_multiple(organization_id, created_by, inventory_id, plants_harvested, harvested_quantity, checked_by, weighed_by, approved_by, scale_name = None, timestamp = None):
        
        original_batch = (Inventory.query
                          .filter(Inventory.id == inventory_id)
                          .filter(Inventory.organization_id == organization_id)
                          .one_or_none()
                          )
        
        original_batch_stats_serialized = Inventory.serialize_inventory_stats(original_batch.stats)
        
        if original_batch_stats_serialized.get('qty') < plants_harvested:
            raise ClientBadRequest({"message": f"Current inventory quantity is smaller than the input provided"}, 400) 
        
        create_batch = Batch.duplicate_batch_empty_stats(organization_id, created_by, inventory_id, scale_name, timestamp)
        
        batch = create_batch['inventory']
        activity = create_batch['activity']
        
        if plants_harvested > 0:
            Inventory.transfer_inventory(organization_id, created_by, inventory_id, batch.id, plants_harvested, approved_by, weighed_by, checked_by, activity.id, timestamp)
        
        new_batch = Batch.harvest_plant(organization_id, created_by, batch.id, harvested_quantity, checked_by, weighed_by, approved_by, scale_name, timestamp, True, inventory_id)
        
        return new_batch

    def get_child_inventories_multiple_harvesting_ids(organization_id, parent_inventory_id):
        return (Inventory.query.with_entities(Inventory.id, Inventory.is_child, Inventory.parent_id)
                         .filter(Inventory.parent_id == parent_inventory_id)
                         .filter(Inventory.organization_id == organization_id)
                         .filter(Inventory.is_child == True)
                         .all())

    def merge_multiple_harvest(organization_id, created_by, source_inventory_id, child_inventories_list, approved_by, recorded_by):

        child_batches = (Inventory.query
                             .filter(Inventory.id.in_(child_inventories_list))
                             .filter(Inventory.is_child == True)
                             .all())
        
        activity_name = 'merge_multiple_harvest_batches'
        
        to_inventory = (Inventory.query
                                .filter(Inventory.id == source_inventory_id)
                                .filter(Inventory.is_parent == True)
                                .filter(Inventory.organization_id == organization_id)
                                .one_or_none())

        if not to_inventory:
            raise ClientBadRequest({"message": f"Source inventory is not a parent"}, 400)

        for child_batch in child_batches:
            
            from_inventory_serialized_stats = Inventory.serialize_inventory_stats(child_batch.stats)
            to_inventory_serialized_stats =  Inventory.serialize_inventory_stats(to_inventory.stats)
            
            quantity = from_inventory_serialized_stats.get('qty')
            
            if(to_inventory_serialized_stats.get('qty') <= 0.0 and to_inventory_serialized_stats.get('unit') == 'plants'):
                to_inventory_serialized_stats['unit'] = 'g-wet'
            
            if from_inventory_serialized_stats.get('unit') != to_inventory_serialized_stats.get('unit'):
                raise ClientBadRequest({"message": f"Inventories should be of the same type to merge batches"}, 400)

            if child_batch.attributes.get('stage') != to_inventory.attributes.get('stage'):
                raise ClientBadRequest({"message": f"Inventories should be in the same stage to merge batches"}, 400)


            from_inventory_stats = Inventory.deserialize_inventory_stats(organization_id, 
                                                                        from_inventory_serialized_stats.get('unit'), 
                                                                        from_inventory_serialized_stats.get('qty') - quantity)
            
            to_inventory_stats =  Inventory.deserialize_inventory_stats(organization_id, 
                                                                        to_inventory_serialized_stats.get('unit'), 
                                                                        to_inventory_serialized_stats.get('qty') + quantity)
            
            data = {
                "to_qty": float(quantity),
                "variety": child_batch.variety,
                "from_qty": float(quantity),
                "approved_by": approved_by,
                "recorded_by": recorded_by,
                "to_qty_unit": from_inventory_serialized_stats.get('unit'),
                "from_qty_unit": to_inventory_serialized_stats.get('unit'),
                "to_inventory_id": to_inventory.id,
                "from_inventory_id": child_batch.id
            }
            
            activity = Activity.save_activities(organization_id, data, created_by, activity_name)
            
            setattr(child_batch, 'stats', json.loads(json.dumps(from_inventory_stats, cls=DecimalEncoder)))
            
            Inventory.create_inventory_adjustment(organization_id, created_by, 
                                                    from_inventory_serialized_stats.get('unit'), 
                                                    float(from_inventory_serialized_stats.get('qty') - quantity), 
                                                    child_batch.id, 
                                                    activity_name, 
                                                    child_batch.type,
                                                    activity.id)
            
            setattr(to_inventory, 'stats', json.loads(json.dumps(to_inventory_stats, cls=DecimalEncoder)))
            
            Inventory.create_inventory_adjustment(organization_id, created_by,
                                                    to_inventory_serialized_stats.get('unit'),
                                                    float(quantity),
                                                    to_inventory.id,
                                                    activity_name,
                                                    to_inventory.type,
                                                    activity.id)
            
            setattr(child_batch, 'parent_id', source_inventory_id)
            
        db.session.commit()
        
        return to_inventory

    def weight_adjustment(organization_id, created_by, batch_id, adjusted_weight, approved_by, checked_by, reason_for_modification):
        
        allowed_activities = []
        
        activities_mapping_weight_adjustment = ActivitiesMapping.get_activities_weight_adjustment()
        
        for activity in activities_mapping_weight_adjustment:
            allowed_activities.append(activity.name)
        
        inventory_activities = Inventory.get_all_activities_by_inventory_id(batch_id)
        original_inventory = (Inventory.query
                                       .filter(Inventory.organization_id == organization_id)
                                       .filter(Inventory.id == batch_id)
                                       .one_or_none())
        
        if(original_inventory.type != 'batch'):
            raise ClientBadRequest({"message": f"Inventory must be a batch"}, 400)
        
        original_inventory_stats = Inventory.serialize_inventory_stats(original_inventory.stats)
        original_inventory_new_stats = Inventory.deserialize_inventory_stats(organization_id, original_inventory_stats.get('unit'), adjusted_weight)
        current_quantity = copy.deepcopy(original_inventory_stats.get('qty'))
        setattr(original_inventory, 'stats', json.loads(json.dumps(original_inventory_new_stats, cls=DecimalEncoder)))
        
        original_activity = next((activity for activity in inventory_activities if activity.name in allowed_activities), None)
        
        if(original_inventory_stats.get('unit') not in ['g-wet', 'dry', 'cured', 'crude', 'distilled']):
            raise ClientBadRequest({"message": f"Inventory must be in one of the following stages: ['g-wet', 'dry', 'cured', 'crude', 'distilled']"}, 400)
        
        if(not original_activity):
            raise ClientBadRequest({"message": f"Batch doesn't have one of the allowed activities. Batch should have at least of the following: {allowed_activities}"}, 400)
        
        original_activity = (Activity.query
                             .filter(Activity.id == original_activity.id)
                             .filter(Activity.organization_id == organization_id)
                             .one_or_none())

        inventory_adjustment_activities = Activity.get_inventory_adjustment_activity_by_parent_activity(organization_id, original_activity.id)
        inventory_adjustment_activity = next((act for act in inventory_adjustment_activities if act.data.get('unit') == original_inventory_stats.get('unit')))
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == inventory_adjustment_activity.id)
                                        .filter(Activity.organization_id == organization_id)
                                        .one_or_none())
        
        data_original_activity = original_activity.data
        data_original_activity['to_qty'] = float(adjusted_weight)
        if(data_original_activity.get('description') and (original_activity.name == 'batch_record_harvest_weight' or original_activity.name == 'batch_record_harvest_weight_partially')):
            data_original_activity['description'] = str(data_original_activity['description']).replace(f'{current_quantity}g', f'{adjusted_weight}g')

        data_inventory_adjustment = inventory_adjustment_activity.data
        data_inventory_adjustment['quantity'] = float(adjusted_weight)
 
        Activity.update_activities(original_activity.id, organization_id, data_original_activity, created_by, original_activity.name, reason_for_modification)
        Activity.update_activities(inventory_adjustment_activity.id, organization_id, data_inventory_adjustment, created_by, inventory_adjustment_activity.name, reason_for_modification)
        
        data = {
            'inventory_id': batch_id,
            'from_qty': current_quantity,
            'to_qty': adjusted_weight,
            'modified_activity': original_activity.name,
            'modified_activity_id': original_activity.id,
            'modified_inventory_adjustment_id': inventory_adjustment_activity.id,
            'reason_for_modification': reason_for_modification,
            'description': f'''From: {current_quantity}g {str(original_inventory_stats.get('unit')).replace('g-', '')} to: {adjusted_weight}g''',
            'approved_by': approved_by,
            'checked_by': checked_by
        }
        
        activity = Activity.save_activities(organization_id, data, created_by, 'weight_adjustment')
        Signature.create_signature(activity.id, organization_id, created_by, 'Approved By', approved_by, activity.id)
        Signature.create_signature(activity.id, organization_id, created_by, 'Checked By', checked_by, activity.id)
        
        db.session.commit()
        
        return original_inventory