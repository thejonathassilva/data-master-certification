from fastapi import APIRouter, HTTPException, Query
from app.domain.dtos import PredictRequest, PredictionResponse, SubjectOnlyResponse, IntentOnlyRequest, IntentOnlyResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["predict"])
service = PredictionService()

@router.post("", response_model=PredictionResponse)
def predict(req: PredictRequest, channel: str = Query(..., alias="channel")):
    try:
        return service.predict(channel, req.text)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="prediction_error")

@router.post("/subject", response_model=SubjectOnlyResponse)
def predict_subject(req: PredictRequest, channel: str = Query(..., alias="channel")):
    try:
        sid, score, low = service.predict_subject(channel, req.text)
        return SubjectOnlyResponse(subjectId=sid, confidence=score, lowConf=low)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="prediction_error")

@router.post("/intent-ner", response_model=IntentOnlyResponse)
def predict_intent(req: IntentOnlyRequest, subject_name: str = Query(..., alias="subjectId")):
    try:
        intent, conf, ents = service.predict_intent_and_entities(subject_name, req.text)
        return IntentOnlyResponse(intentId=intent, confidence=conf, entities=ents, node=None)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="prediction_error")