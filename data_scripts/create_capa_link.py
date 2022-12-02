import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')
    
from db_functions import DATABASE, insert_into_db, select_collection_from_db
from constants import USER_ID
import argparse
from activities.capa_add_link import CapaAddLink


def get_capa_link_ids(organization_id):
    ids = []
    capa_links = select_collection_from_db('capa_links', organization_id)
    for capa_link in capa_links[0]:
        ids.append(capa_link.get('id'))
    return ids


def create_capa_link(capa_id, link_id, link_type, organization_id, extras):
    record = {
        "name": 'capa_add_link',
        "capa_id": capa_id,
        "created_by": USER_ID,
        "link_type": link_type,
        "link_id": link_id,
        "organization_id": organization_id,
        **extras
    }

    result = CapaAddLink.do_activity(record, {})
    return result.get('capa_link_id')


def main():
    """Main function that creates a capa for a given organization."""

    parser = argparse.ArgumentParser(
        description='Create a capa link for a specified organization in the database'
    )

    parser.add_argument(
        'capa_id',
        type=int,
        help='Capa ID of the capa link',
    )

    parser.add_argument(
        'link_id',
        type=int,
        help='Account/inventory/order ID of the capa link',
    )

    parser.add_argument(
        '--type',
        dest="link_type",
        type=str,
        choices=['account', 'inventory', 'order', 'upload'],
        help='Type of the capa link',
        required=True
    )

    parser.add_argument(
        '--organization_id',
        type=int,
        help='The id of the organization the capa link belongs to',
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
    if args.data is not None:
        extras['data'] = args.data

    return create_capa_link(
        args.capa_id,
        args.link_id,
        args.link_type,
        args.organization_id,
        extras
    )


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
