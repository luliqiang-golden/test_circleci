"""generate a csv report"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

from io import StringIO
import csv
from dateutil.relativedelta import relativedelta
import json
import os
import sys

from flask_restful import Resource
import flask

from db_functions import select_resource_from_db, DATABASE, select_from_db, rehydrate_resource
from class_errors import ClientBadRequest

from auth0_authentication import requires_auth


class ExportToCsv():
    def convert(self):

        report = self.__get_data()

        myFile = open('data.csv', 'w')
      
        with myFile:
            writer = csv.writer(myFile)

            # if you want to write the column names
            writer.writerow(report[0].keys())
            
            for row in report:
                writer.writerow(row.values())


    def __get_data(self):
        # you need to write the query over here.
        params = None
        query = '''
            SELECT *
            FROM activities
            LIMIT 1
        '''
        report_result = select_from_db(query, params)

        return list(map(lambda row: rehydrate_resource(row), report_result))
      
 
                    
if __name__ == "__main__":
   
    test_class = ExportToCsv()
    test_class.convert()
    

   