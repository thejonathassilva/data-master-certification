from typing import List, Dict, Any
from bson import ObjectId
import logging
from app.infrastructure.mongo import intents_col

log = logging.getLogger(__name__)

class IntentsRepository:
    def __init__(self):
        self.col = intents_col()

    def find_by_id(self, value: str):
        return self.col.find_one({"_id": ObjectId(value)})
    
    def find_by_name(self, name: str):
        return self.col.find_one({"name": name})
