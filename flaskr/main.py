import logging
import pyrebase
import pymysql
import bcrypt

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session

import firebase_admin
from firebase_admin import credentials, firestore

from flask import Flask, render_template, request, url_for, redirect, session
import bcrypt

import db

app = Flask(__name__)
app.secret_key = "testing"
users = db.users


# # Product SQL get data
# def get_data(item, table, column, column_id):
#     cnx = open_cloudsql_connection()
#
#     with cnx.cursor() as cursor:
#         if column is None:
#             # Get everything
#             fetched_items = cursor.execute('select %s from %s;' % (item, table))
#             items = cursor.fetchall()
#         else:
#             # Get specific entry
#             fetched_items = cursor.execute("select * from %s where %s='%s';" % (table, column, column_id))
#             items = cursor.fetchone()
#     if fetched_items > 0:
#         return items
#     else:
#         got_items = 'No items in DB'
#         return got_items


# # Product SQL create data
# def create_data(table, item_id, item_name, item):
#     cnx = open_cloudsql_connection()
#     with cnx.cursor() as cursor:
#         cursor.execute('INSERT INTO %s (%s, %s) VALUES(%s, %s)' % (table, item_id, item_name, item["4"], item["test"]))
#     cnx.commit()
#     cnx.close()


# # Initialise person as dictionary
# person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "address": "", "picture": "", "admin": False}
# idToken = ""


# @app.context_processor
# def inject_status():
#     return dict(logg_status=person["is_logged_in"], name=person["name"], email=person["email"], uid=person["uid"],
#                 address=person["address"], picture=person["picture"], admin=person["admin"])


@app.route('/')
def home():
    return render_template("home.html")


# # If someone clicks on signup, they are redirected to /signup
# @app.route("/signup", methods=["POST", "GET"])
# def signup():
#     if request.method == "POST":  # Only listen to POST
#         request_result = request.form  # Get the data submitted
#         name = request_result["name"]
#         email = request_result["email"]
#         password = request_result["pass"]
#         confirm_password = request_result["confPass"]
#         if password == confirm_password:
#             try:
#                 # Try creating the user account using the provided data
#                 auth.create_user_with_email_and_password(email, password)
#                 # Login the user
#                 user = auth.sign_in_with_email_and_password(email, password)
#
#                 global idToken
#                 idToken = user["idToken"]
#
#                 # Add data to global person
#                 global person
#                 person["is_logged_in"] = True
#                 person["name"] = name
#                 person["email"] = user["email"]
#                 person["uid"] = user["localId"]
#                 person["address"] = "Add address"
#                 person["picture"] = "/static/assets/user.png"
#                 person["admin"] = False
#
#                 # Append data to the firebase realtime database
#                 signup_data = {"name": name, "email": email, "address": person["address"], "picture": person["picture"],
#                                "admin": person["admin"]}
#                 firestoreDB.collection(u'users').document(person["uid"]).set(signup_data)
#             except:
#                 # If there is any error, redirect to error
#                 return redirect(url_for('error_found'))
#             else:
#                 # To home page
#                 return redirect(url_for('home'))
#     else:
#         if person["is_logged_in"]:
#             return redirect(url_for('home'))
#         else:
#             return redirect(url_for('error_found'))
@app.route("/signup", methods=["post", "get"])
def signup():
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = users.find_one({"name": user})
        email_found = users.find_one({"email": email})
        if user_found:
            message = "There already is a user by that name"
            return render_template("signup.html", message=message)
        if email_found:
            message = "This email already exists in database"
            return render_template("signup.html", message=message)
        if password1 != password2:
            message = "Passwords should match!"
            return render_template("signup.html", message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode("utf-8"), bcrypt.gensalt())
            user_input = {"name": user, "email": email, "password": hashed}
            users.insert_one(user_input)

            user_data = users.find_one({"email": email})
            new_name = user_data["name"]
            new_email = user_data["email"]

            return render_template("logged_in.html", name=new_name, email=new_email)
    return render_template("signup.html")


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        name = session["name"]
        email = session["email"]
        return render_template('logged_in.html', name=name, email=email)
    else:
        return redirect(url_for("login"))


# # If someone clicks on login, they are redirected to /login
# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":  # Only if data has been posted
#         request_result = request.form  # Get the data
#         email = request_result["email"]
#         password = request_result["pass"]
#         try:
#             # Try signing in the user with the given information
#             user = auth.sign_in_with_email_and_password(email, password)
#
#             global idToken
#             idToken = user["idToken"]
#
#             # Add data to global person
#             global person
#             person["is_logged_in"] = True
#             person["email"] = user["email"]
#             person["uid"] = user["localId"]
#
#             # Get the data of the user
#             login_data = firestoreDB.collection(u'users').document(person["uid"]).get()
#             login_data = login_data.to_dict()
#             # "name": name, "email": email, "address": address, "picture": picture, "admin": admin
#
#             person["name"] = login_data["name"]
#             person["address"] = login_data["address"]
#             person["picture"] = login_data["picture"]
#             person["admin"] = login_data["admin"]
#
#         except:
#             # If there is any error, redirect to error
#             return redirect(url_for('error_found'))
#         else:
#             # To home page
#             return redirect(url_for('home'))
#     else:
#         if person["is_logged_in"]:
#             return redirect(url_for('home'))
#         else:
#             return redirect(url_for('error_found'))
@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_found = users.find_one({"email": email})
        if user_found:
            name_val = user_found['name']
            email_val = user_found['email']
            password_check = user_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), password_check):
                session["name"] = name_val
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


# @app.route('/logout')
# def logout():
#     # Reset global variables
#     global idToken
#     idToken = ""
#
#     global person
#     person = {"is_logged_in": False, "name": "", "email": "", "uid": "", "address": "", "picture": "", "admin": False}
#
#     return redirect(url_for('home'))
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("sign_out.html")
    else:
        return render_template('signup.html')


@app.route('/product')
def product():
    # products = get_data("*", "product", None, None)

    return render_template('product0.html')  # , products=products


@app.route('/tracking')
def tracking():
    # order_collection = open_mongodb_connection()
    #
    # if person["admin"]:
    #     order_find = order_collection.find()
    # else:
    #     order_find = order_collection.find({"order.uid": person["uid"]})
    #
    # orders = []
    # for order in order_find:
    #     orders.append(order)
    #
    # if len(orders) == 0:
    #     orders = "No current orders"

    return render_template('tracking0.html')  # , orders=orders


@app.route('/about')
def about():
    return render_template('about0.html')


@app.route('/account')
def account():
    # # Get the data of the active user
    # account_data = firestoreDB.collection(u'users').document(person["uid"]).get()
    # account_data = account_data.to_dict()
    # # "name": name, "email": email, "address": address, "picture": picture, "admin": admin

    # # Update the data of the active user
    # person["name"] = account_data["name"]
    # person["email"] = account_data["email"]
    # person["address"] = account_data["address"]
    # person["picture"] = account_data["picture"]

    return render_template('account0.html')


@app.route('/checkout')
def checkout():
    # item_location = firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').stream()
    # items = []
    # checkout_price = 0
    # for item in item_location:
    #     items.append(item.to_dict())
    #     price = item.to_dict()
    #     checkout_price = checkout_price + price["total_price"]

    # if len(items) == 0:
    #     items = "No items in cart"

    return render_template('checkout0.html')  # , items=items, checkout_price=checkout_price


@app.route('/create-order')
def create_order():
    # order_collection = open_mongodb_connection()
    #
    # item_location = firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').stream()
    # date = datetime.today().strftime('%d-%m-%y')
    # items = []
    # checkout_price = 0
    # for item in item_location:
    #     items.append(item.to_dict())
    #     price = item.to_dict()
    #     checkout_price = checkout_price + price["total_price"]
    #     item.reference.delete()
    #
    # order = {"uid": person["uid"], "items": items, "orderPrice": checkout_price, "date": date,
    #          "progress": "processing"}
    #
    # order_collection.insert_one({"order": order})

    return redirect(url_for('tracking'))


@app.route('/empty')
def empty_cart():
    # item_location = firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').stream()
    # for item in item_location:
    #     item.reference.delete()

    return redirect(url_for('product'))


# @app.route('/delete-account')
# def delete_account():
#     # Delete user information
#     firestoreDB.collection(u'users').document(person["uid"]).delete()
#
#     # Delete user account
#     auth.delete_user_account(idToken)
#
#     return redirect(url_for('logout'))
#
#
# @app.route('/update-account', methods=["POST", "GET"])
# def update_account():
#     if request.method == "POST":  # Only if data has been posted
#         request_result = request.form  # Get the data
#         name = request_result["name"]
#         email = request_result["email"]
#         address = request_result["address"]
#         picture = request_result["picture"]
#
#         if name == "":
#             name = person["name"]
#         if email == "":
#             email = person["email"]
#         if address == "":
#             address = person["address"]
#         if picture == "":
#             picture = person["picture"]
#
#         user_info = {"name": name, "email": email, "address": address, "picture": picture}
#
#         firestoreDB.collection(u'users').document(person["uid"]).set(user_info, merge=True)
#
#         return redirect(url_for('home'))
#
#     else:
#         return redirect(url_for('error_found'))
#
#
# @app.route('/add-to-cart', methods=['POST'])
# def add_product_to_cart():
#     try:
#         quantity = int(request.form['quantity'])
#         code = request.form['code']
#         # Validate the received values
#         if quantity and code and request.method == 'POST':
#             row = get_data("*", "product", "code", code)
#
#             # Update new quantity & add total price
#             row = {'name': row['name'], 'code': row['code'], 'image': row['image'], 'quantity': quantity,
#                    'price': row['price'], 'total_price': quantity * row['price']}
#
#             # Check if item already in basket
#             ref = firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').document(
#                 row["name"]).get()
#             if ref.exists:
#                 # Update quantity & add total price
#                 ref = ref.to_dict()
#                 basket_quantity = int(row["quantity"]) + int(ref["quantity"])
#
#                 row = {'name': row['name'], 'code': row['code'], 'image': row['image'], 'quantity': basket_quantity,
#                        'price': row['price'], 'total_price': basket_quantity * row['price']}
#
#                 firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').document(row["name"]) \
#                     .set(row, merge=True)
#             else:
#                 # Add item
#                 firestoreDB.collection(u'users').document(person["uid"]).collection(u'basket').document(
#                     row["name"]).set(row)
#
#             return redirect(url_for('product'))
#         else:
#             return redirect(url_for('error_found'))
#     except Exception as e:
#         print(e)
#
#


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
    app.run()
