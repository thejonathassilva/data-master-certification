from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
import logging
log = logging.getLogger(__name__)

def _maybe_objid(v):
    if v is None: return None
    if isinstance(v, ObjectId): return v
    return ObjectId(v) if ObjectId.is_valid(str(v)) else v

class ModelVersionsRepository:
    def __init__(self, db):
        self.col = db["model_versions"]

    def get_latest_ready(self, scope: str, subject_id: Optional[str], channel: Optional[str]) -> Optional[dict]:
        q = {"scope": scope, "status": "READY"}
        if scope == "subject":
            q["subject_id"] = _maybe_objid(subject_id)
        else:
            q["channel"] = channel
        return self.col.find_one(q, sort=[("created_at", -1)])

    def list_versions(self, scope: str, subject_id: Optional[str], channel: Optional[str]) -> List[dict]:
        q = {"scope": scope}
        if subject_id:
            q["subject_id"] = ObjectId(subject_id)
        if channel:
            q["channel"] = channel
        return list(self.col.find(q))

    def create_status(self, scope: str, subject_id: Optional[str], channel: Optional[str],
                    version: str, status: str, correlation_id: Optional[str],
                    metrics: Optional[Dict[str, Any]] = None,
                    minio_uri: Optional[str] = None) -> dict:
        doc = {
            "scope": scope,
            "subject_id": _maybe_objid(subject_id) if scope == "subject" else None,
            "channel": channel if scope == "channel" else None,
            "version": version,
            "status": status,
            "metrics": metrics,
            "minio_uri": minio_uri,
            "created_at": datetime.utcnow(),
            "correlation_id": correlation_id,
        }
        res = self.col.insert_one(doc)
        if not res.acknowledged:
            log.error("model_versions.insert_one sem ACK | doc=%s", doc)
            raise RuntimeError("Falha ao inserir model_versions (sem ACK)")
        log.info("model_versions criado | _id=%s %s %s v=%s status=%s corr=%s",
                 res.inserted_id, scope, subject_id or channel, version, status, correlation_id)
        return doc

    def set_ready(self, scope: str, subject_id: Optional[str], channel: Optional[str],
                  version: str, metrics: Dict[str, Any], minio_uri: str):
        filt = {
            "scope": scope,
            "subject_id": _maybe_objid(subject_id) if scope == "subject" else None,
            "channel": channel if scope == "channel" else None,
            "version": version
        }
        res = self.col.update_one(filt, {"$set": {"status": "READY", "metrics": metrics, "minio_uri": minio_uri}})
        if res.matched_count == 0:
            cand = list(self.col.find({"scope": scope, "version": version}).sort("created_at", -1))
            log.error("set_ready sem match | filtro=%s | candidatos=%s",
                      filt, [{"id": str(x["_id"]), "subj": x.get("subject_id"), "chan": x.get("channel"),
                              "status": x.get("status")} for x in cand][:5])
            raise RuntimeError("Falha ao marcar READY: versão não encontrada")
        log.info("model_versions READY | filtro=%s mod=%s", filt, res.modified_count)

        
    def set_failed(self, scope: str, subject_id: Optional[str], channel: Optional[str],
                   version: str, message: str):
        self.col.update_one(
            {"scope": scope, "subject_id": ObjectId(subject_id), "channel": channel, "version": version},
            {"$set": {"status": "FAILED", "message": message}}
        )



