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

# Initialize firestore sdk
cred = credentials.Certificate("ck-ad-1-firebase-adminsdk-szo9b-4294d0a5ab.json")
firebase_admin.initialize_app(cred)
# initialize firestore instance
db = firestore.client()


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
def get_data(item, table, column, column_id):  # TODO: is table needed?
    cnx = open_connection()

    with cnx.cursor() as cursor:
        if column is None:
            # Get everything
            fetched_items = cursor.execute('select %s from %s;' % (item, table))
            items = cursor.fetchall()
        else:
            # Get specific entry
            fetched_items = cursor.execute("select * from %s where %s='%s';" % (table, column, column_id))
            items = cursor.fetchone()
    if fetched_items > 0:
        return items
    else:
        got_items = 'No items in DB'
        return got_items


# SQL create data
def create_data(item):
    cnx = open_connection()
    with cnx.cursor() as cursor:
        cursor.execute('INSERT INTO item (item_id, item_name) VALUES(%s, %s)' % (item["4"], item["test"]))
    cnx.commit()
    cnx.close()


# Initialise person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}


@app.context_processor
def inject_status():
    return dict(logg_status=person["is_logged_in"], name=person["name"], email=person["email"], uid=person["uid"])


@app.route('/')
@app.route('/home')
def home():
    if person["is_logged_in"]:
        return render_template("user_home.html")
    else:
        return render_template("home.html")


@app.route('/data')
def data():
    products = get_data("*", "product", None, None)

    return render_template('data.html', products=products)


@app.route('/tracking')
def tracking():
    # TODO: Add orders to user firebase

    # TODO: maybe - create order function? On checkout?
    # TODO: if doesn't exist - add order collection to user
    # TODO: add order to collection
    # TODO: add items to order

    return render_template('tracking.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/account')
def account():
    return render_template('account.html')


@app.route('/checkout')
def checkout():
    item_location = db.collection(u'users').document(person["uid"]).collection(u'basket').stream()
    items = []
    checkout_price = 0
    for item in item_location:
        items.append(item.to_dict())
        price = item.to_dict()
        checkout_price = checkout_price + price["total_price"]

    return render_template('checkout.html', items=items, checkout_price=checkout_price)


@app.route('/empty')
def empty_cart():
    # TODO: remove all items from basket?
    return


@app.route('/add-to-cart', methods=['POST'])
def add_product_to_cart():
    try:
        quantity = int(request.form['quantity'])
        code = request.form['code']
        # Validate the received values
        if quantity and code and request.method == 'POST':
            row = get_data("*", "product", "code", code)

            # Update new quantity & add total price
            row = {'name': row['name'], 'code': row['code'], 'image': row['image'], 'quantity': quantity,
                   'price': row['price'], 'total_price': quantity * row['price']}

            # Check if item already in basket
            ref = db.collection(u'users').document(person["uid"]).collection(u'basket').document(row["name"]).get()
            if ref.exists:
                # Update quantity & add total price
                ref = ref.to_dict()
                basket_quantity = int(row["quantity"]) + int(ref["quantity"])

                row = {'name': row['name'], 'code': row['code'], 'image': row['image'], 'quantity': basket_quantity,
                       'price': row['price'], 'total_price': basket_quantity * row['price']}

                db.collection(u'users').document(person["uid"]).collection(u'basket').document(row["name"]) \
                    .set(row, merge=True)
            else:
                # Add item
                db.collection(u'users').document(person["uid"]).collection(u'basket').document(row["name"]).set(row)

            return redirect(url_for('data'))
        else:
            return redirect(url_for('error_found'))  # or 'Error while adding item to cart'?
    except Exception as e:
        print(e)


@app.route('/delete')
def delete_product(code):
    # TODO: remove item from basket

    # all_total_price = 0?
    # all_total_quantity = 0?

    return redirect(url_for('data'))


# If someone clicks on login, they are redirected to /login
@app.route("/login", methods=["POST", "GET"])
def login():
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
            login_data = db.collection(u'users').document(person["uid"])
            login_data = login_data.get()
            login_data = login_data.to_dict()
            person["name"] = login_data["name"]
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


# If someone clicks on signup, they are redirected to /signup
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":  # Only listen to POST
        request_result = request.form  # Get the data submitted
        name = request_result["name"]
        email = request_result["email"]
        password = request_result["pass"]
        confirm_password = request_result["confPass"]
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
                signup_data = {"name": name, "email": email}
                db.collection(u'users').document(person["uid"]).set(signup_data)
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


@app.route("/logout", methods=["POST", "GET"])
def logout():
    person["is_logged_in"] = False

    return redirect(url_for('home'))


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
    # conn = open_connection()  # TODO: Make work on cloud?
    app.run()
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)

# @app.route('/add', methods=['POST'])
# def add_item():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400
#     create_data(request.get_json())
#     return 'Item Added'
