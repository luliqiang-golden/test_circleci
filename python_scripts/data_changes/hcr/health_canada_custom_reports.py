# Import libraries
import datetime as dt
import calendar
import time
import json

from report_functions import *

# Report Parameters
ORG_ID = 1
YEAR = 2021
MONTH = 8
DAY = 31
FULL_MONTH = True

f = open('../../reporting/canada_report_columns.json')

reporting_columns = json.load(f)
reporting_columns_names = list(dict.fromkeys(reporting_columns.keys()))
reporting_columns_vars = dict.fromkeys(reporting_columns.values())
reporting_columns_vars.pop(0, None)
reporting_columns_vars = list(reporting_columns_vars)

f.close()

# Set up cursor
conn = psycopg2.connect(f'dbname={DB_NAME} host={DB_HOST} password={DB_PASSWORD} user={DB_USERNAME}')
cursor = conn.cursor()

last_month_day = calendar.monthrange(YEAR, MONTH)[1]
datelist = pd.date_range(start=f'{YEAR}-{MONTH}-{DAY}', end=f'{YEAR}-{MONTH}-{last_month_day}', freq = 'D').to_list()

filled_columns = []

def extract_daily_report(date: str) -> dict:
    result = dict()
    ## OPENING
    open_inventory_initial_date = (pd.Timestamp(date) - pd.Timedelta("1Y")).strftime('%Y-%m-%d')
    open_inventory_final_date = (pd.Timestamp(date) - pd.Timedelta("1D")).strftime('%Y-%m-%d')


    result.update(pd_f_hc_report_opening_inventory(open_inventory_initial_date, open_inventory_final_date, ORG_ID))

    ## ADDITION AND REDUCTION ##
    result.update(pd_f_hc_report_inventory_produced_processed(date, date, ORG_ID))
    ## ADDITION AND REDUCTION ##

    ## ADDITIONS
    result.update(pd_f_hc_report_received_inventory(date, date, ORG_ID))
    # result.update(pd_f_hc_report_other_additions(date, date, ORG_ID))

    ## REDUCTIONS
    result.update(pd_f_hc_report_inventory_packaged_label(date, date, ORG_ID))
    result.update(pd_f_hc_report_inventory_shipped_domestic(date, date, ORG_ID))
    result.update(pd_f_hc_report_inventory_shipped_testers(date, date, ORG_ID))
    result.update(pd_f_hc_report_inventory_adjustment_loss(date, date, ORG_ID))
    result.update(pd_f_hc_report_inventory_destroyed(date, date, ORG_ID))

    ## CLOSING
    result.update(pd_f_hc_report_closing_inventory(open_inventory_initial_date, date, ORG_ID))

    return result

def generate_report_dataframe(report: dict, date) -> pd.DataFrame:
    report_df = pd.DataFrame(columns=reporting_columns_vars)

    for i in report.keys():
        filled_columns.append(i)
        report_df.loc[0, 'report_period_year'] = date
        report_df.loc[0, 'report_period_month'] = date
        report_df.loc[0, i] = report[i]

    return report_df

def generate():
    # Run the main program - this is in the same sequence as that in the report
    out_df = pd.DataFrame(columns=reporting_columns_vars)

    rows = [pd.Timestamp(f'{YEAR}-{MONTH}-{DAY}')]

    if FULL_MONTH:
        rows = pd.date_range(start=f'{YEAR}-{MONTH}-01', end=f'{YEAR}-{MONTH}-{calendar.monthrange(YEAR, MONTH)[1]}',
                                   freq='D').to_list()

    for i in range(len(rows)):
        start_time = time.time()
        current_date = rows[i].strftime('%Y-%m-%d')

        data = extract_daily_report(current_date)
        data_df = generate_report_dataframe(data, current_date)
        out_df = pd.concat([out_df, data_df], ignore_index = True)

        print(f'Completed {current_date} in {(time.time() - start_time):.2f} secs')

    export_csv(out_df)

def export_csv(data_df):

    # Add columns as per health canada report
    # Get the columns that are present and rename them using a dictionary.
    var_names = []
    report_names = []
    for key, value in reporting_columns.items():
        if value != 0 and value not in var_names:
            var_names.append(value)
            report_names.append(key)

    rename_dict = dict(zip(var_names, report_names))

    # Get the full column names
    report_columns_list = list(reporting_columns_names)

    # Rename columns that are present
    data_df.rename(columns=rename_dict, inplace=True)

    # Add the columns that are not present
    not_present_columns = set(report_columns_list) - set(data_df.columns.to_list())
    data_df.loc[:, not_present_columns] = 0
    # out_df

    # Reorder
    out_df = data_df[report_columns_list]

    # Export to a csv file
    out_df.to_csv('daily_hc_' + dt.datetime.strftime(dt.datetime.utcnow(), '%Y%m%d') + '.csv', index=False)

generate()