import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


from labels.class_label_abstract import LabelAbstract
from class_errors import EngineError
import json



class LabelBaseZpl(LabelAbstract): 

    
    
    
    def __init__(self, label_type, object_id, label_id, organization_id, number_of_labels = 1, show_number = False, start_number = 1, out_of = 1):
        """
            Constructor method
        """
        self._label_type = label_type
        self._object_id = object_id
        self._label_id = label_id
        self._organization_id = organization_id
        self._show_number = eval(show_number.title())
        self._number_of_labels = int(number_of_labels)
        self._start_number = int(start_number)
        self._out_of = int(out_of)
        self._label_height = 4
        

    def _set_label_template_info(self, label_id, organization_id):
        template_object  = super()._set_label_template_info(label_id, organization_id)
        self._label_height = template_object["height"]
        

    def _get_barcode_object(self, id, label_type):
        return json.dumps(
            {
                'type': label_type,
                'id': id,
            },
            sort_keys="true")
        
    
    def do_formatting(self):
        try:
            self._set_label_template_info(self._label_id, self._organization_id)
            data = self._get_data(self._table_name, self._object_id, self._organization_id)

            barcode_object = self._get_barcode_object(self._object_id, self._label_type)
            
            if (self._number_of_labels > 0):
                self._label_template = self._add_label_number(self._number_of_labels, self._show_number, self._start_number, self._out_of)
    
            
            
            formatted_label = self._label_template.format(
                data=data,
                barcode_data=barcode_object,
            )

            return formatted_label

        except Exception as e:
            raise EngineError({
                "error": "class_label_ZPL_formatting_error",
                "description": "Error formating label - {}".format(e)
            }, 403)


    def _add_label_number(self, number_of_labels, show_number, start_number, out_of):
        x_position =  660
        y_position = 0

        if (self._label_height == 2):
            y_position = 350
        elif (self._label_height == 4):
            y_position = 745
        elif (self._label_height == 8):
            y_position = 1555

        number_zpl_code = """
            ^PQ{0}^FS
        """.format(number_of_labels).replace('\n', ' ')

        if (show_number):
            # this position works for printers with 203 dpi    

            number_zpl_code = number_zpl_code + """
                ^FO{0},{1}^AZN,30^FD^SN00{2},1,N^FS
                ^FT^AZN,30^FD/{3}^FS
            """.format(x_position, y_position, start_number, out_of).replace('\n', ' ')


        number_zpl_code = number_zpl_code + "^XZ"


        return self._label_template.replace("^XZ", number_zpl_code)
