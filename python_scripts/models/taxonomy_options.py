'''This module contains database schema model for taxonomy options table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

class TaxonomyOptions(db.Model):

    '''Definition of taxonomy options table'''
    __tablename__ = 'taxonomy_options'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String)
    data = db.Column(JSONB)
    taxonomy_id = db.Column(db.Integer)

    def get_stats_object_by_name(organization_id, name):

        stats_object_list = db.session.execute("""select name, 
                                                    data->>'type' as type, 
                                                    data->>'parent' as parent, 
                                                    data->>'stages' as stages, 
                                                    data->>'subtype' as subtype, 
                                                    data->>'friendlyName' as friendly_name,
                                                    data->>'metricMass' as metric_mass,
                                                    data->>'activity' as activity
                                            from taxonomy_options
                                            where taxonomy_id = (select id from taxonomies where name = 'stats' and organization_id = :org_id) 
                                            order by id;
                                                """, {'org_id': organization_id})
        
        stats = list(filter(lambda stats: stats["name"] == name, stats_object_list))
        
        if (stats):
            return stats[0]

    def get_variety_by_id(organization_id, variety_id):
        
        from models.taxonomies import Taxonomies
        
        taxonomy = (Taxonomies.query
                    .filter(Taxonomies.organization_id == organization_id)
                    .filter(Taxonomies.name == 'varieties')
                    .one_or_none())
        
        return (TaxonomyOptions.query
                               .filter(TaxonomyOptions.id == variety_id)
                               .filter(TaxonomyOptions.organization_id == organization_id)
                               .filter(TaxonomyOptions.taxonomy_id == taxonomy.id)
                               .one_or_none())

    def get_variety_by_name(organization_id, variety_name):
        
        from models.taxonomies import Taxonomies
        
        taxonomy = (Taxonomies.query
                    .filter(Taxonomies.organization_id == organization_id)
                    .filter(Taxonomies.name == 'varieties')
                    .one_or_none())
        
        return (TaxonomyOptions.query
                               .filter(TaxonomyOptions.name == variety_name)
                               .filter(TaxonomyOptions.organization_id == organization_id)
                               .filter(TaxonomyOptions.taxonomy_id == taxonomy.id)
                               .one_or_none())