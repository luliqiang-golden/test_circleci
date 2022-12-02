# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE, insert_into_db

from constants import USER_ID


def create_taxonomies(organization_id):
    taxonomy_names = [
        "varieties",
        "strains",
        "destruction_reasons",
        "waste_types",
        "destruction_methods",
        "stages",
        "labels",
        "compost_types",
        "pest_types",
        "categories",
        "upload_categories"
    ]

    for taxonomy in taxonomy_names:
        record = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            "name": taxonomy
        }
        insert_into_db("taxonomies", record)


def main():
    """Main function that creates taxonomies for a given organization."""

    parser = argparse.ArgumentParser(
        description='Create taxonomies for a specified organization in the database'
    )

    parser.add_argument(
        '--organization_id',
        type=str,
        help='Organization id to create taxonomy for',
        required=True
    )

    args = parser.parse_args()

    create_taxonomies(args.organization_id)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
