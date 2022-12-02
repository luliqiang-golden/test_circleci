# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

from activities.department_create import DepartmentCreate
from constants import USER_ID
from db_functions import DATABASE, DatabaseError


def create_department(organization_id, name):
    record = {
        "name": "department_create",
        "organization_id": organization_id,
        "created_by": USER_ID,
        "department_name": name
    }

    DepartmentCreate.do_activity(record, {})


def create_departments(organization_id):
    """Main function that creates a department for a given organization.
    """

    create_department(
        organization_id=organization_id,
        name='Management'
    )

    create_department(
        organization_id=organization_id,
        name='Warehouse'
    )

    create_department(
        organization_id=organization_id,
        name='Cultivation'
    )


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        # Begin DB transaction
        DATABASE.dedicated_connection().begin()

        create_departments(organization_id)

        # Commit DB transaction
        DATABASE.dedicated_connection().commit()
