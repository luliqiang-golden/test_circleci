# Import libraries from parent folder
import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) +
    '/python_scripts')

import argparse
from db_functions import DATABASE, insert_into_db, select_resource_from_db
from utilities import select_from_db
from constants import USER_ID


def create_user(organization_id, name, email):
    user = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": name,
        "email": email,
        "enabled": True
    }

    res = insert_into_db("users", user)

    return res["id"]

def get_users_by_organization(organization_id):
    params = { 'organization_id': organization_id }
    
    query = '''        SELECT *
        FROM users AS a
        WHERE a.organization_id=%(organization_id)s
    '''
    
    result = select_from_db(query, params)
    if (result):
        return result


def main():
    """Main function that creates a user for a given organization.
    """

    parser = argparse.ArgumentParser(
        description='Create a user in the database')

    parser.add_argument(
        '--organization_id',
        type=int,
        help='Organization id to create user for',
        required=True)

    parser.add_argument('--name', type=str, help='Name of user', required=True)

    parser.add_argument(
        '--email', type=str, help='Email of user', required=True)

    args = parser.parse_args()

    create_user(args.organization_id, args.name, args.email)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
