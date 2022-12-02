'''This module contains database schema model for order items table'''
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm.util import aliased
from sqlalchemy.sql.sqltypes import Integer, String
from app import db
from sqlalchemy import DateTime, func
from models.inventory.lot import Lot
from models.inventory.lot_item import LotItem
from models.skus import Skus
from models.activity import Activity

class OrderItem(db.Model):
    
    '''Definition of order items table'''
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    sku_id = db.Column(db.Integer)
    sku_name = db.Column(db.String)
    order_id = db.Column(db.Integer)
    data = db.Column(JSONB)
    created_by = db.Column(db.Integer)
    shipment_id = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    ordered_stats = db.Column(JSONB)
    variety = db.Column(db.String)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    shipped_stats = db.Column(JSONB)
    status = db.Column(db.String)
    quantity = db.Column(db.Integer)
    filled = db.Column(db.Integer)
    price = db.Column(db.Numeric(14,2))
    excise_tax = db.Column(db.Numeric(14,2))
    provincial_tax = db.Column(db.Numeric(14,2))
    attributes = db.Column(JSONB)
    discount = db.Column(db.Numeric(14,2))
    shipping_value = db.Column(db.Numeric(14,2))
    
    def validate_lots_quantity(lots, sku_id):
        
        lot_ids = [lot['id'] for lot in lots]

        lot = aliased(Lot)

        queryset = (LotItem.query
                    .add_entity(lot.id).join(lot, lot.id == LotItem.data['from_inventory_id'].astext.cast(Integer))
                    .join(Skus, LotItem.data['sku_id'].astext.cast(Integer) == Skus.id)
                    .filter(lot.id.in_(lot_ids))
                    .filter(Skus.id == sku_id)
                    .filter(LotItem.data['order_item_id'] == None)
                    .filter(LotItem.type == 'lot item')
                    .filter(lot.type == 'lot')
                    .all())

        lot_item_grouped_by_lot_id = defaultdict(list)

        # group lot items per lot id to make it easier to compare/validate quantity
        for obj in queryset:
            lot_item_grouped_by_lot_id[obj.id].append(obj.LotItem)

        # check if request is valid before taking any action in the database
        for lots in lots:
            if(lots['quantity_selected'] > len(lot_item_grouped_by_lot_id[lots['id']])):
                return False, lots['id']

        return True, lot_item_grouped_by_lot_id

    def validate_request_total_quantity(order_item_id, lots):
        
        total_quantity = 0
        for lot in lots:
            total_quantity += int(lot['quantity_selected'])
        
        order_item_details = (OrderItem.query
                        .filter(OrderItem.id == order_item_id).first())
        
        order_item_quantity = order_item_details.quantity
        
        if(total_quantity != order_item_quantity):
            return False
        
        return True

    def get_order_item_quantity_to_be_filled(external_order_item_id):
        """Returns quantity which are fillable

        Args:
            order_item_id (int): id of Order Item

        Returns:
            int: fillable quantity
        """
        order_item_details = (OrderItem.query
                        .filter(OrderItem.data['external_order_item_id'].astext.cast(String) == str(external_order_item_id)).first())
        
        if order_item_details:
            filled = order_item_details.filled
            quantity = order_item_details.quantity
            
            if filled is None:
                filled = 0
            
            if quantity is None:
                quantity = 0
            return order_item_details.id, quantity - filled
        
        return None, 0
    
    
    def fill_order_item(organization_id, order_item_id, sku_id, lots, created_by):

            quantity_filled = 0
            lot_item_grouped_by_lot_id = OrderItem.validate_lots_quantity(lots, sku_id)[1]
            
            lot_item_mappings  = []
            activities_mapping = []
            
            # updates inventory table to relate order item and lot item
            for lots in lots:
                for i in range(int(lots['quantity_selected'])):

                    lot_item_grouped_by_lot_id[lots['id']][i].data['order_item_id'] = order_item_id
                    
                    lot_item_mappings.append({'id': lot_item_grouped_by_lot_id[lots['id']][i].id, 
                                        'data': lot_item_grouped_by_lot_id[lots['id']][i].data})

                    data_order_item_map_to_lot_item = {
                        'inventory_id': lot_item_grouped_by_lot_id[lots['id']][i].id,
                        'order_item_id': order_item_id
                    }

                    quantity_filled += 1
                    
                    activities_mapping.append(Activity(
                        organization_id=organization_id, 
                             created_by=created_by,
                             timestamp=datetime.now(),
                             name= 'order_item_map_to_lot_item', 
                             data=data_order_item_map_to_lot_item
                    ))

            db.session.bulk_update_mappings(LotItem, lot_item_mappings)
            db.session.bulk_save_objects(activities_mapping)
            db.session.commit()

            skus = Skus.query.filter(Skus.id == sku_id).first()
            skus.current_inventory = skus.current_inventory - quantity_filled
            skus.attributes['reserved'] = skus.attributes['reserved'] - quantity_filled
            db.session.query(Skus).filter(Skus.id == sku_id).update({
                'attributes': skus.attributes,
                'current_inventory': skus.current_inventory
            })
            db.session.commit()

            return quantity_filled

    def add_order_item_shipment(organization_id, created_by, order_item_id, shipment_id, quantity_filled):

        order_item = OrderItem.query.filter(OrderItem.id == order_item_id).first()

        for k1, v1 in order_item.ordered_stats.items():
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    order_item.ordered_stats[k1][k2] = float(Decimal(v2) * quantity_filled)
            else:
                order_item.ordered_stats[k1] = float(Decimal(v1) * quantity_filled)

        OrderItem.query.filter(OrderItem.id == order_item_id).update({
                'shipment_id': shipment_id,
                'filled': quantity_filled,
                'shipped_stats': order_item.ordered_stats
        })

        data = {
            'order_item_id': order_item_id,
            'shipment_id': shipment_id,
            'quantity_filled': quantity_filled
        }
         
        Activity.save_activities(organization_id, data, created_by, 'order_item_add_shipment')


    def get_available_stock(self, created_by, organization_id, params):

        lot_item = aliased(LotItem)

        # create reserved field if not exists
        for sku in Skus.query.filter(Skus.attributes['reserved'] == None):
            sku.attributes = deepcopy(sku.attributes)
            sku.attributes['reserved'] = 0
            db.session.commit()

        queryset = (
            Skus.query
            .with_entities(
                Skus.id.label('sku_id'),
                Skus.name.label('sku_name'),
                Skus.price.label('sku_price'),
                Skus.variety.label('sku_variety'),
                Skus.timestamp.label('sku_timestamp'),
                Skus.sales_class.label('sku_sales_class'),
                Skus.attributes['status'].label('sku_status'),
                Skus.target_qty.label('sku_target_qty'),
                Skus.target_qty_unit.label('sku_target_qty_unit'),
                Skus.attributes['reserved'].label('sku_reserved'),
                func.count(lot_item.id).label('count'))
            .join(lot_item, Skus.id == lot_item.data['sku_id'].astext.cast(Integer))
            .filter(
                Skus.variety == lot_item.variety,
                lot_item.data['order_item_id'] == None,
                Skus.organization_id == organization_id
            ).group_by(Skus.id, Skus.name)
        )

        if params.get('sales_class'):
            queryset = queryset.filter(Skus.sales_class==params.get('sales_class'))
        if params.get('variety'):
            queryset = queryset.filter(Skus.variety==params.get('variety'))
        if params.get('status'):
            queryset = queryset.filter(Skus.attributes['status'].astext==params.get('status'))
        if params.get('target_qty_unit'):
            queryset = queryset.filter(Skus.target_qty_unit==params.get('target_qty_unit'))

        queryset = queryset.all()
        return queryset
