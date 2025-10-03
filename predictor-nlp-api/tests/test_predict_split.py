import pytest
from app.domain.dtos import EntityDTO
from app.api.routers import predict as predict_router

@pytest.mark.asyncio
async def test_predict_subject_ok(client, monkeypatch):
    # mock: channel classifier → subject
    monkeypatch.setattr(
        predict_router.service,
        "predict_subject",
        lambda channel_name, text: ("SUBJECT_ID_1", 0.91, False),
    )

    res = await client.post("/predict/subject?channel=PF", json={"text": "quero assistência 24h"})
    assert res.status_code == 200
    body = res.json()
    assert body["subjectId"] == "SUBJECT_ID_1"
    assert 0.0 <= body["confidence"] <= 1.0
    assert body["lowConf"] is False


@pytest.mark.asyncio
async def test_predict_intent_ok(client, monkeypatch):
    # mock: subject pipeline → intent + entities
    def _fake_intent_and_ents(subject_id, text):
        ents = [
            EntityDTO(label="PLACA_VEICULO", value="ABC1D23", start=10, end=17, score=0.78),
        ]
        return "ASSISTENCIA_24H", 0.83, ents

    monkeypatch.setattr(
        predict_router.service,
        "predict_intent_and_entities",
        _fake_intent_and_ents,
    )

    payload = {
        "subjectId": "SUBJECT_ID_1",
        "text": "meu carro quebrou, preciso de guincho para placa ABC1D23"
    }
    res = await client.post("/predict/intent", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["intentId"] == "ASSISTENCIA_24H"
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["entities"], list)
    assert body["entities"][0]["label"] == "PLACA_VEICULO"
    assert body["entities"][0]["value"] == "ABC1D23"
    assert body["entities"][0]["score"] == 0.78


@pytest.mark.asyncio
async def test_predict_subject_low_conf_flag(client, monkeypatch):
    # mock: baixa confiança no subject
    monkeypatch.setattr(
        predict_router.service,
        "predict_subject",
        lambda channel_name, text: ("SUBJECT_ID_1", 0.19, True),
    )

    res = await client.post("/predict/subject?channel=PF", json={"text": "..."})
    assert res.status_code == 200
    body = res.json()
    assert body["subjectId"] == "SUBJECT_ID_1"
    assert body["lowConf"] is True
