"""fix subtype and report section fields for cannabinoid, sift, terpene, biomass, distilled and crude

Revision ID: a0258cf85b16
Revises: f4a83c5b3879
Create Date: 2021-12-13 19:43:27.805206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0258cf85b16'
down_revision = 'f4a83c5b3879'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute("""
    
        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{subtype}', '"pure intermediates"', true)
        WHERE name IN ('sift', 'terpene', 'cannabinoid', 'biomass', 'distilled', 'crude');

        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{reportSection}', '"pure intermediates"', true)
        WHERE name IN ('sift', 'terpene', 'cannabinoid', 'biomass', 'distilled', 'crude');

    """)
    pass


def downgrade():
    connection = op.get_bind()
    connection.execute("""
    
        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{subtype}', '"ingested"', true)
        WHERE name IN ('distilled', 'crude');

        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{reportSection}', '"ingested"', true)
        WHERE name IN ('distilled', 'crude');
        
        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{subtype}', '"other"', true)
        WHERE name IN ('sift', 'terpene', 'cannabinoid', 'biomass');

        UPDATE taxonomy_options
        SET data = jsonb_set(data, '{reportSection}', '"other"', true)
        WHERE name IN ('sift', 'terpene', 'cannabinoid', 'biomass');

    """)
    pass
