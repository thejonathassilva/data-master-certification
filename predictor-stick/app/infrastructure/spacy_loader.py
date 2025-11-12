import os
import spacy
from typing import Any
from app.core.config import settings
from app.infrastructure.minio_client import download_and_extract

def load_spacy_from_minio(minio_uri: str) -> Any:
    path = download_and_extract(minio_uri, settings.CACHE_DIR)
    candidates = [os.path.join(path, p) for p in os.listdir(path)]
    selected = path
    for c in candidates:
        if os.path.isdir(c) and os.path.isfile(os.path.join(c, "meta.json")):
            selected = c
            break
    nlp = spacy.load(selected)
    print("PIPES:", nlp.pipe_names)
    print("TEXTCAT LABELS:", getattr(nlp.get_pipe("textcat"), "labels", None) if "textcat" in nlp.pipe_names else None)
    print("NER LABELS:", nlp.get_pipe("ner").labels if "ner" in nlp.pipe_names else None)
    return nlp
