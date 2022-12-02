# Import libraries from parent folder
from constants import USER_ID
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

from db_functions import DATABASE
from activities.org_update_upload_formats import OrgUpdateUploadFormats
from activities.org_update_metric_system import OrgUpdateMetricSystem
from activities.org_update_license_id import OrgUpdateLicenseId
from activities.org_update_date_time_format import OrgUpdateDateTimeFormat
from activities.org_update_date_format import OrgUpdateDateFormat
from activities.org_update_currency import OrgUpdateCurrency


def create_org_settings(organization_id):

    # update org settings
    activities = ['org_update_currency', 'org_update_date_format', 'org_update_date_time_format',
                  'org_update_license_id', 'org_update_metric_system', 'org_update_upload_formats']

    for activity_name in activities:

        activity_args = {
            'name': activity_name,
            'organization_id': organization_id,
            'created_by': USER_ID
        }

        if activity_name == 'org_update_currency':
            activity_args['currency'] = 'CAD'
            result = OrgUpdateCurrency.do_activity(activity_args, {})

            if result:
                print("Updated organization's currency")
            else:
                print("Error in updating organization's currency")


        elif activity_name == 'org_update_date_format':
            activity_args['date_format'] = 'M/d/yy'
            activity_args['date_locale'] = 'en-US'
            result = OrgUpdateDateFormat.do_activity(activity_args, {})

            if result:
                print("Updated organization's date format")
            else:
                print("Error in updating organization's date format")

        elif activity_name == 'org_update_date_time_format':
            activity_args['date_time_format'] = 'MMM D, Y, H:mm'
            result = OrgUpdateDateTimeFormat.do_activity(activity_args, {})

            if result:
                print("Updated organization's date time format")
            else:
                print("Error in updating organization's date time format")


        elif activity_name == 'org_update_license_id':
            activity_args['license_id'] = '123 DEF'
            result = OrgUpdateLicenseId.do_activity(activity_args, {})

            if result:
                print("Updated organization's license ID")
            else:
                print("Error in updating organization's license ID")


        elif activity_name == 'org_update_metric_system':
            activity_args['metric_system'] = 'metric'
            result = OrgUpdateMetricSystem.do_activity(activity_args, {})

            if result:
                print("Updated organization's metric system")
            else:
                print("Error in updating organization's metric system")


        elif activity_name == 'org_update_upload_formats':
            activity_args['upload_formats'] = ["csv", "log", "jpeg", "jpg", "png", "ods", "xls", "xlsx", "doc",
                                               "docx", "odt", "pdf", "txt", "vnd.ms-excel", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
            result = OrgUpdateUploadFormats.do_activity(activity_args, {})

            if result:
                print("Updated organization's file upload formats")
            else:
                print("Error in updating organization's upload formats")



if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")

    if (organization_id):
        # Begin DB transaction
        DATABASE.dedicated_connection().begin()

        create_org_settings(organization_id)

        # Commit DB transaction
        DATABASE.dedicated_connection().commit()
