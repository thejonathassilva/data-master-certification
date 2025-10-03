from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging
from app.infrastructure.mongo import model_versions_col

log = logging.getLogger(__name__)

class MongoReferenceRepository:
    def __init__(self):
        self.col = model_versions_col()

    def load_j_assistant_reference(self, subject_id: str, model_type: str):
        
        return self.col.find_one({
            "subject_id": str(subject_id),
            "model_type": model_type
        })