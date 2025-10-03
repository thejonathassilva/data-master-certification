import time, logging, numpy as np
from app.services.dataset_builder import DatasetBuilder
from app.utils.preprocess_text import preprocess_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from app.services.minio_storage_service import MinioStorageService
from app.config import settings
from app.observability.metrics import push_training_metrics

log = logging.getLogger(__name__)

class TrainingPipeline:
    def __init__(self, db, model_repo, channels_repo, subjects_repo, intents_repo):
        self.db = db
        self.model_repo = model_repo
        self.channels_repo = channels_repo
        self.subjects_repo = subjects_repo
        self.intents_repo = intents_repo
        self.ds_builder = DatasetBuilder(intents_repo)
        self.storage = MinioStorageService()

    def _resolve_channel(self, subject_id: str) -> str | None:
        try:
            subj = self.subjects_repo.find_by_id(subject_id)
            return subj.get('channel') or subj.get('channelId') or None
        except Exception:
            return None

    def run(self, subject_id: str):
        engine_name = "stick-IA"
        channel = self._resolve_channel(subject_id)

        start = time.time()
        status = 'FAILED'
        accuracy = f1_macro = avg_conf = None
        n_samples = n_features = n_classes = None

        try:
            log.info("Começando execução (engine=%s, subject=%s, channel=%s)", engine_name, subject_id, channel)

            df_intents = self.ds_builder.build_df_intents(subject_id)
            if df_intents.empty:
                raise ValueError(f"Sem exemplos para subject_id={subject_id}")

            df_intents["text"] = df_intents["text"].apply(preprocess_text)

            vectorizer = TfidfVectorizer(
                ngram_range=(settings.ngram_min_range, settings.ngram_max_range),
                max_features=settings.max_features,
                sublinear_tf=True
            )

            X = vectorizer.fit_transform(df_intents["text"])
            y = df_intents["intent"].astype(str)

            n_samples = X.shape[0]
            n_features = X.shape[1]
            n_classes = int(len(np.unique(y)))

            # --- modelo
            clf = RandomForestClassifier(
                n_estimators=settings.n_estimators,
                class_weight=settings.class_weight,
                random_state=settings.random_state,
                n_jobs=settings.n_jobs,
                verbose=settings.verbose
            )
            clf.fit(X, y)

            if hasattr(clf, "predict_proba"):
                probas = clf.predict_proba(X)
                max_conf = probas.max(axis=1)
                avg_conf = float(np.mean(max_conf))
            else:
                avg_conf = None

            try:
                min_per_class = 2
                if n_samples >= max(5, n_classes * min_per_class):
                    cv = StratifiedKFold(n_splits=min(5, n_samples), shuffle=True, random_state=42)
                    accuracy = float(np.mean(cross_val_score(clf, X, y, cv=cv, scoring='accuracy')))
                    f1_macro = float(np.mean(cross_val_score(clf, X, y, cv=cv, scoring='f1_macro')))
            except Exception as e:
                log.warning("Cross-val não executada: %s", e)

            # --- logging por exemplo (como você já fazia)
            if hasattr(clf, "predict_proba"):
                classes = clf.classes_
                for _, row in df_intents.iterrows():
                    vec = vectorizer.transform([row["text"]])
                    p = clf.predict_proba(vec)[0]
                    idx = int(np.argmax(p))
                    pred = classes[idx]
                    conf = float(p[idx])
                    log.info("Esperada: %s | Predita: %s | Conf: %.4f | Texto='%s'",
                             row['intent'], pred, conf, row['text'][:80])

            classifier_url = self.storage.save_object(subject_id, "clf", clf)
            vectorizer_url = self.storage.save_object(subject_id, "vectorizer", vectorizer)

            self.model_repo.save_to_reference_j_assistant(subject_id, "clf", classifier_url)
            self.model_repo.save_to_reference_j_assistant(subject_id, "vectorizer", vectorizer_url)

            status = 'READY'
            log.info("Artefatos publicados (clf=%s, vectorizer=%s)", classifier_url, vectorizer_url)

        except Exception as exc:
            log.exception("Falha no treinamento: %s", exc)
            status = 'FAILED'
        finally:
            duration = time.time() - start
            log.info("Tempo total de treinamento %.3fs", duration)

            push_training_metrics(
                engine=engine_name,
                subject_id=subject_id,
                channel=channel,
                status=status,
                duration_s=duration,
                n_samples=n_samples,
                n_features=n_features,
                n_classes=n_classes,
                accuracy=accuracy,
                f1_macro=f1_macro,
                avg_confidence=avg_conf
            )
