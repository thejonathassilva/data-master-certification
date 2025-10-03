from typing import Dict, Any, List, Tuple
import hashlib, json, logging
import spacy
from spacy.training import Example
from spacy.util import fix_random_seed
from app.repositories.subjects_repo import SubjectsRepository
from app.repositories.model_versions_repo import ModelVersionsRepository
from app.infrastructure.cache import model_cache
from app.infrastructure.spacy_loader import load_spacy_from_minio
from app.core.config import settings

log = logging.getLogger(__name__)
_preview_cache: dict[str, Dict[str, Any]] = {}


class PreviewService:
    def __init__(self):
        self.subjects_repo = SubjectsRepository()
        self.versions_repo = ModelVersionsRepository()

    # ---------- Infra ----------
    def _load_subject_model(self, subject_id: str):
        subject = self.subjects_repo.get_by_id(subject_id)
        if not subject:
            return None, None, None
        mv = self.versions_repo.get_ready_subject_model(
            str(subject["_id"]), subject.get("active_model_version")
        )
        nlp = None
        if mv:
            key = ("subject", str(subject["_id"]), mv["version"])
            nlp = model_cache.get(key) or load_spacy_from_minio(mv["minio_uri"])
            model_cache[key] = nlp
        return subject, mv, nlp

    def _fresh_textcat_multilabel(self, lang: str, labels: List[str]):
        nlp = spacy.blank(lang or "pt")
        tc = nlp.add_pipe("textcat_multilabel")
        for lb in sorted(set(labels)):  # ordem fixa
            if lb not in tc.labels:
                tc.add_label(lb)
        return nlp, tc

    # ---------- Negativos automáticos (determinísticos) ----------
    def _auto_negatives(self, intent_name: str, base_nlp, k_target: int) -> List[str]:
        templates = (
            "quero {x}", "preciso de {x}", "falar sobre {x}",
            "informações sobre {x}", "como faço para {x}", "desejo {x}",
        )
        generic_pool = (
            "bom dia", "quero falar com atendente", "qual o horário de atendimento",
            "como alterar endereço", "informações da fatura", "não entendi",
            "quero atualizar meus dados", "pagar boleto", "qual o prazo", "olá",
            "qual o limite do cartão", "quero cancelar assinatura",
            "preciso de segunda via do boleto", "minha entrega atrasou",
        )
        out: List[str] = []
        other = []
        if base_nlp is not None and "textcat" in base_nlp.pipe_names:
            try:
                other = [lb for lb in base_nlp.get_pipe("textcat").labels if lb != intent_name]
            except Exception:
                other = []
        for lb in sorted(other):
            tok = lb.replace("_", " ").lower()
            for t in templates:
                out.append(t.format(x=tok))
                if len(out) >= k_target:
                    return out[:k_target]
        for g in generic_pool:
            out.append(g)
            if len(out) >= k_target:
                break
        return out[:k_target]

    # ---------- Métricas ----------
    @staticmethod
    def _f1_at_threshold(y_true: List[int], y_score: List[float], thr: float = 0.5) -> float:
        y_pred = [1 if s >= thr else 0 for s in y_score]
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)
        denom = (2 * tp + fp + fn)
        return 0.0 if denom == 0 else (2 * tp) / denom

    @staticmethod
    def _cats_of(nlp: "spacy.Language", label: str, texts: List[str]) -> List[float]:
        return [float(d.cats.get(label, 0.0)) for d in nlp.pipe(texts)]

    @staticmethod
    def _estimate_confusions(nlp, texts: List[str]) -> List[List[Any]]:
        counts = {}
        for t in texts:
            doc = nlp(t)
            cats = sorted(doc.cats.items(), key=lambda kv: kv[1], reverse=True)[:2]
            if len(cats) == 2:
                a, b = cats[0][0], cats[1][0]
                key = tuple(sorted([a, b]))
                counts[key] = counts.get(key, 0) + 1
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
        return [[k[0], k[1], v] for (k, v) in top]

    # ---------- Split estratificado determinístico ----------
    def _stratified_split(self, pos_ex: List[Example], neg_ex: List[Example], val_ratio: float = 0.2):
        pos = sorted(pos_ex, key=lambda e: e.reference.text)
        neg = sorted(neg_ex, key=lambda e: e.reference.text)
        k_pos = max(1 if len(pos) > 0 else 0, int(round(val_ratio * len(pos))))
        k_neg = int(round(val_ratio * len(neg)))
        val = pos[:k_pos] + neg[:k_neg]
        train = pos[k_pos:] + neg[k_neg:]
        return train, val

    # ---------- Train loop (épocas/batch/early-stopping) ----------
    def _train_textcat(
        self,
        nlp_shadow: "spacy.Language",
        textcat,
        train_examples: List[Example],
        val_examples: List[Example],
        label: str,
        seed: int,
        epochs: int,
        batch_size: int,
        patience: int,
        thr: float,
    ):
        fix_random_seed(seed)
        try:
            textcat.initialize(lambda: train_examples, nlp=nlp_shadow)
        except Exception:
            pass

        best_f1 = -1.0
        best_bytes = None
        bad = 0

        def iter_batches(exs, bs):
            for i in range(0, len(exs), bs):
                yield exs[i:i+bs]

        for ep in range(1, max(1, epochs) + 1):
            for batch in iter_batches(train_examples, max(1, batch_size)):
                nlp_shadow.update(batch, drop=0.0)  # determinístico

            # eval no hold-out
            val_texts = [ex.reference.text for ex in val_examples]
            y_true = [int(ex.reference.cats.get(label, 0.0) >= thr) for ex in val_examples]
            y_score = self._cats_of(nlp_shadow, label, val_texts)
            f1 = self._f1_at_threshold(y_true, y_score, thr=thr)

            if f1 > best_f1 + 1e-9:
                best_f1 = f1
                best_bytes = textcat.to_bytes()
                bad = 0
            else:
                bad += 1
                if bad >= max(1, patience):
                    break

        if best_bytes is not None:
            textcat.from_bytes(best_bytes)
        return best_f1

    # ---------- Prévia ----------
    def intent_preview(self, subject_id: str, intent_name: str, examples: List[str]) -> Dict[str, Any]:
        if settings.PREVIEW_FORCE_CPU:
            spacy.require_cpu()
        fix_random_seed(settings.RANDOM_SEED)

        # cache por conteúdo
        key = hashlib.sha1(
            json.dumps(
                {"sid": subject_id, "intent": intent_name, "pos": sorted(examples)},
                ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        if key in _preview_cache:
            return _preview_cache[key]

        subject, mv, base_nlp = self._load_subject_model(subject_id)
        if base_nlp is None:
            base_nlp = spacy.blank("pt")

        THR = 0.5
        pos_texts = sorted(list(examples))

        # BEFORE
        before_scores = self._cats_of(base_nlp, intent_name, pos_texts)
        before_y_true = [1] * len(pos_texts)
        before_f1 = self._f1_at_threshold(before_y_true, before_scores, thr=THR)

        # Negativos automáticos
        neg_target = max(max(3, len(pos_texts)), min(2 * len(pos_texts), 50))
        neg_texts = self._auto_negatives(intent_name, base_nlp, neg_target)

        # Shadow + labels
        nlp_shadow, tc = self._fresh_textcat_multilabel(base_nlp.lang, [intent_name])

        # Examples
        def ex(txt: str, y: float):
            return Example.from_dict(nlp_shadow.make_doc(txt), {"cats": {intent_name: float(y)}})
        pos_examples = [ex(t, 1.0) for t in pos_texts]
        neg_examples = [ex(t, 0.0) for t in neg_texts]

        # Split 80/20 estratificado
        train_examples, val_examples = self._stratified_split(pos_examples, neg_examples, val_ratio=0.2)

        # Train (épocas/batch/early-stop)
        after_f1 = self._train_textcat(
            nlp_shadow, tc, train_examples, val_examples,
            label=intent_name,
            seed=settings.RANDOM_SEED,
            epochs=settings.EPOCHS_TEXTCAT,
            batch_size=settings.BATCH_SIZE,
            patience=settings.EARLY_STOP_PATIENCE,
            thr=THR,
        )

        # Confianças para AS SUAS FRASES (o que você quer ver no preview)
        draft_scores = self._cats_of(nlp_shadow, intent_name, pos_texts)
        sample_conf = [{"text": t, "confidence": float(s)} for t, s in zip(pos_texts, draft_scores)]

        # (interno) métricas auxiliares para validação
        val_texts = [ex.reference.text for ex in val_examples]
        y_true = [int(ex.reference.cats.get(intent_name, 0.0) >= THR) for ex in val_examples]
        y_score = self._cats_of(nlp_shadow, intent_name, val_texts)
        y_pred = [1 if s >= THR else 0 for s in y_score]
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
        fpr = (fp / (fp + tn)) if (fp + tn) else 0.0
        neg_scores = [s for s, yt in zip(y_score, y_true) if yt == 0]
        neg_max_conf = max(neg_scores) if neg_scores else 0.0
        pos_avg = sum(d["confidence"] for d in sample_conf) / len(sample_conf) if sample_conf else 0.0
        pos_min = min(d["confidence"] for d in sample_conf) if sample_conf else 0.0

        lift = after_f1 - before_f1
        top_confusions = self._estimate_confusions(base_nlp, pos_texts)

        # validação (critérios em .env)
        reasons: list[str] = []
        passed = True
        if after_f1 < settings.PREVIEW_MIN_F1:
            passed = False; reasons.append(f"F1_after {after_f1:.2f} < min {settings.PREVIEW_MIN_F1:.2f}")
        if lift < settings.PREVIEW_MIN_LIFT:
            passed = False; reasons.append(f"lift {lift:.2f} < min {settings.PREVIEW_MIN_LIFT:.2f}")
        if pos_avg < settings.PREVIEW_MIN_POS_CONF:
            passed = False; reasons.append(f"avg_pos_conf {pos_avg:.2f} < min {settings.PREVIEW_MIN_POS_CONF:.2f}")
        if neg_max_conf > settings.PREVIEW_MAX_NEG_CONF:
            passed = False; reasons.append(f"max_neg_conf {neg_max_conf:.2f} > max {settings.PREVIEW_MAX_NEG_CONF:.2f}")
        if fpr > settings.PREVIEW_MAX_FPR:
            passed = False; reasons.append(f"FPR {fpr:.2f} > max {settings.PREVIEW_MAX_FPR:.2f}")

        validation = {
            "passed": passed,
            "reasons": reasons,
            "stats": {
                "pos_avg_conf": round(pos_avg, 4),
                "pos_min_conf": round(pos_min, 4),
                "neg_max_conf": round(neg_max_conf, 4),
                "fpr": round(fpr, 4)
            }
        }

        resp = {
            "deltaMetrics": {
                "intent_f1_before": round(float(before_f1), 4),
                "intent_f1_after": round(float(after_f1), 4),
                "lift": round(float(lift), 4),
                "threshold_used": THR,
                "seed": settings.RANDOM_SEED,
                "epochs_textcat": settings.EPOCHS_TEXTCAT,
                "batch_size": settings.BATCH_SIZE,
                "early_stop_patience": settings.EARLY_STOP_PATIENCE,
            },
            # 👇 agora o preview mostra exatamente as frases do payload
            "sampleConfidence": sample_conf,
            "topConfusions": top_confusions,
            "validation": validation
        }
        _preview_cache[key] = resp
        return resp
