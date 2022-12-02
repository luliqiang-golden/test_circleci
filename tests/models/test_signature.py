import json
import secrets

from datetime import datetime, timezone
from models.organization import Organization
from python_scripts.models.activity import Activity
from tests import TestCase
from models.signature import Signature
from app import db
from models.user import User


class TestSignature(TestCase):
    organization_id = 0
    created_by_id = 0
    signed_by_id = 0
    activity_id = 0
    def setUp(self):
        super(TestSignature, self).setUp()

        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        created_by = User(organization_id=self.organization_id, name="Approver", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='creator@wilcompute.com')
        db.session.add(created_by)
        db.session.commit()
        self.created_by_id = created_by.id
        self.signed_by_id  = created_by.id
        
        user_approver = User(organization_id=self.organization_id, name="Approver", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='approver@wilcompute.com')
        db.session.add(user_approver)
        db.session.commit()

        user_recorder = User(organization_id=self.organization_id, name="Recorder", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='recorder@wilcompute.com')
        db.session.add(user_recorder)
        db.session.commit()
        
        activity = Activity(organization_id=self.organization_id,created_by=user_approver.id,timestamp=datetime.now(timezone.utc),name='signature',data='{}')
        db.session.add(activity)
        db.session.commit()
        self.activity_id = activity.id
        
    def test_find(self):
        signature = Signature(field="Reviewed by", organization_id=self.organization_id, timestamp='2021-01-01 00:00:00',
                             created_by=self.created_by_id, signed_by=self.signed_by_id, activity_id=self.activity_id, data="{}")
        db.session.add(signature)
        db.session.commit()

        signature_find = Signature.find(signature.id)
        json_return = "{'json_list': [{'activity_id': " + str(self.activity_id) + ", 'created_by': " + str(self.created_by_id) + ", 'data': '{}', 'field': 'Reviewed by', 'id': " + str(signature.id) +  ", 'organization_id': " + str(self.organization_id) + ", 'signed_by': " + str(self.signed_by_id) + ", 'timestamp': '2021-01-01T00:00:00+00:00'}]}"
        assert str(json.loads(signature_find.response[0]))==json_return
