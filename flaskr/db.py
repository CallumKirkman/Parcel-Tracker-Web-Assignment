from flask_pymongo import pymongo
import os
from dotenv import load_dotenv

# Initialize mongoDB
# When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
if os.environ.get("GAE_ENV") == "standard":
    mongo_username = os.environ.get("MONGO_DB_USERNAME")
    mongo_password = os.environ.get("MONGO_DB_PASSWORD")
    mongo_database = os.environ.get("MONGO_DB_DATABASE_NAME")
else:
    load_dotenv()
    mongo_username = os.getenv("MONGO_DB_USERNAME")
    mongo_password = os.getenv("MONGO_DB_PASSWORD")
    mongo_database = os.getenv("MONGO_DB_DATABASE_NAME")

CONNECTION_STRING = "mongodb+srv://" + mongo_username + ":" + mongo_password + \
                    "@cluster.ktjzqqr.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database(mongo_database)
users = db.users
# users, orders, basket
