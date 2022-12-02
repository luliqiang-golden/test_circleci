"""Endpoints for External Orders"""
import json
import requests
from flask_restful import Resource
from flask import request, jsonify
from activities.external_activities.manage_webhook import WebhookSubscribe
from resource_functions import delete_subscription, get_collection
from auth0_authentication import requires_auth
from db_functions import DATABASE
from class_errors import DatabaseError


class WebhookSubscription(Resource):

    @requires_auth
    def post(self, current_user):
        """
        Create a new subscribe entry
        """

        user = current_user['org_roles'][0]
        user_id = user['user_id']
        organization_id = user['organization']['id']
        data = request.get_json()

        data['created_by'] = user_id  # current_user['user_id'],

        data['name'] = 'create_subscribe_entry'

        data['organization_id'] = organization_id

        return WebhookSubscribe.do_activity(data, None)


class WebhookUnsubscription(Resource):

    @requires_auth
    def delete(self, current_user, webhook_record_id, organization_id=None):
        """Delete subscription"""
        return delete_subscription(
            resource='Webhook_subscriptions',
            resource_id=webhook_record_id,
            organization_id=organization_id)


def firing_webhooks(current_user=None, organization_id=None, event=None, event_data=None):

    results = []
    cursor = DATABASE.dedicated_connection().cursor()
    query = f"SELECT * FROM public.webhook_subscriptions where event = '{event}'"
    try:
        cursor.execute(query)
        cursor_data = cursor.fetchall()
        [results.append(dict(_)) for _ in cursor_data]
        for row in results:
            url = row['url']
            payload = {"event": str(row['event']), "event_data": json.loads(json.dumps(event_data, default=str))}
            headers = {
                'Content-Type': 'application/json'
            }
            requests.request("POST", url, headers=headers, json=payload)
        return {"message": "successfully fired"}
    except Exception as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": 'database_error',
                "message": "There was an error {}".format(error.args[0])
            }, 500)
