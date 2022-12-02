"""adds gummies as endtype

Revision ID: fb216d3fe2a5
Revises: 448ef2df18f4
Create Date: 2022-02-03 21:47:42.304623

"""
from sqlalchemy import func
from alembic import op
from models.taxonomies import Taxonomies
from models.taxonomy_options import TaxonomyOptions


# revision identifiers, used by Alembic.
revision = 'fb216d3fe2a5'
down_revision = '448ef2df18f4'
branch_labels = None
depends_on = None


def upgrade():
    
    connection = op.get_bind()
    
    queryset = (
                Taxonomies.query
                .with_entities(Taxonomies.id, 
                               Taxonomies.organization_id)
                .filter(Taxonomies.name == 'stats')
        ).all()
    
    taxonomy_options_insert = [{'organization_id': entry[1],
                         'created_by': 1,
                         'timestamp': func.now(),
                         'name': 'gummies',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": True, "subtype": "solid", "metricMass": "g", "friendlyName": "extract (gummies)", 
                                "cannabisClass": "cannabis extracts", "reportSection": "solid", "isFinalProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]
    
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert))


def downgrade():
    
    connection = op.get_bind()
    
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'gummies'))
    
