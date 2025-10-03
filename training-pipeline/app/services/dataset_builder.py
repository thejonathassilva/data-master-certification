import re, logging, os, random
from typing import Dict, List, Tuple
from collections import defaultdict
from pathlib import Path
from app.config import settings
import pandas as pd

log = logging.getLogger(__name__)

class DatasetBuilder:
    def __init__(self, intents_repo):
        self.intents_repo = intents_repo

    def build_df_intents(self, subject_id: str):
        intents = self.intents_repo.list_active_by_subject(subject_id)
        examples = []

        counts = defaultdict(int)
        per_intent_samples = defaultdict(list)

        for it in intents:
            intent_name = it["name"]
            for ex in it.get("examples", []):
                intent_name = it["name"]
                rec = {"text": ex, "intent": intent_name}
                examples.append(rec)
                counts[intent_name] += 1
                # guarda só alguns exemplos para log
                if len(per_intent_samples[intent_name]) < 3:
                    per_intent_samples[intent_name].append(rec)

        total = len(examples)
        log.info("[dataset] subject='%s' | total_examples=%d | per_intent=%s",
                subject_id, total, dict(counts))

        # LOG amostras (até 3 por intent)
        for k, v in per_intent_samples.items():
            log.info("[dataset] sample intent=%s | %s", k, [s['text'] for s in v])

        df_intents = pd.DataFrame(examples)

        return df_intents
