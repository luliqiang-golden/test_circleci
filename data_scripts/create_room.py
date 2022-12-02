# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE, insert_into_db

from constants import USER_ID


def create_room(organization_id, name, zone, description=""):
    record = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": name,
        "zone": zone,
        "description": description
    }

    insert_into_db("rooms", record)


def main():
    """Main function that creates a room for a given organization.
    """

    parser = argparse.ArgumentParser(
        description='Create a room in the database'
    )

    parser.add_argument(
        '--organization_id',
        type=str,
        help='Organization id to create room for',
        required=True
    )

    parser.add_argument(
        '--name',
        type=str,
        help='Name of room to be created',
        required=True
    )

    parser.add_argument(
        '--zone',
        type=str,
        help='Zone for the room',
        required=True
    )

    parser.add_argument(
        '--description',
        type=str,
        help='Description for the room'
    )

    args = parser.parse_args()

    create_room(
        args.organization_id,
        args.name,
        args.zone,
        args.description
    )


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
