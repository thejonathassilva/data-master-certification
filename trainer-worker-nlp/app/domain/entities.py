from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ModelVersion:
    scope: str           # "subject" | "channel"
    subject_id: Optional[str]
    channel: Optional[str]
    version: str
    minio_uri: Optional[str]
    status: str
    metrics: Optional[Dict[str, Any]]
    created_at: datetime
    correlation_id: Optional[str]
