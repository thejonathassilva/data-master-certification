import pytest
from app.services.prediction_service import PredictionService

@pytest.mark.asyncio
async def test_predict_endpoint_smoke(monkeypatch, client):
    # Monkeypatch repos e loaders para não depender de Mongo/MinIO/spaCy reais
    svc = PredictionService()

    monkeypatch.setattr(svc.channels_repo, "get_by_name", lambda name: {"_id": "CH1", "name": name, "min_conf_subject": 0.2})
    monkeypatch.setattr(svc.versions_repo, "get_ready_channel_model", lambda channel: {"version": "1.0.0", "minio_uri": "s3://nlp-models/PF/_channel/1.0.0/model.tar.gz"})
    monkeypatch.setattr(svc.subjects_repo, "get_by_id", lambda sid: {"_id": sid, "thresholds": {"intent_min_conf": 0.3, "entity_min_conf": 0.2}, "active_model_version": "1.2.3"})
    monkeypatch.setattr(svc.versions_repo, "get_ready_subject_model", lambda sid, ver: {"version": ver or "1.2.3", "minio_uri": "s3://nlp-models/PF/ASSUNTO/1.2.3/model.tar.gz"})

    class DummyDoc:
        def __init__(self, cats=None, ents=None):
            self.cats = cats or {}
            self.ents = ents or []

    class DummyNLP:
        def __call__(self, text):
            # canal retorna subjectId numérico como label
            return DummyDoc(cats={"SUBJECT_ID_1": 0.9})

    class DummyNLPSubject:
        def __call__(self, text):
            return DummyDoc(cats={"ASSISTENCIA_24H": 0.83}, ents=[])

    from app.infrastructure.spacy_loader import load_spacy_from_minio as real_loader
    def fake_loader(uri):
        if "/_channel/" in uri:
            return DummyNLP()
        return DummyNLPSubject()
    monkeypatch.setattr("app.services.prediction_service.load_spacy_from_minio", fake_loader)

    # chama via API
    r = await client.post("/predict?channel=PF", json={"text": "quebrou meu carro preciso de guincho 24h"})
    assert r.status_code == 200
    body = r.json()
    assert body["subjectId"] == "SUBJECT_ID_1"
    assert body["intentId"] == "ASSISTENCIA_24H"
    assert 0 <= body["confidence"] <= 1
