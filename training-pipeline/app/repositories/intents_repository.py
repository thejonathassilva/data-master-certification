from typing import List, Dict, Any
from bson import ObjectId
import logging

log = logging.getLogger(__name__)

class IntentsRepository:
    def __init__(self, db):
        self.col = db["intents"]

    def _normalize_subject_id(self, subject_id: str) -> Dict[str, Any]:
        """Monta um $or robusto: subjectId/subject_id e string/ObjectId."""
        sid_raw = str(subject_id) if subject_id is not None else ""
        sid = sid_raw.strip()  # remove espaços invisíveis / quebras de linha

        conds = []
        # subjectId (string e ObjectId)
        conds.append({"subjectId": sid})
        if ObjectId.is_valid(sid):
            conds.append({"subjectId": ObjectId(sid)})

        # subject_id (string e ObjectId) — para esquemas alternativos
        conds.append({"subject_id": sid})
        if ObjectId.is_valid(sid):
            conds.append({"subject_id": ObjectId(sid)})

        return {"$or": conds}

    def list_active_by_subject(self, subject_id: str) -> List[dict]:
        # filtro robusto de active: considera "sem active" como ativo
        subject_match = self._normalize_subject_id(subject_id)
        q = {
            "$and": [
                subject_match,
                {"$or": [{"active": True}, {"active": {"$exists": False}}]},
            ]
        }

        docs = list(self.col.find(q, {"name": 1, "examples": 1, "active": 1}).sort("name", 1))

        # Logs de diagnóstico
        log.info(
            "[intents_repo] subject_id='%s' (sanitized) | encontrados=%d",
            str(subject_id).strip(), len(docs)
        )
        if not docs:
            # Tenta variantes para diagnosticar onde quebra:
            variants = [
                {"subjectId": str(subject_id).strip(), "active": True},
                {"subjectId": ObjectId(subject_id)} if ObjectId.is_valid(str(subject_id).strip()) else None,
                {"subject_id": str(subject_id).strip(), "active": True},
                {"subject_id": ObjectId(subject_id)} if ObjectId.is_valid(str(subject_id).strip()) else None,
            ]
            for i, v in enumerate([v for v in variants if v]):
                cnt = self.col.count_documents(v)
                log.warning("[intents_repo][diag] variante #%d %s => %d", i+1, v, cnt)

            # E mostra um exemplo bruto da coleção para comparar
            sample = self.col.find_one({}, {"subjectId":1, "subject_id":1, "active":1, "name":1})
            log.warning("[intents_repo][diag] sample doc: %s", sample)

        # normaliza saída
        out: List[Dict[str, Any]] = []
        for d in docs:
            name = d.get("name")
            examples = d.get("examples") or []
            if name and isinstance(examples, list):
                out.append({"name": name, "examples": examples})
        return out

