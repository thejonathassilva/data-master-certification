from typing import Optional
from bson import ObjectId

class ChannelsRepository:
    def __init__(self, db):
        self.col = db["channels"]

    def get_by_id_or_name(self, value: str) -> Optional[dict]:
        # tenta por _id (ObjectId); senão por name (ex.: "PF")
        if ObjectId.is_valid(value):
            doc = self.col.find_one({"_id": ObjectId(value)})
            if doc: return doc
        doc = self.col.find_one({"_id": value})
        if doc: return doc
        return self.col.find_one({"name": value})

