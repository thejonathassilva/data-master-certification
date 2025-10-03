from __future__ import annotations
import re
from typing import Any
from typing_extensions import Annotated
from pydantic import AfterValidator, PlainSerializer

# --- validators & normalizers ---

_VERSION_RE = re.compile(r"^v\d+$", re.IGNORECASE)

def _ensure_non_empty_str(v: Any) -> str:
    if v is None:
        raise ValueError("valor ausente")
    if not isinstance(v, str):
        raise TypeError("deve ser string")
    v2 = v.strip()
    if not v2:
        raise ValueError("string vazia")
    return v2

def _validate_subject_id(v: Any) -> str:
    # Mantém simples (string não vazia). Se quiser, valide ObjectId:
    # from bson import ObjectId; assert ObjectId.is_valid(v2)
    return _ensure_non_empty_str(v)

def _normalize_channel_name(v: Any) -> str:
    v2 = _ensure_non_empty_str(v)
    return v2.upper()

def _validate_version(v: Any) -> str:
    v2 = _ensure_non_empty_str(v)
    if not _VERSION_RE.match(v2):
        raise ValueError("versão deve seguir o padrão vN (ex.: v3)")
    # normaliza para minúsculo no prefixo
    return f"v{int(v2[1:])}"

def _validate_confidence(v: Any) -> float:
    if isinstance(v, (int, float)):
        val = float(v)
    else:
        try:
            val = float(str(v))
        except Exception as e:
            raise TypeError("confidence deve ser numérico") from e
    if not (0.0 <= val <= 1.0):
        raise ValueError("confidence deve estar entre 0.0 e 1.0")
    return val

# --- public VO types (Annotated) ---

SubjectId = Annotated[str,
    AfterValidator(_validate_subject_id),
    PlainSerializer(lambda v, _: v, return_type=str)
]

ChannelName = Annotated[str,
    AfterValidator(_normalize_channel_name),
    PlainSerializer(lambda v, _: v, return_type=str)
]

Version = Annotated[str,
    AfterValidator(_validate_version),
    PlainSerializer(lambda v, _: v, return_type=str)
]

Confidence = Annotated[float,
    AfterValidator(_validate_confidence),
    PlainSerializer(lambda v, _: v, return_type=float)
]
