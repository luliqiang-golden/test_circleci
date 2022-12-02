import decimal
import json

class DecimalEncoder(json.JSONEncoder):
    """use to transfer decimal to float"""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return (self, obj)