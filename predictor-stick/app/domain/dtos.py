from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# Requests
class PredictRequest(BaseModel):
    text: str

class IntentDraft(BaseModel):
    name: str
    examples: List[str] = Field(default_factory=list)
    negatives: List[str] | None = None

class PreviewRequest(BaseModel):
    subjectId: str
    intentDraft: IntentDraft

class CacheBustRequest(BaseModel):
    subjectId: Optional[str] = None
    channel: Optional[str] = None

# Responses
class EntityDTO(BaseModel):
    label: str
    value: str
    start: int
    end: int
    score: float

class PredictionResponse(BaseModel):
    subjectId: str
    intentName: Optional[str] 
    confidence: float

class PreviewResponse(BaseModel):
    deltaMetrics: Dict[str, float]
    sampleConfidence: List[Dict[str, Any]]
    topConfusions: List[List[Any]]

class SubjectOnlyResponse(BaseModel):
    subjectId: str | None
    confidence: float | None
    lowConf: bool = False

class IntentOnlyRequest(BaseModel):
    text: str

class IntentOnlyResponse(BaseModel):
    intentId: str | None
    confidence: float | None
    entities: List[EntityDTO] = []
    node: Any | None = None
