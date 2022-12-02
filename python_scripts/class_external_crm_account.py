"""Endpoints for External CRM Accounts"""

from flask_restful import Resource

from flask import request

from class_errors import ClientBadRequest

from resource_functions import get_collection, get_resource, post_new_resource, post_update_existing_resource

from datetime import datetime
from auth0_authentication import requires_auth
from activities.external_activities.create_external_crm_account import CreateExternalCRMAccount
from activities.external_activities.external_crm_account_update import ExternalCRMAccountUpdate
from activities.external_activities.external_crm_account_update_status import ExternalCRMAccountUpdateStatus
from activities.external_activities.external_crm_account_create_note import ExternalCRMAccountCreateNote
from activities.external_activities.external_crm_account_attach_document import ExternalCRMAccountAttachDocument
from class_external_webhooks import firing_webhooks


class ExternalCrmAccounts(Resource):
    '''
    Class to interact with crm_accounts
    '''
    @requires_auth
    def get(self, current_user, organization_id=1):
        # current_user parameter is unused in this function but it is necessary for Authentication.
        """
        Read all CRM accounts records
        Ex: https://seed-to-sale-dev.appspot.com/v1/organizations/1/external_crm_accounts (GET)
        Result: 
        {
            "data": 
            [
                {
                    "account_type": "license holder",
                    "attributes": {
                        "expiration_date": "2021-02-28T03:00:00.000Z",
                        "status": "awaiting_approval"
                    },
                    "created_by": 183,
                    "email": "zvxem@hotmail.com",
                    "fax": "4379999604",
                    "id": "976",
                    "name": "2360f",
                    "organization_id": 1,
                    "residing_address": {
                        "address1": "4205 Shipp Dr",
                        "address2": "77npo",
                        "city": "Mississauga",
                        "country": "Canada",
                        "postalCode": "L4Z 2Y9",
                        "province": "ON"
                    },
                    "shipping_address": [
                        {
                            "address1": "3803 Calgary Trail NW",
                            "address2": null,
                            "city": "Edmonton",
                            "country": "Canada",
                            "postalCode": "T6J 2M8",
                            "province": "AB"
                        }
                    ],
                    "telephone": "4379993707",
                    "timestamp": "2021-01-04T21:15:49.190987+00:00"
                }
            ],
            "page": 1,
            "per_page": 20,
            "total": 1
        }
        """
        return get_collection(
            current_user=None,
            organization_id=organization_id,
            resource='crm_accounts')

    @requires_auth
    def post(self, current_user, organization_id=1):
        # current_user parameter is unused in this function but it is necessary for Authentication.
        """
        Add new CRM account record
        POST: {
            "account_type": "patient/retailer/distributor/license holder/recreational consumer/researcher/supplier/lab",
            "account_name": "Test",  
            "attributes": {
                "expiration_date": "2027-01-09T05:00:00.000Z"
            }, 
            "organization_id": 1, 
            "email": "asdas@outllook.com", 
            "fax": "12312",  
            "telephone": "12312", 
            "residing_address": {
                "address1": "address 1", 
                "address2": "12312", 
                "city": "12312", 
                "country": "12312", 
                "postalCode": "123123", 
                "province": "23123"
            }, 
            "shipping_address": [
                {
                "address1": "address 1", 
                "address2": "12312", 
                "city": "12312", 
                "country": "12312", 
                "postalCode": "123123", 
                "province": "23123"
                }, 
                {
                "address1": "address 2", 
                "address2": "12312", 
                "city": "12312", 
                "country": "31231", 
                "postalCode": "1233123", 
                "province": "12312"
                }, 
                {
                "address1": "address 3", 
                "address2": "31231", 
                "city": "23123", 
                "country": "12312sa", 
                "postalCode": "123123", 
                "province": "123123"
                }
            ]
            }
        """

        data = request.get_json()

        data['name'] = 'create_external_crm_account'

        data['created_by'] = 1

        data['organization_id'] = organization_id

        data['timestamp'] = datetime.now()
            
        if "attributes" not in data or "expiration_date" not in data["attributes"]:
            if (data['account_type'] == 'patient'):
                raise ClientBadRequest(
                {
                    "code": "missing_required_fields",
                    "description": "Missing one of attributes, attributes['expiration_date']"
                }, 400)
            else:
                data['expiration_date'] = 'notset'
        
        else:
            data['expiration_date'] = data["attributes"]["expiration_date"]

        result = CreateExternalCRMAccount.do_activity(data, None)
        if data.get("account_type") == "patient":
            firing_webhooks(organization_id=organization_id, event='crm_accounts.created', event_data=data)
        return result


class ExternalCrmAccount(Resource):
    @requires_auth
    def get(self, current_user, crm_account_id, organization_id=1):
        # current_user parameter is unused in this function but it is necessary for Authentication.
        """
        Get a specific crm account by id
        Ex: https://seed-to-sale-dev.appspot.com/v1/organizations/1/external_crm_accounts/976 (GET)
        Result: 
        {
            "account_type": "license holder",
            "attributes": {
                "expiration_date": "2021-02-28T03:00:00.000Z",
                "status": "awaiting_approval"
            },
            "created_by": 183,
            "email": "zvxem@hotmail.com",
            "fax": "4379999604",
            "id": "976",
            "name": "2360f",
            "organization_id": 1,
            "residing_address": {
                "address1": "4205 Shipp Dr",
                "address2": "77npo",
                "city": "Mississauga",
                "country": "Canada",
                "postalCode": "L4Z 2Y9",
                "province": "ON"
            },
            "shipping_address": [
                {
                    "address1": "3803 Calgary Trail NW",
                    "address2": null,
                    "city": "Edmonton",
                    "country": "Canada",
                    "postalCode": "T6J 2M8",
                    "province": "AB"
                }
            ],
            "telephone": "4379993707",
            "timestamp": "2021-01-04T21:15:49.190987+00:00"
        }
        """
        return get_resource(
            current_user=None,
            resource_id=crm_account_id,
            organization_id=organization_id,
            resource='crm_accounts')

    @requires_auth
    def patch(self, current_user, crm_account_id, organization_id=1):
        # current_user parameter is unused in this function but it is necessary for Authentication.
        """
        Update existing CRM account record
        """

        data = request.get_json()

        data['crm_account_id'] = crm_account_id

        data['created_by'] = 1

        data['organization_id'] = organization_id

        result = {}
        # To update external crm account
        if data['name'] == 'external_crm_account_update':
            '''
            {
                "name": "external_crm_account_update", 
                "account_name": "Test CRM 51",
                "account_type" : "paitent",
                "expiration_date":"notset",
                "shipping_address": [
                        {
                            "address1": "380 Calgary Trail NW",
                            "address2": null,
                            "city": "Edmonton",
                            "country": "Canada",
                            "postalCode": "T6J 2M8",
                            "province": "AB"
                        }
                ]
            }
            '''
            
            result = ExternalCRMAccountUpdate.do_activity(data, None)

        # To update external crm account status
        if data['name'] == 'external_crm_account_update_status':
            '''
                {
                    "name": "external_crm_account_update_status",
                    "to_status": "approved/awaiting approval/unapproved",
                    "updated_by":"Xyz",
                    "description":"Test"
                }
            '''
            result = ExternalCRMAccountUpdateStatus.do_activity(data, None)

        # To update external crm account attach document
        if data['name'] == 'external_crm_accont_attach_document':
            '''
                {
                    "name": "external_crm_account_attach_document",
                    "upload_id": "257"
                }
            '''
            result = ExternalCRMAccountAttachDocument.do_activity(data, None)

        # To update external crm account create note
        if data['name'] == 'external_crm_account_create_note':
            '''
                {
                    "name": "external_crm_account_create_note",
                    "description":"Test",
                    "detail":"Testing"
                }
            '''
            result = ExternalCRMAccountCreateNote.do_activity(data, None)
        if data.get("account_type") == "patient":
            firing_webhooks(organization_id=organization_id, event='crm_accounts.updated', event_data=data)
        return result
