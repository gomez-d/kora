import os

from pymongo import MongoClient

# Create the MongoDB client using the connection URL defined in the environment variables.
client = MongoClient(
    os.getenv('MONGODB_URL'),
    uuidRepresentation='standard'
)

# Get the database defined in the MongoDB connection URL.
database = client.get_database()

# Collections used by the unstructured data service.
# Each collection stores documents with flexible internal structures.
ai_recommendations_collection = database['ai_recommendations']
ml_results_collection = database['ml_results']
logs_collection = database['logs']