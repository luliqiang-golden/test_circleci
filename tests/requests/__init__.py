import auth0_authentication
import secrets

from flask_restful import Api
from unittest.mock import MagicMock
from models.taxonomies import Taxonomies
from models.taxonomy_options import TaxonomyOptions
from tests import TestCase
from app import db
from models.user import User
from models.organization import Organization
from random import randrange

class AuthenticatedTestCase(TestCase):
    def setUp(self):
        super(AuthenticatedTestCase, self).setUp()
        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        
        current_user = User(organization_id=organizations.id, name="Current User", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='current@wilcompute.com')
        db.session.add(current_user)
        db.session.flush()
        self.current_user_id = current_user.id
        auth0_authentication.get_user = MagicMock(return_value={'user_id': self.current_user_id})
        
        taxonomy = Taxonomies(organization_id=organizations.id,
                              created_by=current_user.id,
                              name='stats',
                              data='{}')
        db.session.add(taxonomy)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='seeds',
                            data={"type": "standard", "parent": "", "stages": ["planning", "germinating"], "enabled": True, "subtype": "", "metricMass": "un", "friendlyName": "seeds", "cannabisClass": "cannabis plants seeds", "reportSection": "seeds", "isFinalProduct": False},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='plants',
                            data={"type": "standard", "parent": "", "stages": ["planning", "propagation", "vegetation", "flowering"], "enabled": True, "subtype": "", "metricMass": "un", "friendlyName": "plants", "cannabisClass": "cannabis plants", "reportSection": "plants", "isFinalProduct": False},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='g-wet',
                            data={"type": "standard", "parent": "", "stages": ["planning", "harvesting"], "enabled": True, "subtype": "", "metricMass": "g", "friendlyName": "(wet)", "cannabisClass": "fresh cannabis", "reportSection": "fresh_cannabis", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='dry',
                            data={"type": "standard", "parent": "g-dry", "stages": ["planning", "drying"], "enabled": True, "subtype": "", "metricMass": "g", "friendlyName": "dry (dry material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='cured',
                            data={"type": "standard", "parent": "g-dry", "stages": ["planning", "curing"], "enabled": True, "subtype": "", "metricMass": "g", "friendlyName": "dry (cured material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='hash',
                            data={"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": True, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='crude',
                            data={"type": "standard", "parent": "g-oil", "stages": ["planning", "extracting_crude_oil"], "enabled": True, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (crude material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='distilled',
                            data={"type": "standard", "parent": "g-oil", "stages": ["planning", "distilling"], "enabled": True, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (distilled material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()


        taxonomy_options = TaxonomyOptions(
                            organization_id=organizations.id,
                            name='terpene',
                            data={"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (terpene)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True},
                            created_by=current_user.id,
                            taxonomy_id=taxonomy.id)
        db.session.add(taxonomy_options)
        db.session.commit()

