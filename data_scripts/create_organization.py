# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE, insert_into_db

from constants import USER_ID


def create_org(name):
    record = {
        "name": name,
        "features": {
            "qa": True,
            "admin": True,
            "orders": True,
            "uploads": True,
            "inventory": True,
            "warehouse": True,
            "greenhouse": True,
            "crm-account": True,
            "environment": True,
            "rule-editor": True
        },
        "security": {
            "scanner_timeout": 600,
            "scanner_timeout_warning": 15
        }
    }

    res = insert_into_db("organizations", record)

    return res["id"]


def main():
    """Main function that takes organization name as an argument and inserts a new organization with the default feature set under the given name.
    """

    parser = argparse.ArgumentParser(
        description='Create an organization in the database'
    )

    parser.add_argument(
        '--name',
        type=str,
        help='Name for the organization',
        required=True
    )

    args = parser.parse_args()

    create_org(args.name)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
