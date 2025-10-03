from typing import List, Dict, Any
from bson import ObjectId
import logging

log = logging.getLogger(__name__)

class EntitiesRepository:
    def __init__(self, db):
        self.col = db["entities"]

    def _normalize_subject_id(self, subject_id: str) -> Dict[str, Any]:
        """Monta um $or robusto: subjectId/subject_id e string/ObjectId."""
        sid_raw = str(subject_id) if subject_id is not None else ""
        sid = sid_raw.strip()

        conds = []
        conds.append({"subjectId": sid})
        if ObjectId.is_valid(sid):
            conds.append({"subjectId": ObjectId(sid)})

        conds.append({"subject_id": sid})
        if ObjectId.is_valid(sid):
            conds.append({"subject_id": ObjectId(sid)})

        return {"$or": conds}

    def list_by_subject(self, subject_id: str) -> List[dict]:
        subject_match = self._normalize_subject_id(subject_id)

        docs = list(self.col.find(subject_match).sort("name", 1))

        log.info(
            "[entities_repo] subject_id='%s' (sanitized) | encontrados=%d",
            str(subject_id).strip(), len(docs)
        )

        if not docs:
            sample = self.col.find_one({}, {"subjectId":1, "subject_id":1, "name":1})
            log.warning("[entities_repo][diag] Nenhum entity encontrado. Sample doc: %s", sample)

        return docs
