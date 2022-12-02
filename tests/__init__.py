import os
import flask_testing
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Api

import tests.helpers
from app import app, db, DB_HOST, DB_USERNAME,DB, DB_PASSWORD, sql_url
import auth0_authentication
from api_encoder import CustomJSONEncoder

import psycopg2


DB = 'seed-to-sale-test'
sql_url = "postgresql://{0}:{1}@{2}/{3}".format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB)


class TestCase(flask_testing.TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = sql_url
        app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False
        return app
        
    def tearDown(self):
        db.session.remove()
        tables = [
            "public.signatures",
            "public.activities",
            "public.inventories",
            "public.users",
            "public.organizations",
            "public.health_canada_report",
            "public.currencies",
            "public.order_items",
            "public.skus",
            "public.orders",
            "public.shipments",
            "public.crm_accounts",
            "public.sensors_data",
            "public.consumable_classes",
            "public.consumable_lots",
            "public.role",
            "public.role_permission",
            "public.user_role",
            "public.user_role_history",
            "public.permission_role_history"
        ]
        TestCase.delete_data(self,tables)
        TestCase.reset_sequence(self,tables)

    def delete_data(self, tables):
        con = psycopg2.connect(host=DB_HOST, database=DB,user=DB_USERNAME, password=DB_PASSWORD)
        for t in tables:
            cur = con.cursor()
            sql = 'TRUNCATE ' + t + ' RESTART IDENTITY CASCADE;'
            cur.execute(sql)
            con.commit()
        con.close()

    def reset_sequence(self, tables):
        con = psycopg2.connect(host=DB_HOST, database=DB,user=DB_USERNAME, password=DB_PASSWORD)
        for t in tables:
            cur = con.cursor()
            ending = ("_seq" if t == "public.health_canada_report" else "_id_seq")
            
            if(t == 'public.shipments'):
                t = 'public.shipment'
            elif(t == 'public.sensors_data'):
                t = 'public.sensor'
                
            sql = 'ALTER SEQUENCE IF EXISTS ' + t + ending + ' RESTART WITH 1;'
            cur.execute(sql)
            con.commit()
        con.close()
