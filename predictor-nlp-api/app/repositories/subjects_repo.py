from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.infrastructure.mongo import subjects_col

class SubjectsRepository:
    def __init__(self):
        self.col = subjects_col()

    def _normalize_subject(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        if not doc:
            return doc

        if isinstance(doc.get("_id"), ObjectId):
            doc["_id"] = str(doc["_id"])

        if "channel_id" not in doc and "channelId" in doc:
            ch = doc.get("channelId")
            if isinstance(ch, str) and ObjectId.is_valid(ch):
                doc["channel_id"] = ObjectId(ch)
            else:
                doc["channel_id"] = ch  # deixa como veio (string)

        th = doc.get("thresholds") or {}
        if th:
            if "intent_min_conf" not in th and "intentMinConf" in th:
                th["intent_min_conf"] = th["intentMinConf"]
            if "entity_min_conf" not in th and "entityMinConf" in th:
                th["entity_min_conf"] = th["entityMinConf"]
            doc["thresholds"] = th
        return doc

    def get_by_id(self, subject_id: str) -> Optional[Dict[str, Any]]:
        q = {"$or": []}
        if ObjectId.is_valid(subject_id):
            q["$or"].append({"_id": ObjectId(subject_id)})
        q["$or"].append({"_id": subject_id})
        doc = self.col.find_one(q)
        return self._normalize_subject(doc) if doc else None

    def get_by_name(self, subject_name: str) -> Optional[Dict[str, Any]]:
        return self.col.find_one({"name": subject_name})

    def list_by_channel(self, channel_id) -> List[Dict[str, Any]]:
        """
        Aceita:
          - channel_id: ObjectId  -> {channel_id: ObjectId(...)} OU {channelId: "<hex>"}
          - channel_id: str       -> {channel_id: ObjectId(str)} OU {channelId: str}
        """
        ors = []
        if isinstance(channel_id, ObjectId):
            ors.append({"channel_id": channel_id})
            ors.append({"channelId": str(channel_id)})
        elif isinstance(channel_id, str):
            if ObjectId.is_valid(channel_id):
                ors.append({"channel_id": ObjectId(channel_id)})
            ors.append({"channelId": channel_id})
        else:
            ors.append({"channel_id": channel_id})

        cur = self.col.find({"$or": ors})
        return [self._normalize_subject(d) for d in cur]
