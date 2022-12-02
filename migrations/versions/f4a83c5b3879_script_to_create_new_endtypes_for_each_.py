"""script to create new endtypes for each organization into db

Revision ID: f4a83c5b3879
Revises: 488ac58167f5
Create Date: 2021-12-11 02:09:18.044465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a83c5b3879'
down_revision = '488ac58167f5'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
        --seeds
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "", "stages": ["planning", "germinating"], "enabled": true, "subtype": "", "metricMass": "un", "friendlyName": "seeds", "cannabisClass": "cannabis plants seeds", "reportSection": "seeds", "isFinalProduct": false}',
        	'seeds',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'seeds');
        --plants
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "", "stages": ["planning", "propagation", "vegetation", "flowering"], "enabled": true, "subtype": "", "metricMass": "un", "friendlyName": "plants", "cannabisClass": "cannabis plants", "reportSection": "plants", "isFinalProduct": false}',
        	'plants',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'plants');
        --g-wet
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "", "stages": ["planning", "harvesting"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "(wet)", "cannabisClass": "fresh cannabis", "reportSection": "fresh_cannabis", "isFinalProduct": true}',
        	'g-wet',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'g-wet');
        --dry
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "g-dry", "stages": ["planning", "drying"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "dry (dry material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": true}',
        	'dry',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'dry');
        --cured
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "g-dry", "stages": ["planning", "curing"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "dry (cured material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": true}',
        	'cured',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'cured');
        --crude
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
            '{"type": "standard", "parent": "g-oil", "stages": ["planning", "extracting_crude_oil"], "enabled": true, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (crude material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": true}',
            'crude',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'crude');
        --distilled
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "standard", "parent": "g-oil", "stages": ["planning", "distilling"], "enabled": true, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (distilled material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": true}',    
        	'distilled',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'distilled');
        --hash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',    
        	'hash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hash');
        --bubbleHash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubble hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'bubbleHash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash');
        --liveBubbleHash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live bubble hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveBubbleHash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveBubbleHash');
        --hashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hashRosin');
        --liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveRosin');
        --liveHashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live hash rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveHashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveHashRosin');
        --terpene
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (terpene)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'terpene',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'terpene');
        --biomass
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (biomass)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'biomass',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'biomass');
        --sift
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (sift)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'sift',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'sift');
        --cannabinoid
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (cannabinoid)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'cannabinoid',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'cannabinoid');
    """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
    """
        DELETE FROM taxonomy_options WHERE name = 'cannabinoid';
        DELETE FROM taxonomy_options WHERE name = 'sift';
        DELETE FROM taxonomy_options WHERE name = 'biomass';
        DELETE FROM taxonomy_options WHERE name = 'terpene';
        DELETE FROM taxonomy_options WHERE name = 'liveHashRosin';
        DELETE FROM taxonomy_options WHERE name = 'liveRosin';
        DELETE FROM taxonomy_options WHERE name = 'hashRosin';
        DELETE FROM taxonomy_options WHERE name = 'liveBubbleHash';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash';
        DELETE FROM taxonomy_options WHERE name = 'hash';
        DELETE FROM taxonomy_options WHERE name = 'distilled';
        DELETE FROM taxonomy_options WHERE name = 'crude';
        DELETE FROM taxonomy_options WHERE name = 'cured';
        DELETE FROM taxonomy_options WHERE name = 'dry';
        DELETE FROM taxonomy_options WHERE name = 'g-wet';
        DELETE FROM taxonomy_options WHERE name = 'plants';
        DELETE FROM taxonomy_options WHERE name = 'seeds';
    """
    )
