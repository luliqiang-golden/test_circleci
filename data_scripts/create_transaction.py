from class_errors import DatabaseError
from activities.update_transaction_total_amount import UpdateTransactionTotalAmount
from activities.record_transaction_allocation import RecordTransactionAllocation
from activities.record_transaction import RecordTransaction
from constants import USER_ID
from utilities import select_from_db, get_random_date_after_today, get_users_by_organization, get_random_inventory
from db_functions import DATABASE, DatabaseError
from random import randint
import psycopg2.extras
import psycopg2
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def create_transaction_for_consumable_lot(
    organization_id,
    vendor_id,
    purchase_order
):

    transaction = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        'name': 'record_transaction',
        'crm_account_id': vendor_id,
        'purchase_order': purchase_order,
    }

    record_transaction = RecordTransaction.do_activity(transaction, {})

    return record_transaction['transaction_id']


def create_transaction_allocation(
        organization_id,
        transaction_id,
        amount,
        consumable_lot_id):

    transaction_allocation = {
        'name': 'record_transaction_allocation',
        'type': 'debit',
        'created_by': USER_ID,
        'organization_id': organization_id,
        'transaction_id': transaction_id,
        'amount': amount,
        'consumable_lot_id': consumable_lot_id
    }

    record_transaction_allocation = RecordTransactionAllocation.do_activity(
        transaction_allocation, {})


def update_transaction(
    organization_id,
    to_transaction_id,
    amount
):

    update_transaction = {
        'name': 'update_transaction_total_amount',
        'to_transaction_id': to_transaction_id,
        'amount': amount,
        'organization_id': organization_id,
        'created_by': USER_ID
    }

    update_transaction_amount = UpdateTransactionTotalAmount.do_activity(
        update_transaction, {})
