from datetime import datetime
from time import strftime
from activities.capa_action_close import CapaActionClose
from activities.capa_action_cancel import CapaActionCancel
from activities.capa_add_action import CapaAddAction
import argparse
from constants import USER_ID
from db_functions import DATABASE, select_collection_from_db, update_capas_table_action_plan_fields
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def get_capa_action_ids(organization_id):
    ids = []
    capa_actions = select_collection_from_db('capa_actions', organization_id)
    for capa_action in capa_actions[0]:
        ids.append(capa_action.get('id'))
    return ids

# if a status is specififed, it wil lbe in "extras"


def create_capa_action(capa_id, description, organization_id, extras):
    record = {
        'name': 'capa_add_action',
        'capa_id': capa_id,
        'description': description,
        'created_by': USER_ID,
        'organization_id': organization_id,
        **extras
    }

    insert_result = CapaAddAction.do_activity(record, {})

    if not insert_result:
        print('Error creating capa')
        return DATABASE.dedicated_connection().rollback()

    capa_action_id = insert_result.get('capa_action_id')

    # default if status is "awaiting approval" or "canceled"
    adjustment = {
        'actions_total': +1
    }

    if 'status' in extras:
        if extras['status'] == 'closed':
            adjustment = {
                'actions_approved': +1
            }

    adjustment_result = update_capas_table_action_plan_fields(capa_action_id, adjustment)
    if not adjustment_result:
        print('Error adjusting capa action fields after creating capa')
        return DATABASE.dedicated_connection().rollback()

    for status, activity_name in [('closed', 'capa_action_close'), ('canceled', 'capa_action_cancel')]:

        if status == extras['status']:

            activity = {
                'name': activity_name,
                'created_by': USER_ID,
                'organization_id': organization_id,
                'timestamp': extras['timestamp'],
                'status': status,
                'capa_action_id': capa_action_id,
            }

            if activity_name == 'capa_action_close':
                activity['result'] = extras['result']
                result = CapaActionClose.do_activity(activity, {})

            if activity_name == 'capa_action_cancel':
                result = CapaActionCancel.do_activity(activity, {})

            if not result:
                print('Error recording activity')
                return DATABASE.dedicated_connection().rollback()

    return capa_action_id


def main():
    """Main function that creates a capa for a given organization."""

    parser = argparse.ArgumentParser(
        description='Create a capa action for a specified organization in the database. Defaults to "awaiting approval" status unless status flags used'
    )

    parser.add_argument(
        'capa_id',
        type=int,
        help='Capa ID of the capa action',
    )

    parser.add_argument(
        'description',
        type=str,
        help='Description of the capa action',
    )

    parser.add_argument(
        '--comment',
        type=str,
        help='Comment for the capa action',
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
        '--approved',
        type=str,
        metavar=('approve_date'),
        help='Date of approval. **Should match approve action plan activity timestamp (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--canceled',
        type=str,
        metavar=('canceled_date'),
        help='Date of cancelation (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--staff_assigned',
        type=str,
        help='Staff assigned to the capa action',
        required=False
    )

    parser.add_argument(
        '--due_date',
        type=str,
        help='When the capa action is due (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--timestamp',
        type=str,
        help='When the capa action was created (Format: YYYY-MM-DD)',
        required=False
    )

    parser.add_argument(
        '--result',
        type=str,
        choices=['completed', 'completed with exceptions', 'not completed'],
        help='Result of the capa action',
        required=False
    )

    parser.add_argument(
        '--organization_id',
        type=int,
        help='The id of the organization the capa action belongs to',
        required=True
    )

    parser.add_argument(
        '--data',
        type=str,
        help='Data column (jsonb)',
        required=False
    )

    args = parser.parse_args()

    # TODO: better way of doing this???
    extras = {}
    if args.comment:
        extras['comment'] = args.comment
    if args.staff_assigned:
        extras['staff_assigned'] = args.staff_assigned
    if args.due_date:
        extras['due_date'] = args.due_date
    if args.timestamp:
        extras['timestamp'] = args.timestamp
    if args.data:
        extras['data'] = args.data

    if args.closed:
        extras['status'] = 'closed'
        extras['result'] = args.result

    else:
        if args.approved:
            extras['status'] = 'approved'

        elif args.canceled:
            extras['status'] = 'canceled'

    # schema defaults to "awaiting approval" status if none is specified
    return create_capa_action(args.capa_id, args.description, args.organization_id, extras)


if __name__ == '__main__':
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
