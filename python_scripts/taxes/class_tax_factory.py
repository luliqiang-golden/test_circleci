
from taxes.class_tax_canada import TaxCanada
from taxes.class_tax_fallback import TaxFallback


import db_functions

CanadaTypes = {
    'ON': 'hst_tax',
    'AB': 'gst_tax',
    'BC': 'gst_pst_tax',
    'MB': 'gst_pst_tax',
    'NB': 'hst_tax',
    'NL': 'hst_tax',
    'NS': 'hst_tax',
    'PE': 'hst_tax',
    'QC': 'gst_qst_tax',
    'SK': 'gst_pst_tax',
    'NT': 'gst_tax',
    'NU': 'gst_tax',
    'YT': 'gst_tax',
}

class TaxFactory:
    """
        Tax factory Class
        This class is resposable to get the instace of the class tax base
    """
    
    @staticmethod
    def get_instance(order_item_id, price, organization_id):
        """
            Method responsible to get the instance of the tax classes
           
            :returns: the instance of the class
        """
        result = TaxFactory.__get_province_country(organization_id, order_item_id)
        if (result["country"] == "Canada"):
            return TaxCanada(result["country"], result["province"], order_item_id, price, organization_id, CanadaTypes[result["province"]])
        else:
            return TaxFallback(result["country"], result["province"], order_item_id, price, organization_id)
        

    @staticmethod
    def __get_province_country(organization_id, order_item_id):
        params = { 'organization_id': organization_id, 'order_item_id': order_item_id }
        query = '''
            SELECT  o.shipping_address->>'province' AS province, o.shipping_address->>'country' AS country
            FROM order_items AS oi
                INNER JOIN orders AS o ON o.id = oi.order_id
            WHERE oi.id = %(order_item_id)s
                AND oi.organization_id = %(organization_id)s
        '''

        result = db_functions.select_from_db(query, params)
        if (result):            
            return {
                "country": result[0]['country'],
                "province": result[0]['province']
            }


        
    

    

        
    

    