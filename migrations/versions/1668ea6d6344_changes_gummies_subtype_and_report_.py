"""changes gummies subtype and report section from solid to ingested

Revision ID: 1668ea6d6344
Revises: 7056adecf391
Create Date: 2022-02-09 15:35:12.625795

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = '1668ea6d6344'
down_revision = '7056adecf391'
branch_labels = None
depends_on = None


def upgrade():
    
    connection = op.get_bind()
    connection.execute(
        """
            UPDATE taxonomy_options
            SET data = jsonb_set(data, '{subtype}', '"ingested"', true)
            WHERE name IN ('gummies');

            UPDATE taxonomy_options
            SET data = jsonb_set(data, '{reportSection}', '"ingested"', true)
            WHERE name IN ('gummies');
        """
    )


def downgrade():
    
    connection = op.get_bind()
    connection.execute(
        """
            UPDATE taxonomy_options
            SET data = jsonb_set(data, '{subtype}', '"solid"', true)
            WHERE name IN ('gummies');

            UPDATE taxonomy_options
            SET data = jsonb_set(data, '{reportSection}', '"solid"', true)
            WHERE name IN ('gummies');
        """
    )
