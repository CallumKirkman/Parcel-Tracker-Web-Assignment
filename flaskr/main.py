import logging

from flask import Flask, render_template, request, jsonify
from flaskr.database import open_connection, get_data, create_data

app = Flask(__name__)


@app.route('/')  # methods=['GET']?
@app.route('/home')
def home():
    data = get_data(conn)
    print(data)
    return render_template('home.html', data=data)


@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/add', methods=['POST'])
# def add_item():
#     if not request.is_json:
#         return jsonify({"msg": "Missing JSON in request"}), 400
#     create_data(conn, request.get_json())
#     return 'Item Added'


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
    conn = open_connection()
    app.run()
    # Only run for local development.
    # app.run(host='127.0.0.1', port=8080, debug=True)
