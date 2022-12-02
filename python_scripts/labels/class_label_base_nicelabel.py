
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


from labels.class_label_abstract import LabelAbstract
from class_errors import EngineError
import json

class LabelBaseNiceLabel(LabelAbstract): 

    def __init__(self, label_type, object_id, label_id, organization_id, number_of_labels = 1):
        """
            Constructor method
        """
        self._label_type = label_type
        self._object_id = object_id
        self._label_id = label_id
        self._organization_id = organization_id
        self._number_of_labels = int(number_of_labels)


    
    def do_formatting(self):
        try:
            self._set_label_template_info(self._label_id, self._organization_id)
            data = self._get_data(self._table_name, self._object_id, self._organization_id)

           
            return self.__replace_properties(self._label_template, data)

        except Exception as e:
            raise EngineError({
                "error": "class_label_NICELABEL_formatting_error",
                "description": "Error formating label - {}".format(e)
            }, 403)

    
    def __replace_properties(self, template, data):
        for key in template.keys():
            if "data[" in str(template[key]):
                dt = template[key]
                # remove the data[] - left it this way to be complient with what we have for zpl, and also make it easier for implement the changes in the front end, if needed
                dt = dt.replace("data[","").replace("]","")
                template[key] = data[dt]


        return template

    

    