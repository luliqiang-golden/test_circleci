# Import libraries from parent folder
import os
import sys
import datetime
from time import strftime
import requests
from constants import USER_ID

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

from utilities import get_department_by_name, get_random_user, get_random_date_after_today, get_user_by_id
from db_functions import DATABASE, TABLE_COLUMNS, DatabaseError, insert_into_db
from class_sops import Sops
from class_sop_versions import SopVersions
from activities.sop_assign_department import SopAssignDepartment
from activities.sop_assign_user import SopAssignUser
from activities.sop_assignment_sign import SopAssignmentSign
from cloud_storage import CloudStorage

def create_sops(organization_id):

    ## SOP 1: Bulk transfer form
    department = get_department_by_name(organization_id, 'Management')

    user = get_random_user(organization_id)

    record = {'departments': [department.get('id')], 
    'description': 'To establish a procedure to ensure all materials have been accounted for and no mix-up occurred during the production of medical cannabis.', 
    'approved_date': get_random_date_after_today(1,10),
    'effective_date': get_random_date_after_today(1,10),
    'review_due_date': get_random_date_after_today(1,10),
    'review_approval_date': get_random_date_after_today(1,10),
    'assignments': [user.get('id')], 
    'content_type': 'application/pdf', 
    'name': 'Bulk Transfer',
    'organization_id': organization_id,
    'created_by':USER_ID}

    # create sop
    db_result = insert_into_db('Sops', record)
    sop_id = db_result.get('id')

    # create sop_version
    version_response = create_sop_version(sop_id, record, 'sops/bulk_transfer_form.pdf')
    sop_version_id = version_response.get('id')

    # create sop activities - sop_assign_user & sop_assign_department
    sop_activities(sop_id, sop_version_id, record)

    ## SOP 2: Inventory Control
    department = get_department_by_name(organization_id, 'Warehouse')
    user = get_random_user(organization_id)

    record = {'departments': [department.get('id')], 
    'description': 'To establish the method for tracking the inventory of raw materials, packaging materials, and cannabis.', 
    'approved_date': get_random_date_after_today(1,10),
    'effective_date': get_random_date_after_today(1,10),
    'review_due_date': get_random_date_after_today(1,10),
    'review_approval_date': get_random_date_after_today(1,10),
    'assignments': [user.get('id')], 
    'content_type': 'application/pdf', 
    'name': 'Inventory Control',
    'organization_id': organization_id,
    'created_by':USER_ID}

    # create sop
    db_result = insert_into_db('Sops', record)
    sop_id = db_result.get('id')

    # create sop_version
    version_response = create_sop_version(sop_id, record, 'sops/inventory_control.pdf')
    sop_version_id = version_response.get('id')

    # create sop activities - sop_assign_user & sop_assign_department & sop_assignment_sign
    sop_activities(sop_id, sop_version_id, record, markAsSigned=True)


    ## SOP 3: Product Complaints
    department = get_department_by_name(organization_id, 'Management')
    user_1 = get_random_user(organization_id)
    user_2 = get_random_user(organization_id)
    user_3 = get_random_user(organization_id)

    record = {'departments': [department.get('id')], 
    'description': 'To establish a procedure for processing all product quality complaints and adverse reactions received.', 
    'approved_date': get_random_date_after_today(1,10),
    'effective_date': get_random_date_after_today(1,10),
    'review_due_date': get_random_date_after_today(1,10),
    'review_approval_date': get_random_date_after_today(1,10),
    'assignments': [user_1.get('id'), user_2.get('id'), user_3.get('id')], 
    'content_type': 'application/pdf', 
    'name': 'Product Complaints',
    'organization_id': organization_id,
    'created_by':USER_ID}

    # create sop
    db_result = insert_into_db('Sops', record)
    sop_id = db_result.get('id')

    # create sop_version
    version_response = create_sop_version(sop_id, record, 'sops/product_complaints.pdf')
    sop_version_id = version_response.get('id')

    # create sop activities - sop_assign_user & sop_assign_department 
    sop_activities(sop_id, sop_version_id, record)

     ## SOP 4: SOP on SOPs
    department = get_department_by_name(organization_id, 'Management')
    user_1 = get_random_user(organization_id)
    user_2 = get_random_user(organization_id)

    record = {'departments': [department.get('id')], 
    'description': 'To ensure a consistent process for the creation or revision, review and approval, distribution and implementation of Standard Operating Procedures (SOPs) in compliance with Good Production Practices (GPP)', 
    'approved_date': get_random_date_after_today(1,10),
    'effective_date': get_random_date_after_today(1,10),
    'review_due_date': get_random_date_after_today(1,10),
    'review_approval_date': get_random_date_after_today(1,10),
    'assignments': [user_1.get('id'), user_2.get('id')], 
    'content_type': 'application/pdf', 
    'name': 'SOP on SOPs',
    'organization_id': organization_id,
    'created_by':USER_ID}

    # create sop
    db_result = insert_into_db('Sops', record)
    sop_id = db_result.get('id')

    # create sop_version
    version_response = create_sop_version(sop_id, record, 'sops/sop_on_sops.pdf')
    sop_version_id = version_response.get('id')

    # create sop activities - sop_assign_user & sop_assign_department & sop_assignment_sign
    sop_activities(sop_id, sop_version_id, record, markAsSigned=True, deptHeadSign=True)



def create_sop_version(sop_id, args, filePath):
    resource = 'sop_versions'
    args['sop_id'] = sop_id
    columns = [col for col in TABLE_COLUMNS.get(resource) if col not in ['id']] 
    record = {k:args[k] for k in columns if args.get(k)}
   
    db_result = insert_into_db(resource, record)

    timestamp = strftime("%Y-%m-%dT%H:%M:%S")

    blob = CloudStorage.get_blob('{0}/sops/{1}/{2}'.format(args['organization_id'], sop_id, timestamp))

    signed_url = blob.generate_signed_url(
    datetime.timedelta(minutes=5),
    method='PUT',
    content_type=args['content_type'])

    db_result['upload_url'] = signed_url

    headers = headers = {'Content-type': args['content_type']}
    response = requests.put(signed_url, data=open(filePath, 'rb'), headers=headers)

    if response.status_code != 200:
        print("SOP doc upload was unsuccessful")
    return db_result


def sop_activities(sop_id, sop_version_id, args, markAsSigned = False, deptHeadSign = False):
    
    # set sop department using sop_assign_department activity
    for department in args['departments']:
        activity_args = {
            'sop_id': sop_id,
            'version_id': sop_version_id,
            'department_id': department,
            'created_by_id': args['created_by'],
            'organization_id': args['organization_id']
        }

        SopAssignDepartment.do_activity(activity_args, {})

    # assign sop to users using sop_assign_user activity
    for assigned_to_id in args['assignments']:
        activity_args = {
            'sop_id': sop_id,
            'version_id': sop_version_id,
            'assigned_to_id': assigned_to_id,
            'assigned_by_id': args['created_by'],
            'created_by_id': args['created_by'],
            'organization_id': args['organization_id']
        }
        SopAssignUser.do_activity(activity_args, {})

    if markAsSigned:
        for assigned_to_id in args['assignments']:
            timestamp = strftime("%Y-%m-%dT%H:%M:%S")
            activity_args = {
                    "name": "sop_assignment_sign",
                    "assigned_to_id": assigned_to_id,
                    "assigned_by_id": args['created_by'],
                    "sop_version_id": sop_version_id,
                    "signed_date": timestamp,
                    "created_by": args['created_by'],
                    "organization_id": args['organization_id']
            }
            SopAssignmentSign.do_activity(activity_args, {})

    if deptHeadSign:
        user = get_user_by_id(USER_ID)
        for assigned_to_id in args['assignments']:
            timestamp = strftime("%Y-%m-%dT%H:%M:%S")
            activity_args = {
                    "name": "sop_assignment_sign",
                    "assigned_to_id": assigned_to_id,
                    "assigned_by_id": args['created_by'],
                    "sop_version_id": sop_version_id,
                    "signed_date": timestamp,
                    "department_head_id": USER_ID,
                    "department_head_name": user.get('name'),
                    "created_by": args['created_by'],
                    "organization_id": args['organization_id']
                }
            SopAssignmentSign.do_activity(activity_args, {})



if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        # Begin DB transaction
        DATABASE.dedicated_connection().begin()

        create_sops(organization_id)

        # Commit DB transaction
        DATABASE.dedicated_connection().commit()
