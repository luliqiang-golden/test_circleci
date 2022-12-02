from flask_restful import Resource
from flask import request, jsonify
from marshmallow import ValidationError, EXCLUDE
from class_errors import ClientBadRequest

class BaseController(Resource):
    '''This should be used as base_class for all the resources. Any common method for all the resources can be written here'''

    def serialize(self, schema, args):
        '''Serializes request body data'''
        try:
            data = schema.load(args, unknown=EXCLUDE)
            return data
        except ValidationError as err:
            raise ClientBadRequest({"message": err.messages}, 400)

    def deserialize_object(self, schema, obj):
        '''Returns deserialized objects'''
        if obj:
            return schema.dump(obj)
        raise ClientBadRequest({"message": "No record found"}, 404)
        

    def deserialize_queryset(self, schema, queryset):
        '''Returns list of deserialized objects'''
        if len(queryset) > 0:
            return [schema.dump(obj) for obj in queryset]
        raise ClientBadRequest({"message": "No record found"}, 404)
    
    def deserialize_queryset_multiple(self, schemas, queryset):
        '''Returns list of deserialized objects'''
        entry_list = []
        if len(queryset) > 0:
            for obj in queryset:
                entry = {}
                for i, element in enumerate(obj):
                    entry[type(element).__name__.lower()] = schemas[i].dump(element)
                entry_list.append(entry)
            return entry_list
        raise ClientBadRequest({"message": "No record found"}, 404)

    def get_success_response(self, data, query=None, pagination=False):
        '''Makes success response for GET APIs'''
        response = {
            "data": data,
            "message": "success"
        }
        if pagination and query:
            response['pagination'] = {
                "has_previous_page": query.has_prev,
                "has_next_page": query.has_next,
                "previous_page": query.prev_num,
                "next_page": query.next_num,
                "total": query.total,
                "total_pages": query.pages,
                "per_page": query.per_page,
                "page": query.page
            }
        return jsonify(response),200


            
