from fastapi import APIRouter, HTTPException
from app.domain.dtos import PreviewRequest, PreviewResponse
from app.services.preview_service import PreviewService

router = APIRouter(prefix="/preview", tags=["preview"])
service = PreviewService()

@router.post("/intent", response_model=PreviewResponse)
def preview_intent(req: PreviewRequest):
    try:
        print(req)
        data = service.intent_preview(req.subjectId, 
                                      req.intentDraft.name, 
                                      req.intentDraft.examples
                                      )
        print(f"Data preview Request: {data}")
        return PreviewResponse(**data)
    except Exception as e:
        print(f"Erro ao avaliar a manipulação do request {e}")
        raise HTTPException(status_code=500, detail="preview_error")
