from typing import Optional, Dict, Any
from app.infrastructure.mongo import model_versions_col
from app.domain.types import Scope
from bson import ObjectId

class ModelVersionsRepository:
    def __init__(self):
        self.col = model_versions_col()

    def get_ready_channel_model(self, channel: str) -> Optional[Dict[str, Any]]:
        # pega a versão READY mais recente (por created_at desc)
        return self.col.find_one(
            {"scope": "channel", "channel": channel, "status": "READY"},
            sort=[("created_at", -1)]
        )

    def get_ready_subject_model_latest(self, subject_id: str):
        q = {"scope":"subject", "subject_id": ObjectId(subject_id), "status":"READY"}
        return self.col.find_one(q, sort=[("created_at", -1)])

    
    def get_ready_subject_model(self, subject_id: str, version: str | None):
        if version:
            q = {"scope":"subject","subject_id": ObjectId(subject_id), "version":version,"status":"READY"}
            return self.col.find_one(q)
        # fallback opcional para “pegar o mais recente READY”
        return self.get_ready_subject_model_latest(subject_id)
