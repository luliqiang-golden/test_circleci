import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from abc import ABC,abstractmethod
import db_functions
from enum import Enum
from stats.class_stats import Stats

class TaxType(Enum):
    NONE = 0
    FLOWERING = 1
    NON_FLOWERING = 2
    EXTRACT_OIL = 3


class TaxBase(ABC):
    """
        base tax class
        other classes will extend and implement these methods 
    """
    
    _country = ""
    _province = ""
    _type = TaxType.NONE
    _order_item = None
    _sku = None
    _serialized_stats = None
    _price = 0
    _tax = None
    _tax_name = ""
    _tax_provincial = ""

    def __init__(self, country, province, order_item_id, price, organization_id, tax_provincial = ""):
        """
            Constructor method
        """
        self._country = country
        self._province = province
        self.organization_id = organization_id
        self._order_item = self.__get_order_item(order_item_id, organization_id)
        self._sku = self.__get_sku(self._order_item["sku_id"], organization_id)
        self._serialized_stats = Stats.serialize_stats(self._order_item["ordered_stats"])
        self._price = price
        self.__set_type()
        self._tax_provincial = tax_provincial
        
    @staticmethod
    def get_tax(country, province, organization_id):
        """
            get tax method 
        """
        params = {"country": country, "province": province, "organization_id": organization_id}

        query = '''
            SELECT * FROM (
                SELECT *
                FROM taxes
                WHERE country=%(country)s 
                AND province=%(province)s

                UNION ALL
                SELECT *
                FROM taxes
                WHERE COUNTRY = 'NA'
                AND organization_id=%(organization_id)s
            ) as t1 limit 1            
        '''

        result = db_functions.select_from_db(query, params)
        if (result):
           return result[0]
        else:
            raise Exception("No tax set up for this country and province")

    def __get_order_item(self, order_item_id, organization_id):
        return db_functions.select_resource_from_db('order_items',order_item_id,organization_id)


    def __set_type(self):
        if (self._serialized_stats["unit"] in ["seeds", "plants", "g-wet", "dry", "cured"]):
            self._type = TaxType.FLOWERING
        elif (self._serialized_stats["unit"] in ["distilled", "crude"]):
            self._type = TaxType.EXTRACT_OIL
        else:
            self._type = TaxType.NON_FLOWERING

    def __get_sku(self, sku_id, organization_id):
        return db_functions.select_resource_from_db('skus',sku_id,organization_id)


    def __get_price_per_gram(self):
       return float(float(self._price)/self._sku["target_qty"])

    def _get_total(self):
        return float(float(self._serialized_stats["qty"]) * self.__get_price_per_gram())

    def _update_order_item(self):
        pass

    def do_calculation(self):
        """
            do calculation method - if needed it can be overwriten in the child class
        """
        try:
          self._tax = self.get_tax(self._country, self._province, self.organization_id)
          self._set_variables()
          return self._execute_formulas()
            
        except Exception as e:
            raise Exception("Error executing the tax calculation - {}".format(e))
        

    @abstractmethod
    def _set_variables(self):
        """
           set variables method - must be implemented in the child class
        """

    @abstractmethod
    def _execute_formulas(self):
        """
           execute formula method - must be implemented in the child class
        """