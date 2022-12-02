'''This module contains database schema model for webhook table'''
import json
import requests
from app import db
from sqlalchemy import DateTime, func
from class_errors import ClientBadRequest
from models.activity import Activity

class Webhook(db.Model):
    __tablename__ = 'webhook_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    created_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())

    @staticmethod
    def firing_webhooks(event, event_data):
        webhooks = Webhook.query.filter(Webhook.event==event).all()
        if len(webhooks) >= 1:
            for webhook in webhooks:
                url = webhook.url
                payload = {
                    "event": str(webhook.event),
                    "event_data": json.loads(json.dumps(event_data, default=str))
                }
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, json=payload)
            return {"message": "successfully fired"}


