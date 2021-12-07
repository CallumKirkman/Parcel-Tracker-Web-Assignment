import logging
import pyrebase

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, abort
from flaskr.database import open_connection, get_data, create_data

import datetime  # TODO: Delete?

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
db = firebase.database()

# Initialise person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}


@app.route('/')
@app.route('/home')
def home():
    # if person["is_logged_in"]:
    #     return render_template("home.html", email=person["email"], name=person["name"])
    # else:
    #     return redirect(url_for('data'))
    db_data = {"name": "Callum", "Age": 22, "Address": "20 St Ives"}
    # db_data = {"name": "aaron"}
    db.child("people").push(db_data)
    print("Successful push!")

    return render_template('home.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/data')  # methods=['GET']?
def data():
    fetched_data = get_data(conn)
    return render_template('data.html', data=fetched_data)


@app.route('/add', methods=['POST'])
def add_item():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    create_data(conn, request.get_json())
    return 'Item Added'


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
            result_data = db.child("users").get()
            person["name"] = result_data.val()[person["uid"]]["name"]
        except:
            # If there is any error, redirect back to login
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
                db.child("users").child(person["uid"]).set(register_data)
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
