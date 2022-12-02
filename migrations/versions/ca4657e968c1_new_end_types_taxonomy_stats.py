"""new-end-types-taxonomy-stats

Revision ID: ca4657e968c1
Revises: 1ee52a4e92e4
Create Date: 2021-06-14 14:58:58.412512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca4657e968c1'
down_revision = '1ee52a4e92e4'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(
"""
    INSERT INTO taxonomies (organization_id, created_by, name, data)
        SELECT o.id, 1, 'stats', '{}'
        FROM organizations o
        WHERE o.data IS NOT NULL 
          AND id NOT IN (SELECT organization_id
                         FROM taxonomies
                         WHERE organization_id = o.id
                           AND name = 'stats')
        ORDER BY o.id;

    CREATE OR REPLACE VIEW stats_taxonomies
    AS SELECT to1.id,
        to1.organization_id,
        to1.created_by,
        to1."timestamp",
        to1.name,
        to1.data,
        to1.taxonomy_id
       FROM taxonomy_options to1
         JOIN taxonomies t ON t.id = to1.taxonomy_id
      WHERE t.name::text = 'stats'::text;
    
    DELETE FROM taxonomy_options WHERE id IN (SELECT id FROM stats_taxonomies st);
    
    DO $$
        DECLARE 
            taxonomy_id bigint;
            
        BEGIN
            SELECT id INTO taxonomy_id FROM taxonomies WHERE name = 'stats';
       
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'seeds', '{"type": "standard", "parent": "", "stages": ["planning", "germinating"], "enabled": true, "subtype": "", "metricMass": "un", "friendlyName": "seeds", "cannabisClass": "cannabis plants seeds", "reportSection": "seeds", "isFinalProduct": false}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'plants', '{"type": "standard", "parent": "", "stages": ["planning", "propagation", "vegetation", "flowering"], "enabled": true, "subtype": "", "metricMass": "un", "friendlyName": "plants", "cannabisClass": "cannabis plants", "reportSection": "plants", "isFinalProduct": false}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'g-wet', '{"type": "standard", "parent": "", "stages": ["planning", "harvesting"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "(wet)", "cannabisClass": "fresh cannabis", "reportSection": "fresh_cannabis", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'dry', '{"type": "standard", "parent": "g-dry", "stages": ["planning", "drying"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "dry (dry material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'cured', '{"type": "standard", "parent": "g-dry", "stages": ["planning", "curing"], "enabled": true, "subtype": "", "metricMass": "g", "friendlyName": "dry (cured material)", "cannabisClass": "dried cannabis", "reportSection": "dried_cannabis", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'crude', '{"type": "standard", "parent": "g-oil", "stages": ["planning", "extracting_crude_oil"], "enabled": true, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (crude material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'distilled', '{"type": "standard", "parent": "g-oil", "stages": ["planning", "distilling"], "enabled": true, "subtype": "ingested", "metricMass": "g", "friendlyName": "oil (distilled material)", "cannabisClass": "cannabis oil", "reportSection": "ingested", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'hash', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'bubbleHash', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (bubble hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'liveBubbleHash', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live bubble hash)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'hashRosin', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (hash rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'liveRosin', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'liveHashRosin', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "inhaled", "metricMass": "g", "friendlyName": "extract (live hash rosin)", "cannabisClass": "cannabis extracts", "reportSection": "inhaled", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'terpene', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (terpene)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'biomass', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (biomass)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}', taxonomy_id);     
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'sift', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (sift)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}', taxonomy_id);
            INSERT INTO public.taxonomy_options (organization_id, created_by, timestamp, name, data, taxonomy_id) VALUES (1, 1, now(), 'cannabinoid', '{"type": "extract", "parent": "g-extract", "stages": ["planning"], "enabled": true, "subtype": "other", "metricMass": "g", "friendlyName": "extract (cannabinoid)", "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": true}', taxonomy_id);
             
        END;
    $$;
"""
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
"""
    DELETE FROM taxonomy_options WHERE taxonomy_id IN (SELECT id FROM taxonomies WHERE name = 'stats');

    DROP VIEW IF EXISTS stats_taxonomies;
"""
    )
