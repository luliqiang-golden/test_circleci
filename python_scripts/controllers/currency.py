'''This resource module controls API related to currencies'''

from flask import request, abort, Blueprint, jsonify
from auth0_authentication import requires_auth
from serializer.currency import CurrencySchema
from models.currency import Currency
from controllers import BaseController
from class_errors import ClientBadRequest

currency_schema = CurrencySchema()


class CurrenciesResource(BaseController):
    
    @requires_auth
    def post(self, current_user):
        '''Creates new currency into table'''
        data = self.serialize(currency_schema, request.get_json())
        currency = Currency(data)
        result = currency.insert_object()
        return jsonify({"message":"success", "currency_id":result}), 201

    @requires_auth
    def get(self, current_user):
        '''Returns list of all the currency present in table'''
        queryset = Currency.query.all()
        data = self.deserialize_queryset(currency_schema, queryset)
        return self.get_success_response(data)


class CurrencyByCodeResource(BaseController):
    @requires_auth
    def get(self, current_user, alphabetic_code):
        '''Returns list of currency based on given alphabetic_code'''
        currency_obj = Currency.query.filter_by(alphabetic_code=alphabetic_code.upper()).first()
        data = self.deserialize_object(currency_schema, currency_obj)
        return self.get_success_response(data)

# Make blueprint for currency API
currency_bp = Blueprint('currency', __name__)

# Define url_patterns related to currency API here
currencies = CurrenciesResource.as_view('currencies')
currency_bp.add_url_rule('/currencies', view_func=currencies, methods=['POST','GET'])

currency_by_code = CurrencyByCodeResource.as_view('currency_by_code')
currency_bp.add_url_rule('/currencies/<string:alphabetic_code>', view_func=currency_by_code, methods=['GET'])





