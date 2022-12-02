"""add final extraction stage option

Revision ID: dee995691400
Revises: 109986603645
Create Date: 2022-03-31 17:01:51.123369

"""
from sqlalchemy import func
from alembic import op
from models.taxonomies import Taxonomies
from models.taxonomy_options import TaxonomyOptions

# revision identifiers, used by Alembic.
revision = 'dee995691400'
down_revision = '109986603645'
branch_labels = None
depends_on = None

def upgrade():
    stage = TaxonomyOptions.query.filter_by(name='final_extraction').first()

    if not stage:
        connection = op.get_bind()
        queryset = (
                    Taxonomies.query
                    .with_entities(Taxonomies.id, 
                                Taxonomies.organization_id)
                    .filter(Taxonomies.name == 'stages')
            ).all()

        taxonomy_options_insert = [{
                            'organization_id': entry[1],
                            'created_by': 1,
                            'timestamp': func.now(),
                            'name': 'final_extraction',
                            'data': {"description": "", "allowed_inventory_types": ["batch"], "allowed_previous_stages": []},
                            'taxonomy_id': entry[0]} for entry in queryset]
        
        connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert))

def downgrade():
    connection = op.get_bind()
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'final_extraction'))