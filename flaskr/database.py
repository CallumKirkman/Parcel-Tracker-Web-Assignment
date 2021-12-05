import os
import pymysql

from dotenv import load_dotenv
from flask import jsonify

# TODO: Use Datastore for users? - Lab 3


def open_connection():
    try:
        # When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
        if os.environ.get('GAE_ENV') == 'standard':
            db_user = os.environ.get('CLOUD_SQL_USERNAME')
            db_password = os.environ.get('CLOUD_SQL_PASSWORD')
            db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
            db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

            # If deployed, use the local socket interface for accessing Cloud SQL
            unix_socket = '/cloudsql/{}'.format(db_connection_name)
            cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name,
                                  cursorclass=pymysql.cursors.DictCursor)
        else:
            load_dotenv()
            db_user = os.getenv('CLOUD_SQL_USERNAME')
            db_password = os.getenv('CLOUD_SQL_PASSWORD')
            db_name = os.getenv('CLOUD_SQL_DATABASE_NAME')

            # If running locally, use the TCP connections instead
            # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
            host = '127.0.0.1'
            port = 1433
            cnx = pymysql.connect(user=db_user, password=db_password, host=host, port=port, db=db_name,
                                  cursorclass=pymysql.cursors.DictCursor)

    except pymysql.MySQLError as e:
        return e

    return cnx


def get_data(conn):
    # conn = open_connection()
    with conn.cursor() as cursor:
        result = cursor.execute('select * from item;')
        items = cursor.fetchall()
    if result > 0:
        return items
        # got_items = jsonify(items)  # Needed?
    else:
        got_items = 'No items in DB'
        return got_items


def create_data(conn, item):
    # conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO item (item_id, item_name) VALUES(%s, %s)', (item["4"], item["test"]))
    conn.commit()
    conn.close()