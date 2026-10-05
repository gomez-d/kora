import os

from pymongo import MongoClient

# Get the MongoDB connection URI from the enviroment.
MONGO_URL = os.getenv("MONGODB_URL")

if not MONGO_URL:
    raise ValueError("MONGODB_URL is not configured")

# Create the MongoDB client using the configured URI.
client = MongoClient(MONGO_URL)

# Get the default database specified in the MongoDB URI.
database = client.get_default_database


def check_connection():
    # Verify that the MongoDB server is reachable
    client.admin.command("ping")
