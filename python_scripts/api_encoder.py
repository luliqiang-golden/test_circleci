from flask.json import JSONEncoder
from datetime import datetime
from decimal import Decimal


class CustomJSONEncoder(JSONEncoder):
    """Format dates as ISO instead of HTTP"""

    def default(self, obj):  # pylint: disable=E0202,W0221
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
