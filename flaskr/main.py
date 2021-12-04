import logging
import os
import pymysql

from flask import Flask, render_template, request, jsonify

# from flaskr.db import get, create

app = Flask(__name__)


def open_connection():
    db_user = os.environ.get('CLOUD_SQL_USERNAME')
    db_password = os.environ.get('CLOUD_SQL_PASSWORD')
    db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
    db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

    try:
        # When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
        if os.environ.get('GAE_ENV') == 'standard':
            # If deployed, use the local socket interface for accessing Cloud SQL
            unix_socket = '/cloudsql/{}'.format(db_connection_name)
            cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name,
                                  cursorclass=pymysql.cursors.DictCursor)
        else:
            # If running locally, use the TCP connections instead
            # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
            host = '127.0.0.1'
            port = 1433
            cnx = pymysql.connect(user=db_user, password=db_password, host=host, port=port, db=db_name,
                                  cursorclass=pymysql.cursors.DictCursor)

    except pymysql.MySQLError as e:
        return e

    return cnx


def get_data():
    conn = open_connection()
    with conn.cursor() as cursor:
        result = cursor.execute('select * from item;')
        items = cursor.fetchall()
    if result > 0:
        got_items = jsonify(items)
    else:
        got_items = 'No items in DB'
    return got_items


def create_data(item):
    conn = open_connection()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO item (item_id, item_name) VALUES(%s, %s)', (item["4"], item["test"]))
    conn.commit()
    conn.close()


@app.route('/', methods=['GET'])
def get_items():
    return get_data()


@app.route('/add', methods=['POST'])
def add_item():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    create_data(request.get_json())
    return 'Item Added'


# @app.route('/')
# @app.route('/home')
# def home():
#     return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register')
def form():
    return render_template('register.html')
    # [END form]
    # [START submitted]


@app.route('/submitted', methods=['POST'])
def submitted_form():
    name = request.form['name']
    email = request.form['email']
    site = request.form['site_url']
    comments = request.form['comments']
    # [END submitted]
    # [START render_template]
    return render_template(
        'submitted_form.html',
        name=name,
        email=email,
        site=site,
        comments=comments)
    # [END render_template]


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # conn = open_connection()
    app.run()
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)
