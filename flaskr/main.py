import logging
import pyrebase
import os
import pymysql

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, abort

import firebase_admin
from firebase_admin import credentials, firestore


app = Flask(__name__)

# Firebase details
firebaseConfig = {
    "apiKey": "AIzaSyBIYDxM_WvnjhiSL5SSZEM_mRsYelfvFgk",
    "authDomain": "ck-ad-1.firebaseapp.com",
    "projectId": "ck-ad-1",
    "storageBucket": "ck-ad-1.appspot.com",
    "messagingSenderId": "695010505553",
    "appId": "1:695010505553:web:c8594855c4a3a6734a1970",
    "measurementId": "G-G8SD0BZYBJ",
    "databaseURL": "",
}

# Initialize firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
# db = firebase.database()  # remove?

# Initialize firestore sdk
cred = credentials.Certificate("ck-ad-1-firebase-adminsdk-szo9b-4294d0a5ab.json")
firebase_admin.initialize_app(cred)
# initialize firestore instance
db = firestore.client()


# Initialise person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}


# SQL connect to database
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


# SQL get data
def get_data(cnx):
    with cnx.cursor() as cursor:
        fetched_items = cursor.execute('select * from item;')
        items = cursor.fetchall()
    if fetched_items > 0:
        return items
        # got_items = jsonify(items)  # Needed?
    else:
        got_items = 'No items in DB'
        return got_items


# SQL create data
def create_data(cnx, item):
    with cnx.cursor() as cursor:
        cursor.execute('INSERT INTO item (item_id, item_name) VALUES(%s, %s)', (item["4"], item["test"]))
    cnx.commit()
    cnx.close()


@app.route('/')
@app.route('/home')
def home():
    if person["is_logged_in"]:
        return render_template("user_home.html", email=person["email"], name=person["name"])
    else:
        return render_template("home.html")


@app.route('/data')  # methods=['GET']?
def data():
    fetched_data = get_data(conn)

    # firestore add data
    # db_data = {"name": "test", "age": 0, "address": "Location"}
    # db.collection(u'users').add(db_data)
    return render_template('data.html', data=fetched_data)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/account')
def account():
    return render_template('account.html', email=person["email"], name=person["name"])


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        request_result = request.form  # Get the data
        email = request_result["email"]
        password = request_result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            # Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            # Get the name of the user
            result_data = db.collection(u'users').document(person["uid"])
            result_data = result_data.get()
            result_data = result_data.to_dict()
            person["name"] = result_data["name"]
        except:
            # If there is any error, redirect to error
            return redirect(url_for('error_found'))
        else:
            # To home page
            return redirect(url_for('home'))
    else:
        if person["is_logged_in"]:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('error_found'))


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        register_result = request.form  # Get the data submitted
        name = register_result["name"]
        email = register_result["email"]
        password = register_result["pass"]
        confirm_password = register_result["confPass"]
        if password == confirm_password:
            try:
                # Try creating the user account using the provided data
                auth.create_user_with_email_and_password(email, password)
                # Login the user
                user = auth.sign_in_with_email_and_password(email, password)
                # Add data to global person
                global person
                person["is_logged_in"] = True
                person["name"] = name
                person["email"] = user["email"]
                person["uid"] = user["localId"]
                # Append data to the firebase realtime database
                register_data = {"name": name, "email": email}
                db.collection(u'users').document(person["uid"]).set(register_data)
            except:
                # If there is any error, redirect to error
                return redirect(url_for('error_found'))
            else:
                # To home page
                return redirect(url_for('home'))
    else:
        if person["is_logged_in"]:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('error_found'))


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return render_template('404.html'), 500


@app.route('/error')
def error_found():
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return render_template('404.html')


if __name__ == '__main__':
    conn = open_connection()
    app.run()
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)


# @app.route('/index')
# def index():
#     # For the sake of example, use static information to inflate the template.
#     # This will be replaced with real information in later steps.
#     dummy_times = [datetime.datetime(2021, 1, 1, 10, 0, 0),
#                    datetime.datetime(2021, 1, 2, 10, 30, 0),
#                    datetime.datetime(2021, 1, 3, 11, 0, 0),
#                    ]
#     return render_template('index.html', times=dummy_times)


# @app.route('/registerTemp')
# def form():
#     return render_template('register.html')
#     # [END form]
#     # [START submitted]
#
#
# @app.route('/add', methods=['POST'])
# def add_item():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400
#     create_data(conn, request.get_json())
#     return 'Item Added'
#
#
# @app.route('/submitted', methods=['POST'])
# def submitted_form():
#     name = request.form['name']
#     email = request.form['email']
#     site = request.form['site_url']
#     comments = request.form['comments']
#     # [END submitted]
#     # [START render_template]
#     return render_template(
#         'submitted_form.html',
#         name=name,
#         email=email,
#         site=site,
#         comments=comments)
#     # [END render_template]
