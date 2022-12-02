#Varieties generator
import argparse
import pandas as pd

def generate_varieties(organization_id):
    varieties = ['Granddaddy Purple', 
            'Purple Punch', 
            'G13', 
            'Bubba Kush', 
            'Purple Kush', 
            'LA Confidential', 
            '9 Pound Hammer', 
            'Purple Urkle', 
            'Blackberry Kush', 
            'Hindu Kush', 
            'Pink Kush', 
            'Afgooey', 
            'Romulan', 
            'OG Kush', 
            'Ice Cream Cake', 
            'Apple Fritter', 
            'Peanut Butter Breath', 
            'Sour Diesel', 
            'Maui Wowie', 
            'Durban Poison', 
            'Acapulco Gold', 
            'Green Crack', 
            'Super Lemon Haze', 
            'Super Silver Haze', 
            'White Fire OG']

    strains = ['Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Indica',
                'Hybrid',
                'Indica',
                'Indica',
                'Hybrid',
                'Indica',
                'Hybrid',
                'Hybrid',
                'Sativa',
                'Sativa',
                'Sativa',
                'Sativa',
                'Sativa',
                'Sativa',
                'Sativa',
                'Hybrid']

    varieties_data = {'strain': strains, 'variety': varieties, 'organization_id': organization_id}  

    df = pd.DataFrame(varieties_data)  

    df.to_csv('../template_client_helper_scripts/varieties import.csv', index=False, encoding='utf-8', sep=',')
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_varieties(args.org_id)