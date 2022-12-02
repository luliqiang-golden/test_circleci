"""Blended Batches End Types

Revision ID: 61a7792a04ed
Revises: 01510c41af44
Create Date: 2022-10-19 03:01:10.403106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61a7792a04ed'
down_revision = '01510c41af44'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
    """
    --biomass+sift
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (biomass+sift)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'biomass+sift',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'biomass+sift');
    --biomass+terpene
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (biomass+terpene)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'biomass+terpene',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'biomass+terpene');
    --sift+terpene
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (sift+terpene)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}',
        	'sift+terpene',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'sift+terpene');
    --bubbleHash+hash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubbleHash+hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'bubbleHash+hash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash+hash');
    --bubbleHash+hashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubbleHash+hashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',    
        	'bubbleHash+hashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash+hashRosin');
    --bubbleHash+liveBubbleHash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubbleHash+liveBubbleHash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'bubbleHash+liveBubbleHash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash+liveBubbleHash');
    --bubbleHash+liveHashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubbleHash+liveHashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'bubbleHash+liveHashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash+liveHashRosin');
    --bubbleHash+liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubbleHash+liveRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'bubbleHash+liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'bubbleHash+liveRosin');
    --hash+hashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash+hashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hash+hashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hash+hashRosin');  
    --hash+liveBubbleHash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash+liveBubbleHash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hash+liveBubbleHash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hash+liveBubbleHash');      
    --hash+liveHashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash+liveHashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hash+liveHashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hash+liveHashRosin');    
    --hash+liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash+liveRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hash+liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hash+liveRosin'); 
    --hashRosin+liveBubbleHash
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hashRosin+liveBubbleHash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hashRosin+liveBubbleHash',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hashRosin+liveBubbleHash');    
    --hashRosin+liveHashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hashRosin+liveHashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hashRosin+liveHashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hashRosin+liveHashRosin');  
    --hashRosin+liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hashRosin+liveRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'hashRosin+liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'hashRosin+liveRosin');    
    --liveBubbleHash+liveHashRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (liveBubbleHash+liveHashRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveBubbleHash+liveHashRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveRosin');    
    --liveBubbleHash+liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (liveBubbleHash+liveRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveBubbleHash+liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveBubbleHash+liveRosin');    
    --liveHashRosin+liveRosin
        insert into taxonomy_options (organization_id, created_by, data, name, taxonomy_id, timestamp)
        select
        	t.organization_id,
        	t.created_by,
        	'{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (liveHashRosin+liveRosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}',
        	'liveHashRosin+liveRosin',
        	t.id,
        	now()
        from taxonomies t where t.name = 'stats' and t.id not in (select tt.taxonomy_id from taxonomy_options tt where tt.name = 'liveHashRosin+liveRosin');
    """
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
    """
        DELETE FROM taxonomy_options WHERE name = 'biomass+sift';
        DELETE FROM taxonomy_options WHERE name = 'biomass+terpene';
        DELETE FROM taxonomy_options WHERE name = 'sift+terpene';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash+hash';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash+hashRosin';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash+liveBubbleHash';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash+liveHashRosin';
        DELETE FROM taxonomy_options WHERE name = 'bubbleHash+liveRosin';
        DELETE FROM taxonomy_options WHERE name = 'hash+hashRosin';
        DELETE FROM taxonomy_options WHERE name = 'hash+liveBubbleHash';
        DELETE FROM taxonomy_options WHERE name = 'hash+liveHashRosin';
        DELETE FROM taxonomy_options WHERE name = 'hash+liveRosin';
        DELETE FROM taxonomy_options WHERE name = 'hashRosin+liveBubbleHash';
        DELETE FROM taxonomy_options WHERE name = 'hashRosin+liveHashRosin';
        DELETE FROM taxonomy_options WHERE name = 'hashRosin+liveRosin';
        DELETE FROM taxonomy_options WHERE name = 'liveBubbleHash+liveHashRosin';
        DELETE FROM taxonomy_options WHERE name = 'liveBubbleHash+liveRosin';
        DELETE FROM taxonomy_options WHERE name = 'liveHashRosin+liveRosin';  
    """
    )
