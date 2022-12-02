"""blended pure intermediates

Revision ID: d1e1356995f4
Revises: e7e934260e9b
Create Date: 2022-08-18 15:13:45.770928

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import func
from models.taxonomies import Taxonomies
from models.taxonomy_options import TaxonomyOptions


# revision identifiers, used by Alembic.
revision = 'd1e1356995f4'
down_revision = 'e7e934260e9b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    queryset = (Taxonomies.query
                .with_entities(Taxonomies.id, 
                               Taxonomies.organization_id)
                .filter(Taxonomies.name == 'stats')
        ).all()
 
    #Solids
    taxonomy_options_insert_dryGummies = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+gummies',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "solid", "metricMass": "g", "friendlyName": "extract (dry+gummies)", 
                                "cannabisClass": "cannabis extracts", "reportSection": "solid", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_curedGummies = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+gummies',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "solid", "metricMass": "g", "friendlyName": "extract (cured+gummies)", 
                                "cannabisClass": "cannabis extracts", "reportSection": "solid", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    
    taxonomy_options_insert_gwetGummies = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+gummies',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "solid", "metricMass": "g", "friendlyName": "extract (g-wet+gummies)", 
                                "cannabisClass": "cannabis extracts", "reportSection": "solid", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]
    
    #Pure Intermediates
    taxonomy_options_insert_dryTerpene = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+terpene',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (dry+terpene)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_curedTerpene = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+terpene',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (cured+terpene)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_gwetTerpene = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+terpene',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (g-wet+terpene)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_drySift = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+sift',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (dry+sift)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]
    
    taxonomy_options_insert_curedSift = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+sift',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (cured+sift)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_gwetSift = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+sift',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (g-wet+sift)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_dryBiomass = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+biomass',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (dry+biomass)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]     

    taxonomy_options_insert_curedBiomass = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+biomass',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (cured+biomass)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_gwetBiomass = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+biomass',
                         'data': {"type": "extract", "parent": "g-extract", "stages": ["final_extraction"], "enabled": True, "subtype": "other", "metricMass": "g", "friendlyName": "extract (g-wet+biomass)", 
                         "cannabisClass": "cannabis extracts", "reportSection": "other", "isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]                




    #Inhaled
    taxonomy_options_insert_dryHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+hash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]  

    taxonomy_options_insert_curedHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+hash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]  

    taxonomy_options_insert_gwetHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+hash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_dryBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+bubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_curedBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+bubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_gwetBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+bubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True, "isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]

    taxonomy_options_insert_dryLiveBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+liveBubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+live bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]  

    taxonomy_options_insert_curedLiveBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+liveBubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+live bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_gwetLiveBubbleHash = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+liveBubbleHash',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+live bubble hash)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]
    
    taxonomy_options_insert_dryHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+hashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_curedHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+hashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_gwetHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+hashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_dryLiveRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+liveRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+live rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_curedLiveRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+liveRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+live rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]  

    taxonomy_options_insert_gwetLiveRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+liveRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+live rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_dryLiveHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'dry+liveHashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (dry+live hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset]   

    taxonomy_options_insert_curedLiveHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'cured+liveHashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (cured+live hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 

    taxonomy_options_insert_gwetLiveHashRosin = [{'organization_id': entry[1],'created_by': 1,'timestamp': func.now(),'name': 'g-wet+liveHashRosin',
                         'data': {"type": "extract","parent": "g-extract","stages": ["final_extraction"],"enabled": True,"subtype": "inhaled","metricMass": "g","friendlyName": "extract (g-wet+live hash rosin)",
                         "cannabisClass": "cannabis extracts","reportSection": "inhaled","isFinalProduct": True,"isBlendedProduct": True},
                         'taxonomy_id': entry[0]} for entry in queryset] 
  
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryGummies))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_curedGummies))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetGummies))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryTerpene))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_curedTerpene))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetTerpene))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_drySift))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_curedSift))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetSift))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryBiomass))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_curedBiomass))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetBiomass))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryBubbleHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetBubbleHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryLiveBubbleHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetLiveBubbleHash))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryHashRosin))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetHashRosin))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryLiveRosin))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetLiveRosin))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_dryLiveHashRosin))
    connection.execute(TaxonomyOptions.__table__.insert().values(taxonomy_options_insert_gwetLiveHashRosin))
    

def downgrade():
    connection = op.get_bind()

    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+gummies'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+gummies'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+gummies'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+terpene'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+terpene'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+terpene'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+sift'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+sift'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+sift'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+biomass'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+biomass'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+biomass'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+hash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+hash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+hash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+bubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+bubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+bubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+liveBubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+liveBubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+liveBubbleHash'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+hashRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+hashRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+hashRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+liveRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+liveRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+liveRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'dry+liveHashRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'cured+liveHashRosin'))
    connection.execute(TaxonomyOptions.__table__.delete().where(TaxonomyOptions.name == 'g-wet+liveHashRosin'))