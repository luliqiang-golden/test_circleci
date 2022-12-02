from labels.class_inventory_label_nicelabel import InventoryLabelNiceLabel
from labels.class_label_base_nicelabel import LabelBaseNiceLabel
from labels.class_received_inventory_label_zpl import ReceivedInventoryLabelZpl
from labels.class_inventory_label_zpl import InventoryLabelZpl
from labels.class_wholesale_label_zpl import WholesaleLabelZpl
from labels.class_sample_label_zpl import SampleLabelZpl
from labels.class_order_label_zpl import OrderLabelZpl
from labels.class_destruction_inventory_label_zpl import DestructionInventoryLabelZpl
from labels.class_label_base_zpl import LabelBaseZpl
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


class LabelFactory:
    """
        Label factory Class
        This class is resposable to get the instace of the class label base
    """

    @staticmethod
    def get_instance(label_id, label_type, label_format, object_id, number_of_label, show_number, start_number, end_number, organizarion_id):
        """
            Method responsible to get the instance of the label classes

            :returns: the instance of the class
        """

        if label_format == "ZPL":
            if (label_type == "order"):
                return OrderLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)
            elif (label_type == "sample"):
                return SampleLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)
            elif (label_type == "wholesale"):
                return WholesaleLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)
            elif (label_type == "inventory"):
                return InventoryLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)
            elif (label_type == "destruction_item"):
                return DestructionInventoryLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)

            elif (label_type in ["received_inventory"]):
                return ReceivedInventoryLabelZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)

            else:
                return LabelBaseZpl(label_type, object_id, label_id, organizarion_id, number_of_label, show_number, start_number, end_number)

        if label_format == "NICELABEL":
            if (label_type in ["inventory"]):
                return InventoryLabelNiceLabel(label_type, object_id, label_id, organizarion_id, number_of_label)
            else:
                return LabelBaseNiceLabel(label_type, object_id, label_id, organizarion_id, number_of_label)
