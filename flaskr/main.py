import logging
import os
from flask import Flask, render_template, request
import pymysql

# db_user = os.environ.get('CLOUD_SQL_USERNAME')
# db_password = os.environ.get('CLOUD_SQL_PASSWORD')
# db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
# db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    # # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # # set to `standard`
    # if os.environ.get('GAE_ENV') == 'standard':
    #     # If deployed, use the local socket interface for accessing Cloud SQL
    #     unix_socket = '/cloudsql/{}'.format(db_connection_name)
    #     cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
    # else:
    #     # If running locally, use the TCP connections instead
    #     # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
    #     # so that your application can use 127.0.0.1:3306 to connect to your
    #     # Cloud SQL instance
    #     host = '127.0.0.1'
    #     cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)
    #
    # with cnx.cursor() as cursor:
    #     cursor.execute('select product_name from product;')
    #     result = cursor.fetchall()
    #     current_msg = result[0][0]
    # cnx.close()
    #
    # return str(current_msg)
    # [END gae_python37_cloudsql_mysql]
    return render_template('home.html')


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
    app.run()
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)
