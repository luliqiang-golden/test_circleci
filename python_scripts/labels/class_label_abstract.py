import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from abc import ABC,abstractmethod
from class_errors import EngineError
from db_functions import select_resource_from_db
import json

class LabelAbstract(ABC):
    """
        base label class
        other classes will extend and implement these methods 
    """
    _label_format = ""
    _label_template = ""
    _table_name = ""
    _label_type = ""
    _object_id = ""
    _label_id = ""
    _organization_id = ""
    _number_of_labels = 1
        
            
    
    def _get_data(self, table_name, object_id, organization_id):
        try:
             data = self._select_data(table_name, object_id,  organization_id)
             return self._format_fields(data)
        except Exception as e:
            raise EngineError({
                "code": "label_get_data_erro",
                "description": "Error getting data - {}".format(e)
            }, 403)


    def _set_label_template_info(self, label_id, organization_id):
        template_object = self._get_template(label_id, organization_id)
        if (not template_object):
            raise EngineError({
                "code": "label_doesnt_exist",
                "description": "Label doesn't exist"
            }, 403)

        self._label_format = template_object["format"]
        self._label_template = template_object["template"]
        self._table_name = template_object["tableName"]
        return template_object


    """[summary]
        Need to be implemented,  in case you need to format the data or add some extra info
    """
    def _format_fields(self, data):
        return data


    """[summary]
        select from the db, and can be ovewriten
    """
    def _select_data(self, table_name, object_id, organization_id):
        return select_resource_from_db(
                            table_name,
                            object_id,
                            organization_id,
             )

        
    def _get_template(self, label_id, organization_id):
        return select_resource_from_db('taxonomy_options', label_id,
                                                  organization_id)


    @abstractmethod
    def do_formatting(self):
        """
            do formatting method - must be implemented in the child class
        """
        pass
        
    
    
    

    



    





