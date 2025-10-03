from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel
from app.domain.value_objects import SubjectId, ChannelName, Version

class TrainRequest(BaseModel):
    scope: Literal["subject", "channel", "both"]
    subject_id: Optional[SubjectId] = None
    channel: Optional[ChannelName] = None
    versioning_strategy: Literal["auto", "increment", "fixed"] = "auto"
    base_version: Optional[Version] = None            # e.g. "v3"
    base_lang_model: Optional[str] = None             # e.g. "pt_core_news_md"
    requested_by: str = "console"
    notes: Optional[str] = None
    correlation_id: Optional[str] = None

class TrainStatus(BaseModel):
    subject_id: Optional[SubjectId] = None
    channel: Optional[ChannelName] = None
    scope: Literal["subject", "channel", "both"]
    status: Literal["RUNNING", "SUCCESS", "FAILED"]
    version: Optional[Version] = None
    metrics: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    correlation_id: Optional[str] = None
    ts: int
