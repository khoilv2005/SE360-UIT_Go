import motor.motor_asyncio
from pymongo import MongoClient
import os

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:secret@localhost:27017/uitgo_trips?authSource=admin")
DATABASE_NAME = "uitgo_trips"

# Async MongoDB client for FastAPI
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
trips_collection = database.get_collection("trips")
ratings_collection = database.get_collection("ratings")

# Sync client for setup/migration tasks
sync_client = MongoClient(MONGODB_URL)
sync_database = sync_client[DATABASE_NAME]

def get_database():
    return database
