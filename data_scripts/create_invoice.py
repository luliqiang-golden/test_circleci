import argparse
import psycopg2
import psycopg2.extras

from db_functions import DATABASE
from activities.create_invoice import CreateInvoice
from constants import USER_ID
from class_errors import DatabaseError


def create_invoices(organization_id):
    order = orders[randint(0, len(orders)-1)]
    create_invoice(
        order=order,
        organization_id=organization_id,
        timestamp="2021-04-30 00:00:00"
    )


def create_invoice(order, organization_id, timestamp):
    try:
        invoice = {
            "name": "create_invoice",
            "organization_id": organization_id,
            "created_by": USER_ID,
            "order_id": order["id"],
            "timestamp": timestamp["timestamp"]
        }
        invoice_result = CreateInvoice.do_activity(invoice, {})


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_invoices(organization_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
