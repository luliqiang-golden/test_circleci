#Varieties generator
import argparse
import pandas as pd

def generate_accounts(organization_id):
    
    names = [
        'Researcher',
        'License Holder',
        'Lab',
        'Wholesale',
        'Distributor',
        'Retailer',
        'Supplier',
        'Patient',
        'Government',
        'Individual',
        'Recreational Consumer',
    ]

    _type = [
        'researcher',
        'license holder',
        'lab',
        'wholesale',
        'distributor',
        'retailer',
        'supplier',
        'patient',
        'government',
        'individual',
        'recreational consumer'
    ]

    email = [
        'researcher@test.com',
        'license_holder@test.com',
        'lab@test.com',
        'wholesale@test.com',
        'distributor@test.com',
        'retailer@test.com',
        'supplier@test.com',
        'patient@test.com',
        'government@test.com',
        'individual@test.com',
        'recreational_consumer@test.com'
    ]

    address_1 = [
        'rue Levy',
        'Main St',
        'Baker Street',
        'Horner Ave',
        'Pape Ave',
        'Bridgeport Rd',
        'Saskatchewan Dr',
        'A Avenue',
        'Brook St',
        'Toy Avenue',
        'rue des Églises Est'
    ]

    address_2 = [
        '2807',
        '2941',
        '1920',
        '302',
        '900',
        '3911',
        '4765',
        '3139',
        '4216',
        '2418',
        '169'
    ]

    city = [
        'Montreal',
        'Aylesford',
        'London',
        'Toronto',
        'Toronto',
        'Alliston',
        'Quebec',
        'Edmonton',
        'Kentville',
        'Oshawa',
        'Malartic'
    ]

    province = [
        'Quebec',
        'Nova Scotia',
        'Ontario',
        'Ontario',
        'Ontario',
        'Ontario',
        'Quebec',
        'Alberta',
        'Nova Scotia',
        'Ontario',
        'Quebec'
    ]

    postal_code = [
        'H3C 5K4',
        'B0P 1C0',
        'N0N 0N0',
        'M8W 4Y4',
        'M4E 2V5',
        'L9R 1H4',
        'S4P 3Y2',
        'T5J 0K7',
        'B4N 2N3',
        'L1H 7K5',
        'J0Y 1Z0'
    ]

    country = [
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
        'Canada',
    ]

    telephone = [
        '514-754-6683',
        '902-341-0182',
        '519-432-5226',
        '647-435-7336',
        '416-690-6621',
        '705-435-8535',
        '418-681-2931',
        '780-442-4052',
        '902-691-4086',
        '905-925-2519',
        '819-757-1845',
    ]

    accounts_data = {
        'name': names,
        'type': _type,
        'email': email,
        'address1': address_1,
        'address2': address_2,
        'city': city,
        'province': province,
        'postal code': postal_code,
        'country': country,
        'telephone': telephone,
        'organization_id': organization_id
    }


    df = pd.DataFrame(accounts_data)  

    df.to_csv('../template_client_helper_scripts/create crm accounts.csv', index=False, encoding='utf-8', sep=',')
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_accounts(args.org_id)