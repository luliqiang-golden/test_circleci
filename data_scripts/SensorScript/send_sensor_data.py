import sys
import argparse
from datetime import datetime, timedelta
from random import randint
import json
from ruamel import yaml
import hammock


sys.tracebacklimit = 0
CONFIG_FILE = 'config.yaml'

def try_parse_int(sensor, base=10):
    try:
        int(sensor, base)
        return True
    except ValueError:
        return False

def initialize():

    parser=argparse.ArgumentParser()

    #condition to accept -orgs, -equip and -sensor_data parameteres without other mandatory fields

    mutual_inclusive_condition = ('-orgs' not in sys.argv and 
                                  '-equip' not in sys.argv and 
                                  '-sensor_data' not in sys.argv)

    parser.add_argument('-e',
                        help='Sensor API endpoint, '
                        'if not passed as an argument, '
                        'will read from a configuration file on the same folder of the script '
                        '[python send_sensor_data.py -e <optional_endpoint>]',
                        type=str,
                        default=CONFIG_FILE)

    parser.add_argument('-u',
                        help='growerIQ username, '
                        'if not passed as an argument, '
                        'will read from a configuration file on the same folder of the script '
                        '[python send_sensor_data.py -u <optional_username>]',
                        type=str,
                        default=CONFIG_FILE)

    parser.add_argument('-p',
                        help='growerIQ password, '
                        'if not passed as an argument, '
                        'will read from a configuration file on the same folder of the script '
                        '[python send_sensor_data.py -p <optional_password>]',
                        type=str,
                        default=CONFIG_FILE)

    parser.add_argument('-orgs',
                        help='Pass, as argument, '
                        'provides list of available orgs in the instance '
                        '[python send_sensor_data.py -orgs]',
                        action='store_true')

    parser.add_argument('-equip',
                        help='Pass, as argument, '
                        'list of equipaments (sensor + room information) '
                        '[python send_sensor_data.py -equip all OR <room_name> OR <sensor_id> OR <sensor_name> -org <org_id>]')

    parser.add_argument('-sensor_data',
                        help='Pass, as argument, '
                        'list sensor top 20 latest entries '
                        '[python send_sensor_data.py -sensor_data '
                        '-s <sensor_id> -org <org_id> '
                        'OR python send_sensor_data.py -sensor_data '
                        '-s <sensor_name> -org <org_id>]',
                        action='store_true')

    parser.add_argument('-s',
                        help='Pass, as argument, '
                        'the sensor name or ID to view data on frontend '
                        '[python send_sensor_data.py -s "<sensor_id>" '
                        'OR python send_sensor_data.py -s "<sensor_name>"] '
                        'in case of duplicate names the script considers the one with lowest ID',
                        type=str,
                        required=mutual_inclusive_condition)

    parser.add_argument('-org',
                        help='Pass, as argument, '
                        'if org id provided set the organization value '
                        '[python send_sensor_data.py -org '
                        '<org_id> -s "<sensor_id>" -value "<sensor_reading>"]',
                        type=int,
                        required=mutual_inclusive_condition)

    parser.add_argument('-date',
                        help='Pass, as argument, '
                        'datetime of the reading (yyyy-MM-dd HH:mm:ss+00) format'
                        'If you pass this value with -value parameter, '
                        'it is going to add the entry with the timestamp provided here, '
                        'if you pass this value with -hist parameter it is going to consider '
                        'the current date as the last day and create entries in the past '
                        'the default value is the current date time ',
                        type=str)

    group = parser.add_mutually_exclusive_group(required=mutual_inclusive_condition)

    group.add_argument('-value',
                        help='Pass, as argument, '
                        'value read by sensor '
                        '[python send_sensor_data.py -value '
                        '<sensor_reading> -s <sensor_id> -org <org_id>]',
                        type=int)

    group.add_argument('-hist',
                        help='Pass, as argument, '
                        'the sensor and value in days to create random historical '
                        'data right in the sensor data table '
                        '[python send_sensor_data.py -hist <#_days> -s <sensor_id> -org <org_id>]',
                        type=int)

    return parser.parse_args()

def get_token_api(e, u, p):

    credentials = {
        'username': u,
        'password': p
    }

    token_api = hammock.Hammock(e)
    token_temp = token_api.v1.login.POST(json=credentials)

    return token_temp.json()['access_token']

def parse_endpoint(e):

    if e == CONFIG_FILE:
        data = yaml.safe_load(open(CONFIG_FILE))
        return data['sensor_endpoint']
    else:
        return e

def parse_username(u):

    if u == CONFIG_FILE:
        data = yaml.safe_load(open(CONFIG_FILE))
        return data['groweriq_username']
    else:
        return u

def parse_password(p):

    if p == CONFIG_FILE:
        data = yaml.safe_load(open(CONFIG_FILE))
        return data['groweriq_password']
    else:
        return p

def get_sensor_details(e, s, t, o):

    api = hammock.Hammock(e, headers={'authorization': "Bearer {0}".format(t)})

    if try_parse_int(s):
        sensor_details = (api.v1.organizations(o).sensors.GET(params={
                                                             'filter':'sensor_id='+s,
                                                             'order_by':'timestamp:DESC'
                                                             }).json())
        unit_type_temp = (sensor_details['data'][0]['unit_type'])
        sensor_type_temp = (sensor_details['data'][0]['sensor_type'])
        return s, unit_type_temp, sensor_type_temp

    else:    
        response = (api.v1.organizations(o).equipment.GET(params={'filter':'type=sensor', 'filter':'name='+s, 'order_by':'reading_timestamp:DESC'}).json())

        if(int(response['total']) == 0):
            raise Exception("No sensor found for name: {0}".format(s))

        else:
            s = response['data'][0]['id']
            sensor_details = (api.v1.organizations(o).sensors.GET(params={'filter':'sensor_id='+s, 'order_by':'timestamp:DESC'}).json())
            unit_type = (sensor_details['data'][0]['unit_type'])
            sensor_type = (sensor_details['data'][0]['sensor_type'])
            return s, unit_type, sensor_type

def list_orgs(e, t):

    print('not implemented yet :(, sorry')

def list_equip(e, o, t, resource):

    api = hammock.Hammock(e, headers={'authorization': "Bearer {0}".format(t)})

    if try_parse_int(resource):
        response = api.v1.organizations(o).equipment.GET(params={'filter':'type=sensor', 'filter': 'id='+resource, 'per_page':'1000'})
        print(json.dumps(response.json(), indent=4, sort_keys=True))
    else:
        if resource != 'all':
            response = api.v1.organizations(o).equipment.GET(params={'filter':'type=sensor', 'filter': 'name|room='+resource, 'per_page':'1000'})
            print(json.dumps(response.json(), indent=4, sort_keys=True))
        else:
            response = api.v1.organizations(o).equipment.GET(params={'filter':'type=sensor', 'per_page':'1000'})
            print(json.dumps(response.json(), indent=4, sort_keys=True))

def get_sensor_data(e, o, t, sa):

    api = hammock.Hammock(e, headers={'authorization': "Bearer {0}".format(t)})

    response = api.v1.organizations(o).sensors.GET(params={'filter':'sensor_id='+sa, 'order_by':'timestamp:DESC'})

    print(json.dumps(response.json(), indent=4, sort_keys=True)) 

def add_sensor_entry(e, o, t, sv, sid, ut, st, rt):

    if(rt is None):
        rt = datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")

    payload = {
        "sensor_reading":sv,
        "sensor_id":sid,
        "unit_type":ut,
        "sensor_type":st,
        "reading_timestamp":rt
    }

    api = hammock.Hammock(e, headers={'authorization': "Bearer {0}".format(t), 'content-type':'application/json'})
    response = api.v1.organizations(o).sensors.POST(json=payload)

    if(response.status_code == 200):
        print('entry added successfully')
    else:
        print('something went wrong')

def add_sensor_history(e, o, t, sid, ut, st, h):

    api = hammock.Hammock(e, headers={'authorization': "Bearer {0}".format(t), 'content-type':'application/json'})

    for day in range(h):

        value_ranges = {
            'temperature' : randint(0, 60),
            'humidity': randint(10, 100),
            'co2': randint(100, 300)
        }

        today = datetime(
                        year = datetime.now().year, 
                        month = datetime.now().month, 
                        day = datetime.now().day,
                        hour = randint(0, 23),
                        minute = randint(0, 59),
                        second = randint(0, 59)
                        )

        days_to_decrease = timedelta(days = (h - day -1))

        rt = (today - days_to_decrease).strftime("%Y-%m-%d %H:%M:%S%z")

        payload = {
            'sensor_reading':value_ranges[st],
            'sensor_id':sid,
            'unit_type':ut,
            'sensor_type':st,
            'reading_timestamp':rt
        }

        response = api.v1.organizations(o).sensors.POST(json=payload)

        if(response.status_code == 200):
            print('day {0} added successfully'.format(day))
        else:
            print('something went wrong for day {0}'.format(day))

if __name__ == '__main__':

    args=initialize()

    endpoint = parse_endpoint(args.e)
    username = parse_username(args.u)
    password = parse_password(args.p)


    historical_data = args.hist
    sensor_value = args.value
    org = args.org
    reading_date = args.date

    token = get_token_api(endpoint, username, password)

    if(args.orgs):
        list_orgs(endpoint, token)

    elif(args.equip):
        list_equip(endpoint, org, token, args.equip)

    else:
        sensor_details = get_sensor_details(endpoint, args.s, token, org)

        sensor_id = sensor_details[0]
        unit_type = sensor_details[1]
        sensor_type = sensor_details[2]
        
        if(args.sensor_data):
            get_sensor_data(endpoint, org, token, sensor_id)

        elif(sensor_value is not None):
            add_sensor_entry(endpoint, org, token, sensor_value, sensor_id, unit_type, sensor_type, reading_date)

        elif(historical_data is not None):
            add_sensor_history(endpoint, org, token, sensor_id, unit_type, sensor_type, historical_data)
