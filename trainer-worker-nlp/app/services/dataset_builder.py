import re, logging, os, random
from typing import Dict, List, Tuple
from collections import defaultdict
from pathlib import Path
from app.config import settings

log = logging.getLogger(__name__)

class DatasetBuilder:
    def __init__(self, intents_repo, entities_repo):
        self.intents_repo = intents_repo
        self.entities_repo = entities_repo
        random.seed(settings.random_seed)

    def build_subject_dataset(self, subject_id: str) -> Tuple[List[Dict], List[Dict]]:
        intents = self.intents_repo.list_active_by_subject(subject_id)
        ents_cfg = self.entities_repo.list_by_subject(subject_id)

        examples = []
        counts = defaultdict(int)
        per_intent_samples = defaultdict(list)

        for it in intents:
            intent_name = it["name"]
            for ex in it.get("examples", []):
                entities = self._weak_entities(ex, ents_cfg)  # use sua função real
                rec = {"text": ex, "intent": intent_name, "entities": entities}
                examples.append(rec)
                counts[intent_name] += 1
                if len(per_intent_samples[intent_name]) < 3:
                    per_intent_samples[intent_name].append(rec)

        total = len(examples)
        log.info("[dataset] subject='%s' | total_examples=%d | per_intent=%s",
                subject_id, total, dict(counts))

        for k, v in per_intent_samples.items():
            log.info("[dataset] sample intent=%s | %s", k, [s['text'] for s in v])

        random.shuffle(examples)
        n = int(total * (1 - settings.dev_split))
        return examples[:n], examples[n:]

    def build_channel_dataset(self, all_subjects: List[dict], intents_repo) -> Tuple[List[Dict], List[Dict]]:
        examples = []
        for subj in all_subjects:
            intents = intents_repo.list_active_by_subject(subj["_id"])
            for it in intents:
                for ex in it.get("examples", []):
                    examples.append({"text": ex, "subject": subj["name"]})
        random.shuffle(examples)
        n = int(len(examples) * (1 - settings.dev_split))
        return examples[:n], examples[n:]

    def _weak_entities(self, text: str, ents_cfg: List[dict]) -> List[Tuple[str, int, int]]:
        spans = []
        for ent in ents_cfg:
            label = ent["name"]
            for pat in ent.get("patterns", []) or []:
                for m in re.finditer(pat, text, flags=re.IGNORECASE):
                    s, e = m.span()
                    spans.append((label, s, e))
            for token in ent.get("gazetteer", []) or []:
                for m in re.finditer(re.escape(token), text, flags=re.IGNORECASE):
                    s, e = m.span()
                    spans.append((label, s, e))
        uniq = list({(l, s, e) for (l, s, e) in spans})
        return uniq
