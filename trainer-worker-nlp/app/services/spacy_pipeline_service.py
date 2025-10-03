import os
import random
from typing import List, Dict, Tuple, Optional
import spacy
from spacy.training import Example
from app.config import settings

class SpacyPipelineService:
    def __init__(self):
        random.seed(settings.random_seed)

    def load_base(self, base_dir: Optional[str], base_lang_model: Optional[str]):
        if base_dir and os.path.exists(base_dir):
            return spacy.load(base_dir)
        if base_lang_model:
            return spacy.load(base_lang_model)
        return spacy.blank("pt")

    def build_subject_pipeline(self, nlp, intent_labels: List[str], has_ner: bool):
        if "textcat" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat")
            textcat.cfg.setdefault("exclusive_classes", True)
        else:
            textcat = nlp.get_pipe("textcat")
        for lbl in intent_labels:
            if lbl not in textcat.labels:
                textcat.add_label(lbl)

        if has_ner:
            if "ner" not in nlp.pipe_names:
                ner = nlp.add_pipe("ner")
            else:
                ner = nlp.get_pipe("ner")
        return nlp

    def build_channel_pipeline(self, nlp, subject_labels: List[str]):
        if "textcat" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat")
            textcat.cfg.setdefault("exclusive_classes", True)
        else:
            textcat = nlp.get_pipe("textcat")
        for lbl in subject_labels:
            if lbl not in textcat.labels:
                textcat.add_label(lbl)
        return nlp

    def train_subject(self, nlp, train_data: List[Dict], dev_data: List[Dict],
                      epochs_textcat: int, epochs_ner: int, batch_size: int, patience: int):
        train_examples = []
        intent_labels = {ex["intent"] for ex in train_data + dev_data}
        for ex in train_data:
            doc = nlp.make_doc(ex["text"])
            cats = {lbl: 0.0 for lbl in intent_labels}
            cats[ex["intent"]] = 1.0
            ents = [(s, e, l) for (l, s, e) in [(l, s, e) for (l, s, e) in ex.get("entities", [])]]
            example = Example.from_dict(doc, {"cats": cats, "entities": ents})
            train_examples.append(example)

        if not train_examples:
            return nlp, {"intent_f1": 0.0, "ner_f1": 0.0}

        nlp.initialize(lambda: train_examples)
        best_intent_f1 = 0.0
        best_ner_f1 = 0.0
        no_improve = 0

        for epoch in range(max(epochs_textcat, epochs_ner)):
            random.shuffle(train_examples)
            losses = {}
            for i in range(0, len(train_examples), batch_size):
                batch = train_examples[i:i+batch_size]
                nlp.update(batch, losses=losses)
            intent_f1, ner_f1 = self.eval_subject(nlp, dev_data, intent_labels)
            if intent_f1 + ner_f1 > best_intent_f1 + best_ner_f1:
                best_intent_f1, best_ner_f1 = intent_f1, ner_f1
                no_improve = 0
            else:
                no_improve += 1
            if no_improve >= patience:
                break

        return nlp, {"intent_f1": round(best_intent_f1, 4), "ner_f1": round(best_ner_f1, 4)}

    def eval_subject(self, nlp, dev_data: List[Dict], intent_labels):
        from app.services.metrics_service import macro_f1_intents, entity_f1
        y_true, y_pred = [], []
        ner_preds, ner_gold = [], []
        for ex in dev_data:
            doc = nlp(ex["text"])
            if "textcat" in nlp.pipe_names:
                cats = doc.cats
                pred = max(cats, key=cats.get) if cats else None
            else:
                pred = None
            y_true.append(ex["intent"])
            y_pred.append(pred or "")
            ner_preds.extend([(ent.label_, ent.start_char, ent.end_char) for ent in doc.ents])
            ner_gold.extend([(l, s, e) for (l, s, e) in ex.get("entities", [])])

        return macro_f1_intents(y_true, y_pred), entity_f1(ner_preds, ner_gold)

    def train_channel(self, nlp, train_data: List[Dict], dev_data: List[Dict],
                      epochs: int, batch_size: int, patience: int):
        train_examples = []
        labels = {ex["subject"] for ex in train_data + dev_data}
        for ex in train_data:
            doc = nlp.make_doc(ex["text"])
            cats = {lbl: 0.0 for lbl in labels}
            cats[ex["subject"]] = 1.0
            example = Example.from_dict(doc, {"cats": cats})
            train_examples.append(example)

        if not train_examples:
            return nlp, {"subject_f1": 0.0}

        nlp.initialize(lambda: train_examples)

        best_f1 = 0.0
        no_improve = 0
        for epoch in range(epochs):
            random.shuffle(train_examples)
            losses = {}
            for i in range(0, len(train_examples), batch_size):
                batch = train_examples[i:i+batch_size]
                nlp.update(batch, losses=losses)
            y_true, y_pred = [], []
            for ex in dev_data:
                doc = nlp(ex["text"])
                cats = doc.cats
                pred = max(cats, key=cats.get) if cats else ""
                y_true.append(ex["subject"])
                y_pred.append(pred)
            from app.services.metrics_service import macro_f1_intents
            f1 = macro_f1_intents(y_true, y_pred)
            if f1 > best_f1:
                best_f1 = f1
                no_improve = 0
            else:
                no_improve += 1
            if no_improve >= patience:
                break

        return nlp, {"subject_f1": round(best_f1, 4)}
