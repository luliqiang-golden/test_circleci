from utilities import get_random_date_after_today, get_random_user
from activities.capa_close import CapaClose
from activities.capa_dismiss import CapaDismiss
from activities.capa_initiate import CapaInitiate
from activities.capa_approve_action_plan import CapaApproveActionPlan
from activities.create_capa import CreateCapa
from create_batch import get_batches
from create_capa_action import create_capa_action
from create_capa_link import create_capa_link
import argparse
from random import sample
from constants import USER_ID
from db_functions import DATABASE, select_collection_from_db
from datetime import datetime
from time import strftime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def create_capas(org_id):

    user = get_random_user(org_id)
    create_capa(
        description="Issue with fan in Bay 1",
        reported_by=user.get('name'),
        organization_id=org_id,
        status_array=[('dismissed', strftime("%Y-%m-%dT%H:%M:%S"))],
        plan_time=None,
        extras={}
    )
    user = get_random_user(org_id)
    create_capa(
        description="Product dropped onto floor after harvest",
        reported_by=user.get('name'),
        organization_id=org_id,
        status_array=[],
        plan_time=None,
        extras={}
    )
    user = get_random_user(org_id)
    create_capa(
        description="Excessive powdery mildew found",
        reported_by=user.get('name'),
        organization_id=org_id,
        status_array=[('initiated', strftime("%Y-%m-%dT%H:%M:%S"))],
        plan_time=None,
        extras={}
    )
    user = get_random_user(org_id)
    adverse_id = create_capa(
        description="Adverse reaction - patient requires hospitalization",
        reported_by=user.get('name'),
        organization_id=org_id,
        status_array=[('initiated', strftime("%Y-%m-%dT%H:%M:%S")),
                      ('closed', strftime("%Y-%m-%dT%H:%M:%S"))],
        plan_time=strftime("%Y-%m-%dT%H:%M:%S"),
        extras={}
    )

    batches = get_batches(org_id)
    link_id = sample(batches, 1)[0]['id']

    create_capa_link(
        capa_id=adverse_id,
        link_id=link_id,  # TODO: check if this is a batch
        link_type='inventory',
        organization_id=org_id,
        extras={}
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Notify customers that all sales of product/lot have stopped',
        organization_id=org_id,
        extras={
            'status': 'canceled',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S"),
            'staff_assigned': [user.get('name')]
        }
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Notify customers pending outcome of investigation',
        organization_id=org_id,
        extras={
            'result': 'completed',
            'status': 'closed',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S"),
            'staff_assigned': [user.get('name')],
            'due_date': strftime("%Y-%m-%d"),
        }
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Notify Health Canada using form Side Effects Reporting Form found in document repository',
        organization_id=org_id,
        extras={
            'staff_assigned': [user.get('name')],
            'due_date': strftime("%Y-%m-%d"),
            'result': 'completed',
            'status': 'closed',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S")
        }
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Immediately stop all sale of the product/lot',
        organization_id=org_id,
        extras={
            'staff_assigned': [user.get('name')],
            'due_date': strftime("%Y-%m-%d"),
            'result': 'completed',
            'status': 'closed',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S")
        }
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Investigate adverse reaction',
        organization_id=org_id,
        extras={
            'staff_assigned': [user.get('name')],
            'due_date': strftime("%Y-%m-%d"),
            'result': 'completed',
            'status': 'closed',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S")
        }
    )

    user = get_random_user(org_id)
    create_capa_action(
        capa_id=adverse_id,
        description='Issue product recall',
        organization_id=org_id,
        extras={
            'staff_assigned': [user.get('name')],
            'result': 'completed with exceptions',
            'comment': '1 customer was not able to be reached',
            'status': 'closed',
            'timestamp': strftime("%Y-%m-%dT%H:%M:%S")
        }
    )


# TODO: error handler???
# TODO: remove update??? not necessary... just need insert for capa and activity
def get_capa_ids(organization_id):
    ids = []
    capas = select_collection_from_db('capas', organization_id)
    for capa in capas[0]:
        ids.append(capa.get('id'))
    return ids

# if a status is specififed, it wil lbe in "extras"


def create_capa(description, reported_by, organization_id, status_array, plan_time, extras):
    record = {
        'name': 'create_capa',
        'description': description,
        'reported_by': reported_by,
        'created_by': USER_ID,
        'organization_id': organization_id,
        **extras
    }

    # no status, insert and db will default to "reported"
    if not status_array or len(status_array) < 1:
        return CreateCapa.do_activity(record, {})

    if len(status_array) == 2:
        # if length is 2, status objects must be for initiation and closing
        record['status'] = 'closed'
    else:
        (record['status'], _) = status_array[0]

    result = CreateCapa.do_activity(record, {})
    capa_id = result['capa_id']

    if not capa_id:
        print('Error creating capa')
        return DATABASE.dedicated_connection().rollback()

    # if specified, insert the approve action plan activity
    if plan_time is not None:
        activity = {
            'name': 'capa_approve_action_plan',
            'created_by': USER_ID,
            'organization_id': organization_id,
            'timestamp': plan_time,
            'capa_id': capa_id
        }
        approve_action_plan_result = CapaApproveActionPlan.do_activity(activity, {})
        if not approve_action_plan_result:
            print('Error approving action plan')
            return DATABASE.dedicated_connection().rollback()

    # for each status, insert the status change activity
    for status_object in status_array:
        activity_name_table = {
            'initiated': 'capa_initiate',
            'closed': 'capa_close',
            'dismissed': 'capa_dismiss'
        }
        (status, timestamp) = status_object
        activity_name = activity_name_table[status]

        activity = {
            'name': activity_name,
            'created_by': USER_ID,
            'organization_id': organization_id,
            'timestamp': timestamp,
            'capa_id': capa_id,
            'status': status
        }

        if activity_name == 'capa_initiate':
            record_activity_result = CapaInitiate.do_activity(activity, {})

        if activity_name == 'capa_close':
            record_activity_result = CapaClose.do_activity(activity, {})

        if activity_name == 'capa_dismiss':
            record_activity_result = CapaDismiss.do_activity(activity, {})

        if not record_activity_result:
            print('Error recording activity')
            return DATABASE.dedicated_connection().rollback()

    return result.get('capa_id')


def main():
    """Main function that creates a capa for a given organization."""

    parser = argparse.ArgumentParser(
        description='Create a capa for a specified organization in the database. Defaults to "reported" status unless status flags used'
    )

    parser.add_argument(
        'description',
        type=str,
        help='Description of the capa',
    )

    parser.add_argument(
        '--initiated',
        type=str,
        metavar=('initiate_date'),
        help='Date of initiation (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--with_plan',
        type=str,
        metavar=('approve_action_plan_date'),
        help='Date of action plan approval (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--closed',
        type=str,
        metavar=('close_date'),
        help='Date of closing (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--dismissed',
        type=str,
        metavar=('dismiss_date'),
        help='Date of dismissal (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--reported_by',
        type=str,
        help='Person reporting the capa',
        required=True
    )

    parser.add_argument(
        '--organization_id',
        type=int,
        help='The id of the organization the capa belongs to',
        required=True
    )

    # TODO: check if type should really be string
    parser.add_argument(
        '--data',
        type=str,
        help='Data column (jsonb)',
        required=False
    )

    args = parser.parse_args()

    extras = {}
    status_array = []  # an array of tuples of format (status, timestamp)

    if args.data:
        extras['data'] = args.data

    if args.initiated:
        status_array = [('initiated', args.initiated)]

    if args.closed:
        status_array.append(('closed', args.closed))

    if args.dismissed:
        status_array = [('dismissed', args.dismissed)]

    # schema defaults to "reported" status if none is specified
    return create_capa(args.description, args.reported_by, args.organization_id, status_array, args.with_plan, extras)


if __name__ == '__main__':
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
