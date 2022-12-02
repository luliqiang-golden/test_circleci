# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from db_functions import DATABASE
from utilities import select_from_db

from constants import USER_ID
from class_errors import DatabaseError
from random import randint
from create_crm_account import get_crm_accounts_by_id


from utilities import get_random_room, get_random_date_before_today
from activities.create_shipment import CreateShipment
from activities.order_item_add_shipment import OrderItemAddShipment
from activities.order_item_map_to_lot_item import OrderItemMapToLotItem
from activities.shipment_update_tracking_number import ShipmentUpdateTrackingNumber
from activities.shipment_packaged import ShipmentPackaged
from activities.shipment_delivered import ShipmentDelivered
from activities.shipment_shipped import ShipmentShipped
from activities.shipment_update_shipping_address import ShipmentUpdateShippingAddress
from activities.shipment_update_shipped_date import ShipmentUpdateShippedDate
from activities.shipment_update_delivered_date import ShipmentUpdateDeliveredDate



def create_shipments(organizarion_id):
    try:
        shipment_data = get_shipment_data(organizarion_id)
        
        crm_id = ''
        shipment_id = ''
        deliver = True
        shipments = []
        for data in shipment_data:        
            if (crm_id != data['crm_account_id']):
                shipment_id = create_shipment(organizarion_id, data['crm_account_id'])['shipment_id']
                shipments.append(shipment_id)
                update_tracking_number(organizarion_id, shipment_id)
                update_shipment_address(organizarion_id, shipment_id, data['crm_account_id'])
                close_shipment(organizarion_id, shipment_id)
        
            add_shipment_to_order_item(organizarion_id, shipment_id, data['order_item_id'])
            map_order_item_to_lot_item(organizarion_id, data['order_item_id'], data['inventory_id']) 
            
            crm_id = data['crm_account_id']
            

        for shipment_id in shipments:        
            collect_shipment(organizarion_id, shipment_id)
            update_shipped_date(organizarion_id, shipment_id)
            if (deliver):
                deliver_shipment(organizarion_id, shipment_id)
                update_delivered_date(organizarion_id, shipment_id)
                deliver = not deliver
    except:
        raise



def get_shipment_data(organization_id):
    params = {'organization_id': organization_id}
    query = '''        
        SELECT o.crm_account_id, o.id as order_id, oi.id as order_item_id, oi.sku_name,
               (SELECT id 
                FROM inventories 
                WHERE organization_id = o.organization_id AND type = 'lot item' AND data->>'sku_name'=oi.sku_name ORDER BY RANDOM() LIMIT 1
               ) as inventory_id
        FROM orders AS o
        INNER JOIN order_items AS oi ON o.id = oi.order_id AND o.organization_id = oi.organization_id
        INNER JOIN inventories AS i ON i.organization_id = oi.organization_id AND i.type = 'lot item' AND i.data->>'sku_name' = oi.sku_name
        WHERE o.organization_id = %(organization_id)s AND o.status = 'approved'
        GROUP BY o.crm_account_id, oi.id, o.id, oi.sku_name
    '''
    
    return select_from_db(query, params)


def create_shipment(organizarion_id, crm_account_id):
    createShipmentData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "create_shipment",
      "crm_account_id": crm_account_id
    }
    
    try:
        return CreateShipment.do_activity(createShipmentData, {})
    except:
        print('error creating shipment on create_shipment')
        raise 

def add_shipment_to_order_item(organizarion_id, shipment_id, order_item_id):
    addShipmentToOrderItemData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "order_item_add_shipment",
      "shipment_id": shipment_id, 
      "order_item_id": order_item_id,
      'quantity_filled': 1,
    }
    
    try:
        return OrderItemAddShipment.do_activity(addShipmentToOrderItemData, {})
    except:
        print('error adding shipment to order item on create_shipment')
        raise 

def map_order_item_to_lot_item(organizarion_id, order_item_id, inventory_id):
    mapOrderItemToLotItemData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "order_item_map_to_lot_item",      
      "order_item_id": order_item_id,
      "inventory_id": inventory_id 
    }
    
    try:
        return OrderItemMapToLotItem.do_activity(mapOrderItemToLotItemData, {})
    except:
        print('error mapping order item to lot item on create_shipment')
        raise 

def update_tracking_number(organizarion_id, shipment_id):
    updateTrackingNumberData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_update_tracking_number",      
      "shipment_id": shipment_id,
      "to_tracking_number": 'TRK{}JG'.format(str(randint(1000000000,2000000000)))
    }
    
    try:
        return ShipmentUpdateTrackingNumber.do_activity(updateTrackingNumberData, {})
    except:
        print('error updating tracking number on create_shipment')
        raise 

def close_shipment(organizarion_id, shipment_id):
    closeShipmentData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_packaged",
      "shipment_id": shipment_id, 
      "to_room": get_random_room(organizarion_id)['name']
    }
    
    try:
        return ShipmentPackaged.do_activity(closeShipmentData, {})
    except:
        print('error closing shipment on create_shipment')
        raise 

def deliver_shipment(organizarion_id, shipment_id):
    deliverShipmentData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_delivered",
      "shipment_id": shipment_id
    }
    
    try:
        return ShipmentDelivered.do_activity(deliverShipmentData, {})
    except:
        print('error delivering shipment on create_shipment')
        raise 

def collect_shipment(organizarion_id, shipment_id):
    collectShipmentData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_shipped",
      "shipment_id": shipment_id
    }
    
    try:
        return ShipmentShipped.do_activity(collectShipmentData, {})
    except:
        print('error collecting shipment on create_shipment')
        raise 

def update_shipment_address(organization_id, shipment_id, crm_account):    
    updateShipmentAddressData = {
      "organization_id": organization_id,
      "created_by": USER_ID,
      "name": "shipment_update_shipping_address",
      "shipment_id": shipment_id,
      "to_shipping_address": get_crm_accounts_by_id(organization_id, crm_account)['data']['address'][0]
    }
    
    try:
        return ShipmentUpdateShippingAddress.do_activity(updateShipmentAddressData, {})
    except:
        print('error updating shipment address on create_shipment')
        raise 


def update_shipped_date(organizarion_id, shipment_id):
    updateShippedDateData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_update_shipped_date",
      "shipment_id": shipment_id,
      "to_shipped_date": get_random_date_before_today(60,90)
    }
    
    try:
        return ShipmentUpdateShippedDate.do_activity(updateShippedDateData, {})
    except:
        print('error updating shipped date on create_shipment')
        raise 


def update_delivered_date(organizarion_id, shipment_id):
    updateDeliveredDateData = {
      "organization_id": organizarion_id,
      "created_by": USER_ID,
      "name": "shipment_update_delivered_date",
      "shipment_id": shipment_id,
      "to_delivered_date": get_random_date_before_today(5,50)
    }
    
    try:
        return ShipmentUpdateDeliveredDate.do_activity(updateDeliveredDateData, {})
    except:
        print('error updating delivered date on create_shipment')
        raise 


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_shipments(organization_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
