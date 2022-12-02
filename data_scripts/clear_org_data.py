# Import libraries from parent folder
import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) +
    '/python_scripts')

from db_functions import DATABASE, clear_table_in_org, delete_from_db, clear_table
import re


def clear_org_data(opts=None):
    """ Clear out all specified tables defined in this script for a given organization.

    :type opts: dictionary
    :param opts: Contains options for running this script without interactive prompts

    :rtype: void
    """

    yes = re.compile("Y", re.IGNORECASE)
    no = re.compile("N", re.IGNORECASE)

    if opts is None:
        prompt = input(
            "Do you wish to clear out an organization's data (this action cannot be reversed)? (Y/N): "
        )
    else:
        prompt = opts["clear_org"]

    if not yes.match(prompt):
        return print("Exiting program without clearing data")

    while True:
        try:
            if opts is None:
                prompt = input(
                    "Enter the organization id you wish to clear for: "
                )
            else:
                prompt = opts["org_id"]

            org_id = int(prompt)
            break
        except ValueError:
            print("Error: Entered invalid organization id")

    print("Clearing out data in organization {}".format(org_id))

    # TODO: Add commented tables once those data scripts are completed
    tables = [
        "signatures",
        "activities",
        "capa_actions",
        "capa_links",
        "capas",
        "order_items",
        "orders",
        "shipments",
        "transaction_allocations",
        "consumable_lots",
        "consumable_classes",
        "transactions",
        "crm_accounts",
        # "equipment",
        "inventories",
        "invoices",
        "recalls",
        "rooms",
        # "rules",
        "skus",
        "taxonomy_options",  # must be before taxonomies
        "taxonomies",
        "sop_versions_departments",
        "departments",
        "sop_assignments",
        "sop_versions",
        "sops"

        # "uploads",  # create_activity_sample_lab_result_received from create_sample upload_id is hard coded to 287
        # "users",  # must be third to last
        # "roles",  # must be second to last
        # "organizations",  # must be last, because org ID is referenced
    ]

    for table in tables:
        # Use prompts if you wish to specifically remove tables
        # prompt = input(
        #     "Do you want to delete from {} table? (Y/N): ".format(table))
        # if no.match(prompt):
        #     print("Skipping delete from {} table".format(table))
        #     continue

        if table == "organizations":
            delete_from_db(
                resource=table, resource_id=org_id, organization_id=None)
        else:
            clear_table_in_org(organization_id=org_id, table=table)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    clear_org_data()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
