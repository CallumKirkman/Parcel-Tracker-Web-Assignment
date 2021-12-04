import os
import pymysql
from flask import jsonify


# # Alternate connection
# # When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
#     if os.environ.get('GAE_ENV') == 'standard':
#         # If deployed, use the local socket interface for accessing Cloud SQL
#         unix_socket = '/cloudsql/{}'.format(db_connection_name)
#         cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
#     else:
#         # If running locally, use the TCP connections instead Set up Cloud SQL Proxy
#         # (cloud.google.com/sql/docs/mysql/sql-proxy) so that your application can use
#         # 127.0.0.1:3306 to connect to your cloud SQL instance
#         host = '127.0.0.1'
#         cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)
#
#     with cnx.cursor() as cursor:
#         cursor.execute('select item_name from item;')
#         result = cursor.fetchall()
#         current_msg = result[0][0]
#     cnx.close()
#
#     # current_msg = current_msg


def open_connection():
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user,
                                   password=db_password,
                                   unix_socket=unix_socket,
                                   db=db_name,
                                   cursorclass=pymysql.cursors.DictCursor)
            return conn
    except pymysql.MySQLError as e:
        return e


def get():
    conn = open_connection()
    with conn.cursor() as cursor:
        result = cursor.execute('select * from item;')
        items = cursor.fetchall()
    if result > 0:
        got_items = jsonify(items)
    else:
        got_items = 'No items in DB'
    return got_items


def create(item):
    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO item (item_id, item_name) VALUES(%s, %s)', (item["4"], item["test"]))
    conn.commit()
    conn.close()
