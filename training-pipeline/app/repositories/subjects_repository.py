from typing import Optional, Any, Dict
from bson import ObjectId

def _norm_thresholds(th: Dict[str, Any] | None) -> Dict[str, float] | None:
    if not th: return None
    return {
        "intent_min_conf": th.get("intent_min_conf", th.get("intentMinConf", 0.5)),
        "entity_min_conf": th.get("entity_min_conf", th.get("entityMinConf", 0.5)),
    }

def _normalize_subject(doc: dict) -> dict:
    # channelId (camel) -> mantém como está mas espelha em channel_id por comodidade
    ch = doc.get("channelId", doc.get("channel_id"))
    if ch is not None:
        doc["channelId"] = ch
        doc["channel_id"] = ch
    if "thresholds" in doc:
        doc["thresholds"] = _norm_thresholds(doc["thresholds"])
    return doc

class SubjectsRepository:
    def __init__(self, db):
        self.col = db["subjects"]

    def get_by_id(self, subject_id: str) -> Optional[dict]:
        # tenta ObjectId; se não, string literal
        if ObjectId.is_valid(subject_id):
            doc = self.col.find_one({"_id": ObjectId(subject_id)})
            if doc: return _normalize_subject(doc)
        doc = self.col.find_one({"_id": subject_id})
        if doc: return _normalize_subject(doc)
        return None

    def find_by_channel(self, channel_id_or_hex: str):
        """Retorna subjects cujo channelId (camel) bate com string ou ObjectId hex."""
        # o seu subjects.channelId está salvo como STRING com o hex do ObjectId do canal
        return list(self.col.find({"channelId": str(channel_id_or_hex)}))

    def set_active_version(self, subject_id: str, version: str):
        # atualiza por ObjectId ou string
        if ObjectId.is_valid(subject_id):
            res = self.col.update_one({"_id": ObjectId(subject_id)}, {"$set": {"active_model_version": version}})
            if res.matched_count: return
        self.col.update_one({"_id": subject_id}, {"$set": {"active_model_version": version}})
