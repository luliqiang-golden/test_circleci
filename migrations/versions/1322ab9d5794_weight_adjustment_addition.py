"""weight adjustment addition

Revision ID: 1322ab9d5794
Revises: d1e1356995f4
Create Date: 2022-09-09 20:31:20.007778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1322ab9d5794'
down_revision = 'ca4844301290'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
            ALTER TABLE activities_mapping 
            ADD COLUMN weight_adjustment bool DEFAULT FALSE;

            INSERT INTO activities_mapping (name, friendly_name)
            VALUES ('weight_adjustment', 'Weight Adjustment');

            INSERT INTO activities_mapping (name, friendly_name)
            VALUES ('batch_record_harvest_weight_partially', 'Batch Record Harvest Weight Partially');
            
            UPDATE activities_mapping SET weight_adjustment = TRUE 
            WHERE name IN ('batch_record_bud_harvest_weight',
            'batch_record_harvest_weight',
            'batch_record_dry_weight',
            'batch_record_cured_weight',
            'batch_record_crude_oil_weight',
            'batch_record_distilled_oil_weight',
            'batch_record_harvest_weight_partially');
        """
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        """
            UPDATE activities_mapping SET weight_adjustment = FALSE 
            WHERE name IN ('batch_record_bud_harvest_weight',
            'batch_record_harvest_weight',
            'batch_record_dry_weight',
            'batch_record_cured_weight',
            'batch_record_crude_oil_weight',
            'batch_record_distilled_oil_weight',
            'batch_record_harvest_weight_partially');
            
            DELETE FROM activities_mapping WHERE name = 'batch_record_harvest_weight_partially';
            
            DELETE FROM activities_mapping WHERE name = 'weight_adjustment';
            
            ALTER TABLE activities_mapping
            DROP COLUMN weight_adjustment;
        """
    )
