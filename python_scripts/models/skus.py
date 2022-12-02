'''This module contains database schema model for skus table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func, inspect
from class_errors import ClientBadRequest
from models.taxonomy_options import TaxonomyOptions
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from sqlalchemy.types import String
class Skus(db.Model):

    '''Definition of skus table'''
    __tablename__ = 'skus'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String)
    variety = db.Column(db.String)
    cannabis_class = db.Column(db.String)
    target_qty = db.Column(db.Float)
    data = db.Column(JSONB)
    attributes = db.Column(JSONB)
    target_qty_unit = db.Column(db.String)
    sales_class = db.Column(db.String)
    price = db.Column(db.Numeric(14,2))
    current_inventory = db.Column(db.Integer)
    package_type = db.Column(db.String)

    def find_by_id(sku_id):
        return (Skus.query.filter(Skus.id == sku_id).first())    
    
    
    def format_post_request(data, params):
        extra_fields = dict(params.items() - data.items())
        if "current_inventory" not in data:
            data["current_inventory"] = 0
        status = extra_fields.pop('status', None)
        reserved = extra_fields.pop("reserved", None)
        extra_fields.pop("organization_id", None)
        data["attributes"] = {}
        data["attributes"]["reserved"] = reserved if reserved else 0 
        if status:
            data["attributes"]["status"] = status
        
        product_type = None
        if "product_type" in extra_fields:
            product_type = extra_fields["product_type"]
            
        data["data"] = extra_fields
        if not "external_sku_id" in data["data"] or not "external_sku_variant_id" in data["data"]:
            data["data"]["external_sku_id"] = 0
            data["data"]["external_sku_variant_id"] = 0

        return Skus(**data), product_type
    
    
    def add_sku(sku_data, data, created_by, organization_id):
        try:
            variety = TaxonomyOptions.get_variety_by_name(organization_id, data["variety"])
            if not variety:
                from models.taxonomies import Taxonomies
        
                taxonomy = (Taxonomies.query
                    .filter(Taxonomies.organization_id == organization_id)
                    .filter(Taxonomies.name == 'varieties')
                    .one_or_none())
                
                variety_data = TaxonomyOptions(
                    name = data["variety"],
                    taxonomy_id = taxonomy.id,
                    data = {
                        "strain": "Hybrid"
                    },
                    created_by = created_by,
                    organization_id = organization_id                    
                )
                db.session.add(variety_data)
                db.session.commit()
                                
            db.session.add(sku_data)
            db.session.commit()
            return True, "Success"
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return False, error
    
    def format_get_request(req, organization_id):
        page = req.get('page', type=int)
        per_page = req.get("per_page", type=int)
        filters = req.getlist("filter", type=str)
        
        # Creating Base Query
        base_query = base_query = Skus.query.filter(Skus.organization_id==organization_id).order_by(desc('id'))
        
        # Adding filter to query if conditions come as filter= in request
        for filtr in filters:
            filter_query = filtr.split('=')
            if filter_query[0] == 'external_sku_id':
                base_query = base_query.filter(Skus.external_sku_id==filter_query[1])
            elif filter_query[0] == 'cannabis_class':
                base_query = base_query.filter(Skus.cannabis_class==filter_query[1])
            elif filter_query[0] == 'sales_class':
                base_query = base_query.filter(Skus.sales_class==filter_query[1])
            elif filter_query[0] == 'variety':
                base_query = base_query.filter(Skus.variety==filter_query[1])
            elif filter_query[0] == 'target_qty_unit':
                base_query = base_query.filter(Skus.target_qty_unit==filter_query[1])
            elif filter_query[0] == 'attributes:status':
                base_query = base_query.filter(Skus.attributes['status'].astext.cast(String)==filter_query[1])
        
        # Adding filter to query if conditions come without filter= in request
        if req.get('external_sku_id'):
            base_query = base_query.filter(Skus.external_sku_id==req.get('external_sku_id'))    
        if req.get('cannabis_class'):
            base_query = base_query.filter(Skus.cannabis_class==req.get('cannabis_class'))
        if req.get('sales_class'):
            base_query = base_query.filter(Skus.sales_class==req.get('sales_class'))
        if req.get('variety'):
            base_query = base_query.filter(Skus.variety==req.get('variety'))
        if req.get('target_qty_unit'):
            base_query = base_query.filter(Skus.target_qty_unit==req.get('target_qty_unit'))
        if req.get('attributes:status'):
            base_query = base_query.filter(Skus.attributes['status'].astext.cast(String)==req.get('attributes:status'))
        
        if page and per_page:
            pagination = True
            query = base_query.paginate(page, per_page, False)
            queryset = query.items
        else:
            pagination = False
            query = None
            queryset = base_query.all()

        return queryset, query, pagination
    
    def format_patch_request(org_data, data, params, created_by, organization_id):
        
        org_data.update(data)
        extra_fields = dict(params.items() - data.items())
        
        org_data["organization_id"] = organization_id
        org_data["created_by"] = created_by
        org_data["attributes"] = dict(org_data["attributes"])
                                               
        if "status" in extra_fields:
            org_data["attributes"]["status"] = extra_fields.pop("status")
        if "reserved" in extra_fields:
            org_data["attributes"]["reserved"] = extra_fields.pop("reserved")
        
        only_external_sku_id = None
        if "update_type" in extra_fields:
            only_external_sku_id = extra_fields.pop("update_type")
            
        org_data["data"].update(extra_fields)
        
        return org_data, only_external_sku_id
    
    
    def update_sku(sku_id, update_data):
        Skus.query.filter_by(id=sku_id).update(update_data)
        db.session.commit()
    
    def get_sku_detail_for_webhook(sku_id):
        sku = Skus.query.get(sku_id)
        return {
            "sku_id": sku.id,
            "name": sku.name,
            "current_inventory": sku.current_inventory,
            "price": float(sku.price),
            "external_sku_variant_id": sku.data.get('external_sku_variant_id'),
            "external_sku_id": sku.data.get('external_sku_id'),
            "id": sku.id,
            "variety": sku.variety
        }
