import os
import pymysql
from flask import jsonify

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def open_connection():
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
