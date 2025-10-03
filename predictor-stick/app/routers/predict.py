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