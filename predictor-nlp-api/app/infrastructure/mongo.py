from pymongo import MongoClient
from pymongo.collection import Collection
from app.core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

def channels_col() -> Collection:
    return db["channels"]

def subjects_col() -> Collection:
    return db["subjects"]

def model_versions_col() -> Collection:
    return db["model_versions"]
