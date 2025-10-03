from typing import Dict, Any, List, Tuple, Optional
from bson import ObjectId
from app.core.config import settings
from app.infrastructure.cache import model_cache
from app.infrastructure.spacy_loader import load_spacy_from_minio
from app.repositories.channels_repo import ChannelsRepository
from app.repositories.subjects_repo import SubjectsRepository
from app.repositories.model_versions_repo import ModelVersionsRepository
from app.domain.dtos import EntityDTO, PredictionResponse

import logging
log = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.channels_repo = ChannelsRepository()
        self.subjects_repo = SubjectsRepository()
        self.versions_repo = ModelVersionsRepository()

    # --- Model loading helpers (cached) ---
    def _get_channel_model(self, channel: str):
        log.info(f"[channel] lookup model for channel='{channel}' (expect model_versions: scope='channel', channel='{channel}', status='READY')")
        ch_model = self.versions_repo.get_ready_channel_model(channel)
        if not ch_model:
            # Log com pista de configuração esperada
            log.error(
                "[channel] NOT FOUND model for channel='%s'. "
                "Check Mongo.nhlp.model_versions with {scope:'channel', channel:'%s', status:'READY'} "
                "and MinIO path s3://%s/%s/_channel/<version>/model.tar.gz",
                channel, channel, settings.MINIO_DEFAULT_BUCKET, channel
            )
            raise ValueError(f"Channel model not found for {channel}")

        version = ch_model.get("version")
        minio_uri = ch_model.get("minio_uri")
        status = ch_model.get("status")
        log.info(f"[channel] found model_version: version='{version}', status='{status}', minio_uri='{minio_uri}'")

        key = ("channel", channel, version)
        if key in model_cache:
            log.debug(f"[channel] cache HIT key={key}")
            nlp = model_cache[key]
        else:
            log.debug(f"[channel] cache MISS key={key} -> loading from MinIO")
            log.debug(f"[channel] MinIO endpoint='%s' secure=%s bucket(default)='%s'",
                      settings.MINIO_ENDPOINT, settings.MINIO_SECURE, settings.MINIO_DEFAULT_BUCKET)
            nlp = load_spacy_from_minio(minio_uri)
            model_cache[key] = nlp
            log.info("[channel] model loaded and cached: pipes=%s", getattr(nlp, "pipe_names", []))

        # Sanidade: precisa ter algum classificador de assunto (normalmente textcat)
        try:
            labels = []
            if "textcat" in nlp.pipe_names:
                labels = list(nlp.get_pipe("textcat").labels)
            log.info("[channel] spaCy pipes=%s | textcat.labels=%s | n_labels=%d",
                     nlp.pipe_names, labels, len(labels))
        except Exception as e:
            log.warning("[channel] could not inspect labels: %s", e)

        return nlp, ch_model

    def _get_subject_model(self, subject: Dict[str, Any]):
        active_ver = subject.get("active_model_version")
        log.info("[subject] lookup model for subject_id=%s active_model_version=%s", subject.get("_id"), active_ver)
        mv = self.versions_repo.get_ready_subject_model(str(subject["_id"]), active_ver)
        if not mv:
            log.error("[subject] NOT FOUND model for subject_id=%s (need model_versions: scope='subject', subject_id='%s', version='%s', status='READY')",
                      subject.get("_id"), subject.get("_id"), active_ver)
            raise ValueError(f"Subject model not found for subject={subject['_id']}")

        version = mv.get("version")
        minio_uri = mv.get("minio_uri")
        log.info("[subject] found model_version: version='%s', minio_uri='%s'", version, minio_uri)

        key = ("subject", str(subject["_id"]), version)
        if key in model_cache:
            log.debug("[subject] cache HIT key=%s", key)
            nlp = model_cache[key]
        else:
            log.debug("[subject] cache MISS key=%s -> loading from MinIO", key)
            nlp = load_spacy_from_minio(minio_uri)
            model_cache[key] = nlp
            log.info("[subject] model loaded and cached: pipes=%s", getattr(nlp, "pipe_names", []))

        # Inspeciona intents/NER
        try:
            labels = []
            if "textcat" in nlp.pipe_names:
                labels = list(nlp.get_pipe("textcat").labels)
            ner_labels = []
            if "ner" in nlp.pipe_names:
                ner_labels = list(nlp.get_pipe("ner").labels)
            log.info("[subject] spaCy pipes=%s | intents=%s | ner_labels=%s", nlp.pipe_names, labels, ner_labels)
            # 👇 anexa info para o fallback decidir
            nlp._has_intents = bool(labels)
        except Exception as e:
            log.warning("[subject] could not inspect labels: %s", e)
            nlp._has_intents = False

        return nlp, mv

    # --- Prediction flow ---
    def predict(self, channel_name: str, text: str) -> PredictionResponse:
        # 1) resolve channel & thresholds
        log.info("[predict] channel='%s' | text='%s...'", channel_name, text[:80])
        channel = self.channels_repo.get_by_name(channel_name)
        if not channel:
            log.error("[predict] channel not found in Mongo.channels: name='%s'", channel_name)
            raise ValueError(f"Channel not found: {channel_name}")

        min_conf_subject = float(channel.get("min_conf_subject", 0.0))
        log.info("[predict] channel doc _id=%s | min_conf_subject=%.4f", channel.get("_id"), min_conf_subject)

        # 2) channel classifier → best subjectId (by score)
        ch_nlp, ch_model = self._get_channel_model(channel_name)

        labels = []
        try:
            if "textcat" in ch_nlp.pipe_names:
                labels = list(ch_nlp.get_pipe("textcat").labels)
        except Exception as e:
            log.warning("[predict] could not read channel textcat labels: %s", e)

        if not labels:
            # Fallback: escolher subject via pipelines dos subjects
            best_subject_id, best_score, low_conf = self._fallback_select_subject_via_subject_models(channel, text)
            if not best_subject_id:
                raise ValueError(f"No usable subject found for channel={channel_name} (channel model had no labels and no subject model READY)")
        else:
            ch_doc = ch_nlp(text)
            best_subject_id, best_score = self._select_best_subject_from_cats(ch_doc.cats or {})
            low_conf = best_score < min_conf_subject
            if low_conf:
                log.info("[predict] low subject confidence: score %.4f < min_conf_subject %.4f", best_score, min_conf_subject)


        # 3) load subject pipeline (intent + NER)
        subject = self.subjects_repo.get_by_id(best_subject_id)
        if not subject:
            log.warning("[predict] subject doc not found for subject_id='%s' — returning subject only.", best_subject_id)
            return PredictionResponse(
                subjectId=best_subject_id,
                intentId=None,
                confidence=best_score,
                entities=[],
                node=None,
            )

        subj_nlp, subj_model = self._get_subject_model(subject)
        subj_doc = subj_nlp(text)

        # intent via textcat labels
        intent_id, intent_conf = self._select_best_intent_from_cats(subj_doc.cats or {})
        log.info("[predict] intent top1='%s' conf=%.4f", intent_id, intent_conf or 0.0)

        # entities com filtro por limiar
        thresholds = subject.get("thresholds", {}) or {}
        intent_min_conf = float(
            thresholds.get("intent_min_conf", thresholds.get("intentMinConf", 0.0))
        )
        entity_min_conf = float(
            thresholds.get("entity_min_conf", thresholds.get("entityMinConf", 0.0))
        )
        log.info("[predict] subject thresholds: intent_min_conf=%.4f entity_min_conf=%.4f", intent_min_conf, entity_min_conf)

        entities: List[EntityDTO] = []
        if subj_doc.ents:
            for ent in subj_doc.ents:
                score = None
                if hasattr(ent, "_") and hasattr(ent._, "score"):
                    try:
                        score = float(ent._.score)
                    except Exception:
                        score = None
                if score is None:
                    score = 0.0
        log.info("[predict] entities returned: %d", len(entities))

        return PredictionResponse(
            subjectId=str(subject["_id"]),
            intentId=intent_id,
            confidence=float(intent_conf) if intent_conf is not None else 0.0,
            entities=entities,
            node=None
        )

    @staticmethod
    def _select_best_subject_from_cats(cats: Dict[str, float]) -> Tuple[str, float]:
        if not cats:
            return "", 0.0
        best = max(cats.items(), key=lambda kv: kv[1])
        return best[0], float(best[1])

    @staticmethod
    def _select_best_intent_from_cats(cats: Dict[str, float]) -> Tuple[Optional[str], float]:
        if not cats:
            return None, 0.0
        best = max(cats.items(), key=lambda kv: kv[1])
        return best[0], float(best[1])

    def predict_subject(self, channel_name: str, text: str) -> tuple[str | None, float, bool]:
        log.info("[predict_subject] channel='%s' | text='%s...'", channel_name, text[:80])

        channel = self.channels_repo.get_by_name(channel_name)
        if not channel:
            log.error("[predict_subject] channel not found: '%s'", channel_name)
            return None, 0.0, False

        min_conf_subject = float(channel.get("min_conf_subject", 0.0))
        log.info("[predict_subject] channel min_conf_subject=%.4f", min_conf_subject)

        # tenta modelo de canal
        ch_nlp, _ = self._get_channel_model(channel_name)

        # verifica labels
        labels = []
        try:
            if "textcat" in ch_nlp.pipe_names:
                labels = list(ch_nlp.get_pipe("textcat").labels)
        except Exception as e:
            log.warning("[predict_subject] could not read channel textcat labels: %s", e)

        if not labels:
            # Fallback via subject models
            sid, score, low = self._fallback_select_subject_via_subject_models(channel, text)
            if not sid:
                raise ValueError(f"No usable subject found for channel={channel_name} (channel model had no labels and no subject model READY)")
            return sid, score, low

        # fluxo normal com modelo de canal
        ch_doc = ch_nlp(text)
        subject_id, score = self._select_best_subject_from_cats(ch_doc.cats or {})
        low_conf = (score < min_conf_subject) if subject_id else False
        log.info("[predict_subject] subject_id='%s' score=%.4f low_conf=%s", subject_id, score, low_conf)
        return subject_id, float(score), low_conf


    def predict_intent_and_entities(self, subject_name: str, text: str) -> tuple[str | None, float | None, list[EntityDTO]]:
        log.info("[predict_intent_and_entities] subject_name='%s' | text='%s...'", subject_name, text[:80])
        subject = self.subjects_repo.get_by_name(subject_name)
        if not subject:
            log.error("[predict_intent_and_entities] subject not found: '%s'", subject_name)
            return None, None, []
        subj_nlp, subj_model = self._get_subject_model(subject)
        doc = subj_nlp(text)

        intent_id, intent_conf = self._select_best_intent_from_cats(doc.cats or {})
        thresholds = subject.get("thresholds", {}) or {}
        entity_min_conf = float(
            thresholds.get("entity_min_conf", thresholds.get("entityMinConf", 0.0))
        )
        log.info("[predict_intent_and_entities] intent='%s' conf=%.4f entity_min_conf=%.4f", intent_id, intent_conf or 0.0, entity_min_conf)

        entities: list[EntityDTO] = []
        for ent in (doc.ents or []):
            score = None
            if hasattr(ent, "_") and hasattr(ent._, "score"):
                try:
                    score = float(ent._.score)
                except Exception:
                    score = None
            if score is None:
                score = 0.0
            if score >= entity_min_conf:
                entities.append(EntityDTO(
                    label=ent.label_, value=ent.text,
                    start=ent.start_char, end=ent.end_char, score=score
                ))
        log.info("[predict_intent_and_entities] entities=%d", len(entities))
        return intent_id, float(intent_conf) if intent_conf is not None else None, entities
    
    def _fallback_select_subject_via_subject_models(self, channel_doc: dict, text: str) -> tuple[Optional[str], float, bool]:
        """
        Fallback quando o modelo de canal não tem labels:
        - Se houver 1 subject, retorna-o com score=0.0.
        - Se houver N subjects:
            * tenta avaliar via intents (textcat). Quem tiver maior score ganha;
            * se nenhum tiver intents/cats, usa heurística de NER (quem extrair mais entidades do texto);
            * se ainda assim empatar/zerar, escolhe o primeiro por ordem estável.
        """
        channel_id = channel_doc.get("_id")
        log.warning("[fallback] channel textcat has no labels. Falling back to subject models. channel_id=%s", channel_id)

        # lista subjects do canal
        subjects = self.subjects_repo.list_by_channel(channel_id) or []
        log.info("[fallback] subjects found for channel=%s: %d", channel_doc.get("name"), len(subjects))

        if len(subjects) == 0:
            log.error("[fallback] no subjects for channel=%s", channel_doc.get("name"))
            return None, 0.0, False

        # heurística 0: se há somente 1 subject, devolve-o mesmo sem intents
        if len(subjects) == 1:
            only = subjects[0]
            min_conf_subject = float(channel_doc.get("min_conf_subject", 0.0))
            log.warning("[fallback] only one subject in channel; selecting it with score=0.0 (no intents available)")
            return str(only["_id"]), 0.0, (0.0 < min_conf_subject)

        # tenta via intents (textcat)
        best_sid: Optional[str] = None
        best_score: float = -1.0  # começa < 0 para sabermos se alguém pontuou
        any_intents = False

        for s in subjects:
            try:
                subj_nlp, _ = self._get_subject_model(s)
            except Exception as e:
                log.info("[fallback] subject %s has no READY model (%s) - skipping", s.get("_id"), e)
                continue

            if getattr(subj_nlp, "_has_intents", False):
                any_intents = True
                doc = subj_nlp(text)
                cats = doc.cats or {}
                if not cats:
                    log.info("[fallback] subject %s produced empty cats - skipping", s.get("_id"))
                    continue
                intent_id, intent_score = self._select_best_intent_from_cats(cats)
                log.info("[fallback] intents mode: subject %s top-intent=%s score=%.4f", s.get("_id"), intent_id, intent_score or 0.0)

                if intent_score is not None and float(intent_score) > best_score:
                    best_sid = str(s["_id"])
                    best_score = float(intent_score)

        if any_intents and best_sid is not None:
            min_conf_subject = float(channel_doc.get("min_conf_subject", 0.0))
            low_conf = (best_score < min_conf_subject)
            log.info("[fallback] intents result subject_id=%s score=%.4f low_conf=%s", best_sid, best_score, low_conf)
            return best_sid, best_score, low_conf

        # Ninguém com intents utilizáveis → heurística de NER
        log.warning("[fallback] no usable intents in subjects; using NER heuristic")
        best_sid = None
        best_ner_count = -1

        for s in subjects:
            try:
                subj_nlp, _ = self._get_subject_model(s)
            except Exception as e:
                log.info("[fallback][ner] subject %s has no READY model (%s) - skipping", s.get("_id"), e)
                continue

            doc = subj_nlp(text)
            ner_count = len(doc.ents or [])
            log.info("[fallback][ner] subject %s extracted %d entities", s.get("_id"), ner_count)

            if ner_count > best_ner_count:
                best_ner_count = ner_count
                best_sid = str(s["_id"])

        if best_sid is not None:
            # score proxy fraco baseado no NER: clamp a 0.49 para manter low_conf por padrão
            proxy_score = min(0.49, best_ner_count / 5.0) if best_ner_count > 0 else 0.0
            min_conf_subject = float(channel_doc.get("min_conf_subject", 0.0))
            low_conf = (proxy_score < min_conf_subject)
            log.info("[fallback][ner] result subject_id=%s proxy_score=%.4f low_conf=%s", best_sid, proxy_score, low_conf)
            return best_sid, proxy_score, low_conf

        # última linha de defesa: ordem estável
        first = subjects[0]
        min_conf_subject = float(channel_doc.get("min_conf_subject", 0.0))
        log.warning("[fallback] could not decide via intents nor NER; choosing first subject deterministically")
        return str(first["_id"]), 0.0, (0.0 < min_conf_subject)

