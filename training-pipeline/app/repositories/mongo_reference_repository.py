from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

log = logging.getLogger(__name__)

class MongoReferenceRepository:
    def __init__(self, db):
        self.col = db["j_assistant_reference"]

    def save_to_reference_j_assistant(self, subject_id: str, model_type: str, minio_url: str):
        filter_query = {
            "subject_id": subject_id,
            "model_type": model_type
        }

        update_data = {
            "$set": {
                "subject_id": subject_id,
                "model_type": model_type,
                "minio_url": minio_url,
                "updated_at": datetime.utcnow()
            },
            "$setOnInsert": {
                "_id": ObjectId(),
                "created_at": datetime.utcnow()
            }
        }

        self.col.update_one(
            filter_query,
            update_data,
            upsert=True
        )