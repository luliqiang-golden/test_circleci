# Import libraries from parent folder
from activities.crm_account_attach_document import CRMAccountAttachDocument
from constants import USER_ID
from activities.crm_account_update_status import CRMAccountUpdateStatus
from activities.create_crm_account import CreateCRMAccount
from utilities import get_random_user, get_random_date_after_today, select_from_db, get_ramdon_document_id
from db_functions import DATABASE, insert_into_db
from datetime import datetime, timedelta
from random import sample, randint
import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')


def create_crm_account(organization_id, name, status, types):
    try:
        adress = [{
            "city": "Toronto",
            "country": "Canada",
            "postalCode": "M1S 4N4",
            "address1": "40 Executive Court",
            "address2": "",
            "province": "ON",
        }]
        expiration_date = get_random_date_after_today(10, 30)

        args = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            "name": 'create_crm_account',
            "account_name": name,
            "expiration_date":  expiration_date,
            "account_type": types,
            "email": "test@gmail.com",
            "address": adress,
            "telephone": "4162315647",
            "fax": "10209393",
            "status": "awaiting_approval"
        }
        account_result = CreateCRMAccount.do_activity(args, {})

        if (status != "awaiting_approval"):
            update_status_record = {
                "organization_id": organization_id,
                "created_by": USER_ID,
                "name": "crm_account_update_status",
                "crm_account_id": account_result["crm_account_id"],
                "to_status": status,
                "updated_by": get_random_user(organization_id)['email'],
                "description": "",

            }
            CRMAccountUpdateStatus.do_activity(update_status_record, {})

        if (status == "approved"):
            attach_document_crm_account(organization_id, get_ramdon_document_id(), account_result["crm_account_id"])

        return account_result
    except:
        print('error creating account on create_account')
        raise


def create_accounts(org_id):
    try:
        account_types = [
            "lab",
            "supplier",
            "lab",
            "supplier",
            "patient",
            "patient",
            "patient",
            "wholesale",
            "wholesale"
        ]

        names = [
            "A&L Canada Laboratories Inc.",
            "Tweed Inc.",
            "Molecular Science Labs Corp.",
            "Labstat International ULC",
            "SGS Canada Inc.",
            "Joe Smith",
            "Suzanna Maguire",
            "Aurora Cannabis Inc.",
            "Tilray"
        ]

        statuses = [
            "approved",
            "awaiting_approval",
            "unapproved"
        ]

        for index, account_type in enumerate(account_types):
            cur_status = sample(statuses, 1)[0]

            # to ensure that we always have enough options in the supplier & lab picker modals
            if account_type in ['supplier', 'lab']:
                cur_status = 'approved'

            account_result = create_crm_account(
                org_id,
                name=names[index],
                status=cur_status,
                types=account_type
            )
    except:
        raise


def get_crm_accounts_by_organization(organization_id):
    params = {'organization_id': organization_id}

    query = '''
        SELECT *
        FROM crm_accounts AS a
        WHERE a.organization_id=%(organization_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result


def attach_document_crm_account(org_id, upload_id, crm_account_id):
    attachDocumentData = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "crm_account_attach_document",
        "crm_account_id": crm_account_id,
        "upload_id": upload_id,
    }

    CRMAccountAttachDocument.do_activity(attachDocumentData, {})


def get_crm_accounts_by_id(organization_id, id):
    params = {'organization_id': organization_id, 'id': id}

    query = '''
        SELECT *
        FROM crm_accounts AS a
        WHERE a.organization_id=%(organization_id)s AND a.id = %(id)s
    '''

    result = select_from_db(query, params)

    if (result):
        return result[0]


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_accounts(organization_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
