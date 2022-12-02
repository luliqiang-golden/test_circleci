# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from random import randint
from db_functions import DATABASE, insert_into_db
from utilities import get_random_date_before_today, get_ramdon_document_id
from activities.create_order import CreateOrder
from activities.order_update_account import OrderUpdateAccount
from activities.order_update_status import OrderUpdateStatus
from create_crm_account import get_crm_accounts_by_organization
from create_order_item import  create_order_item, get_skus_by_organization
from activities.order_attach_document import OrderAttachDocument

from constants import USER_ID
from class_errors import DatabaseError

def get_sku(sku_list, quantity, skus = None):
    if (skus == None):
        skus = []
    found = False
    
    while (not found):
        index = randint(0, len(sku_list)-1)
        sku = sku_list[index]
        stock = sku['stock']
        # check if i already chose the sku or it's the last one
        if (len(list(filter(lambda x: x['sku'] == sku["name"], skus))) == 0 or len(sku_list) == 1):
            found = True
    
    max_quantity = 0
    if (stock > 3): 
        max_quantity = 3
    else:
        max_quantity = stock

    item_quantity = randint(1,max_quantity)

    sku['stock'] = stock-item_quantity

    if (sku['stock'] == 0):
        sku_list = list(filter(lambda x: x['stock'] > 0, sku_list))

    skus.append({'sku': sku,
                 'item_quantity': item_quantity,
                })

    quantity = quantity - 1

    if (quantity > 0 and len(sku_list) > 1):
        object_return = get_sku(sku_list, quantity, skus)
    else:
        object_return =  { 
            'skus': skus,
            'sku_list': sku_list
        }

    return object_return


def create_orders(organization_id):
    try:
        crm_accounts = get_crm_accounts_by_organization(organization_id)
        skus = get_skus_by_organization(organization_id)  
      
        sku_with_stock = list(filter(lambda x: x['stock'] > 0, skus))

        if (len(sku_with_stock) > 0):
            sku_quantity = 2
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="wholesale",
                    order_placed_by="Alexander",
                    status="approved",
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']
                        },
                        # this item will be shipped
                        {
                            "sku": skus[1]['sku'],
                            "quantity": skus[1]['item_quantity']

                        }
                    ]

            )

        if (len(sku_with_stock) > 0):
            sku_quantity = 2
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="wholesale",
                    order_placed_by="Joe",
                    status="cancelled",  
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        },
                        {
                            "sku": skus[1]['sku'],
                            "quantity": skus[1]['item_quantity']
                        }
                    ]       
                )

        if (len(sku_with_stock) > 0):
            sku_quantity = 3
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="wholesale",
                    order_placed_by="Rafael", 
                    status="awaiting_approval",           
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        },
                        {
                            "sku": skus[1]['sku'],
                            "quantity": skus[1]['item_quantity']
                        },
                        {
                            "sku": skus[2]['sku'],
                            "quantity": skus[2]['item_quantity']
                        } 
                    ]
                )        
        

        if (len(sku_with_stock) > 0):
            sku_quantity = 3
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="patient",
                    order_placed_by="Rafael",   
                    status="approved",        
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        },
                        {
                            "sku": skus[1]['sku'],
                            "quantity": skus[1]['item_quantity']

                        },
                        {
                            "sku": skus[2]['sku'],
                            "quantity": skus[2]['item_quantity']

                        }
                    ]
                )

        if (len(sku_with_stock) > 0):
            sku_quantity = 3
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):        
                create_order(
                    # same account to the last one, in order to generate good data for shipment
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="wholesale",
                    order_placed_by="JG", 
                    status="approved",         
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        },
                        {
                            "sku": skus[1]['sku'],
                            "quantity": skus[1]['item_quantity']

                        },
                        # this item will be shipped
                        {
                            "sku": skus[2]['sku'],
                            "quantity": skus[2]['item_quantity']

                        }
                    ]
                )

        # for porpuse recall
        if (len(sku_with_stock) > 0):
            sku_quantity = 1
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):        
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="patient",
                    order_placed_by="Harren",   
                    status="approved",        
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        }
                    ]
                )
        
        if (len(sku_with_stock) > 0):
            sku_quantity = 2
            resp = get_sku(sku_with_stock, sku_quantity)
            sku_with_stock = resp['sku_list']
            skus = resp['skus']
            if (len(skus) == sku_quantity):        
                crm_account = crm_accounts[randint(0, len(crm_accounts)-1)]
                create_order(
                    crm_account=crm_account,
                    organization_id=organization_id,
                    order_type="wholesale",
                    order_placed_by="Andrew",   
                    status="approved",        
                    items=[
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        },
                        {
                            "sku": skus[0]['sku'],
                            "quantity": skus[0]['item_quantity']

                        }
                    ]
                )
    except:
        raise
    



def create_order(crm_account, organization_id, order_type, order_placed_by, status, items):
    try:
        order = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": "create_order",
        'crm_account_id': crm_account['id'],
        'crm_account_name': crm_account['name'],
        'shipping_address': crm_account["data"]["address"][0],
        'order_placed_by': order_placed_by,
        'order_received_date': get_random_date_before_today(1, 30),
        'order_type': order_type,
        }
        order_result = CreateOrder.do_activity(order, {})

       
        for x in range(len(items)):
            create_order_item(organization_id, order_result["order_id"], items[x]["sku"], items[x]["quantity"])

        
        order_change_status = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            "name": 'order_update_status',
            "order_id": order_result["order_id"],
            "to_status": status,
        }
        OrderUpdateStatus.do_activity(order_change_status, {})



        if (status == "approved"):
            attach_document_order(organization_id, get_ramdon_document_id(), order_result["order_id"], crm_account["id"])

    except:
        print('error creating order on create_order')
        raise 
        

def attach_document_order(org_id, upload_id, order_id, crm_account_id):
    attachDocumentData = {
        "organization_id": org_id,
        "created_by": USER_ID,
        'name': 'order_attach_document',
        'order_id': order_id,
        'upload_id': upload_id,
        'crm_account_id': crm_account_id,
    }
    OrderAttachDocument.do_activity(attachDocumentData, {})
        



       



if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_orders(organization_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
