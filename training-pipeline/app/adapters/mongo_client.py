from pymongo import MongoClient, ASCENDING
from app.config import settings

_client = None

def get_mongo():
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri)
    return _client[settings.mongo_db]

def ensure_indexes(db):
    db.channels.create_index([("name", ASCENDING)], unique=True)
    db.subjects.create_index([("channelId", ASCENDING)])
    db.intents.create_index([("subject_id", ASCENDING)])
    db.entities.create_index([("subject_id", ASCENDING)])
    db.model_versions.create_index(
        [("scope", ASCENDING), ("subject_id", ASCENDING), ("channel", ASCENDING),
         ("version", ASCENDING), ("status", ASCENDING)]
    )
