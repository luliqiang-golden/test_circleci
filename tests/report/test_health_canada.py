import secrets
from decimal import Decimal
from tests import TestCase
from models.user import User
from models.organization import Organization
from reporting import CanadaCSV
from app import db

class TestCanadaCSV(TestCase):
    organization_id = 0
    created_by_id = 0
    def setUp(self):
        uniq_org_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=uniq_org_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        created_by = User(organization_id=self.organization_id, name="Approver", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='creator@wilcompute.com')
        db.session.add(created_by)
        db.session.commit()
        self.created_by_id = created_by.id
        
    def test_process_report_hcr(self):
        month = '11'
        year = '2021'
        organization_id = self.organization_id
        created_by = self.created_by_id
        report_id =  CanadaCSV.process_report_sqa(month, year, organization_id, created_by)
        self.assertEqual(report_id[0][0],1)

    def test_size_get_report(self):
        month = '11'
        year = '2021'
        organization_id = self.organization_id
        created_by = self.created_by_id
        CanadaCSV.process_report_sqa(month, year, organization_id, created_by)
        records = CanadaCSV.get_report_sqa(month, year, organization_id)
        self.assertEqual(len(list(records)),1)

    def test_get_report(self):
        month = '11'
        year = '2021'
        organization_id = self.organization_id
        created_by = self.created_by_id
        CanadaCSV.process_report_sqa(month, year, organization_id, created_by)
        records = list(CanadaCSV.get_report_sqa(month, year, organization_id))
        self.assertEqual(records[0]["organization_id"],self.organization_id)
        self.assertEqual(records[0]["report_period_month"],'11')
        self.assertEqual(records[0]["report_period_year"],'2021')
        self.assertEqual(records[0]["created_by"],self.created_by_id)
