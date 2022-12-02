# Import libraries from parent folder
from class_errors import DatabaseError
from constants import USER_ID
from utilities import select_from_db
from db_functions import DATABASE, insert_into_db
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def get_taxonomy_id_from_name(organization_id, name):
    params = {}
    params["organization_id"] = organization_id
    params["name"] = name

    query = '''
        SELECT *
        FROM taxonomies AS t
        WHERE t.organization_id=%(organization_id)s
        AND t.name = %(name)s
    '''
    result = select_from_db(query, params)
    return select_from_db(query, params)[0]["id"]


def get_taxonomy_option_data_from_name(organization_id, name):
    params = {}
    params["organization_id"] = organization_id
    params["name"] = name

    query = '''
        SELECT *
        FROM taxonomy_options AS t
        WHERE t.organization_id=%(organization_id)s
        AND t.name = %(name)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result[0]


def get_taxonomy_option_by_taxonomy_name(organization_id, name):
    params = {}
    params["organization_id"] = organization_id
    params["name"] = name

    query = '''
        SELECT op.* FROM taxonomies AS t
			INNER JOIN taxonomy_options AS op ON t.id = op.taxonomy_id AND t.organization_id = op.organization_id
		WHERE t.organization_id = %(organization_id)s and t.name = %(name)s
        ORDER BY op.id
    '''

    result = select_from_db(query, params)
    if (result):
        return result


def create_taxonomy_option(organization_id, name, taxonomy_id, data={}):
    record = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": name,
        "taxonomy_id": taxonomy_id,
        **data
    }
    insert_into_db("taxonomy_options", record)


def create_taxonomy_options(org_id=None, variety_strains=None):
    # Create taxonomy options for labels
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="labels"
    )

    create_taxonomy_option(
        organization_id=org_id,
        taxonomy_id=taxonomy_id,
        name="Batch/Lot/Mother Label",
        data={"format": "ZPL",
              "fields": [
                  {
                      "y": 33.495000000000005,
                      "x": 37.5,
                      "type": "heading",
                      "text": "{data[name]}"
                  },
                  {
                      "y": 133.98000000000002,
                      "x": 37.5,
                      "type": "text",
                      "label": "{data[type]} ID: {data[id]}"
                  },
                  {
                      "y": 167.47500000000002,
                      "x": 37.5,
                      "type": "text",
                      "label": "Room: {data[room]}"
                  },
                  {
                      "y": 200.97000000000003,
                      "x": 37.5,
                      "type": "text",
                      "label": "Created: {data[timestamp]}"
                  },
                  {
                      "y": 301.45500000000004,
                      "x": 37.5,
                      "type": "barcode"
                  }
              ],
              "tableName": "inventories",
              "height": 2,
              "width": 4,
              "subType": "",
              "template": "^XA^CWY,E:OPENSANS-BOLD.TTF^CWZ,E:OPENSANS-REGULAR.TTF^BY4,7^FO37.5,33.495000000000005^AYN,44^FD{data[name]}^FS\n^FO37.5,133.98000000000002^AZN,30^FD{data[type]} ID: {data[id]}^FS\n^FO37.5,167.47500000000002^AZN,30^FDRoom: {data[room]}^FS\n^FO37.5,200.97000000000003^AZN,30^FDCreated: {data[timestamp]}^FS\n^FO37.5,301.45500000000004^B7N,7,0,,,N^FD{barcode_data}^FS^XZ",
              "type": "inventory"}
    )

    # Create taxonomy options for varieties
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="varieties"
    )

    for variety in variety_strains:
        create_taxonomy_option(
            organization_id=org_id,
            name=variety,
            taxonomy_id=taxonomy_id,
            data={"strain": variety_strains[variety]}
        )

    # Create taxonomy options for waste types
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="waste_types"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="leaves",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="flowers",
        taxonomy_id=taxonomy_id,
        data={"description": "dead"}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="stems",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    # Create taxonomy options for destruction methods
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="destruction_methods"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Shredding",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Compost",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    # Create taxonomy options for compost types
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="compost_types"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="stem",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="roots",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    # Create taxonomy options for pest types
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="pest_types"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Aphids",
        taxonomy_id=taxonomy_id,
        data={"description": "Puceron"}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Spider Mite",
        taxonomy_id=taxonomy_id,
        data={"description": "Acariens"}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Mealybug",
        taxonomy_id=taxonomy_id,
        data={"description": "Cochenille farineuse"}
    )


    # Create taxonomy options for destruction reasons
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="destruction_reasons"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Daily sweep",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Harvest trimmings",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    # Create taxonomy options for upload categories
    taxonomy_id = get_taxonomy_id_from_name(
        organization_id=org_id, name="upload_categories"
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Lab Result",
        taxonomy_id=taxonomy_id,
        data={"description": ""}
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="Testing",
        taxonomy_id=taxonomy_id
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="received-unapproved",
        taxonomy_id=taxonomy_id,
        data={"allowed_previous_stages": [
            ""
        ],
            "allowed_inventory_types": [
            "received inventory"
        ],
            "description": ""
        }
    )

    create_taxonomy_option(
        organization_id=org_id,
        name="received-approved",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "received-unapproved"
            ],
            "allowed_inventory_types": [
                "received inventory"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="planning",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                ""
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="germinating",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                ""
            ],
            "allowed_inventory_types": [
                "mother",
                "batch"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="propagation",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "",
                "planning",
                "germinating"
            ],
            "allowed_inventory_types": [
                "mother",
                "batch"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="vegetation",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "propagation"
            ],
            "allowed_inventory_types": [
                "mother",
                "batch"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="flowering",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "vegetation"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": ""
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="harvesting",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "flowering"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "first part of harvesting process"
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="extracting_crude_oil",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "harvesting",
                "drying",
                "curing"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "cannot go to drying"
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="distilling",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "extracting_crude_oil"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "cannot go to drying"
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="drying",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "harvesting"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "second step of harvesting process"
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="curing",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "drying"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "third step of harvesting process"
        }
    )
    create_taxonomy_option(
        organization_id=org_id,
        name="qa",
        taxonomy_id=taxonomy_id,
        data={
            "allowed_previous_stages": [
                "curing",
                "extracting_crude_oil"
            ],
            "allowed_inventory_types": [
                "batch"
            ],
            "description": "Quality Assurance"
        }
    )


def main():
    """Main function that creates taxonomy options for a given organization."""

    parser = argparse.ArgumentParser(
        description='Create taxonomy options for a specified organization in the database'
    )

    parser.add_argument(
        '--organization_id',
        type=str,
        help='Organization id to create taxonomy option for',
        required=True
    )

    parser.add_argument(
        '--name',
        type=str,
        help='Name of taxonomy option',
        required=True
    )

    parser.add_argument(
        '--taxonomy_id',
        type=int,
        help='Taxonomy id to create option under',
        required=True
    )

    args = parser.parse_args()

    create_taxonomy_option(
        args.organization_id,
        args.name,
        args.taxonomy_id
    )


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
