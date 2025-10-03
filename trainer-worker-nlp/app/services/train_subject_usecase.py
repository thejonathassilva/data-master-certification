import time
import logging
import tempfile
from typing import Tuple, Optional, List

from app.constants import MODEL_SCOPE_SUBJECT, TRAINING
from app.services.spacy_pipeline_service import SpacyPipelineService
from app.services.dataset_builder import DatasetBuilder
from app.services.minio_storage_service import MinioStorageService
from app.services.versioning_service import VersioningService
from app.config import settings
from app.observability.metrics import push_training_metrics  # <-- métricas (Pushgateway)

log = logging.getLogger(__name__)


class TrainSubjectUseCase:
    def __init__(self, db, model_repo, subjects_repo, intents_repo, entities_repo):
        self.db = db
        self.model_repo = model_repo
        self.subjects_repo = subjects_repo
        self.intents_repo = intents_repo
        self.entities_repo = entities_repo

        self.pipeline = SpacyPipelineService()
        self.ds_builder = DatasetBuilder(intents_repo, entities_repo)
        self.storage = MinioStorageService()

    def run(
        self,
        subject: dict,
        channel_name: str,
        versioning: VersioningService,
        strategy: str,
        base_version: Optional[str],
        base_lang_model: Optional[str],
        correlation_id: Optional[str],
    ) -> Tuple[str, dict, str, List[str]]:

        steps: List[str] = []
        engine_name = "spacy-IA"
        scope = "subject"
        status = "FAILED"
        version: Optional[str] = None
        start = time.time()

        n_samples: Optional[int] = None
        n_labels: Optional[int] = None
        has_ner_flag: Optional[bool] = None
        accuracy: Optional[float] = None
        f1_macro: Optional[float] = None

        try:
            subject_id = subject["_id"]
            subject_name = subject["name"]

            version = versioning.resolve_target_version(
                strategy, MODEL_SCOPE_SUBJECT, subject_id, None, base_version
            )

            base_dir = None
            if base_version:
                latest = self.model_repo.get_latest_ready(MODEL_SCOPE_SUBJECT, subject_id, None)
                if latest and latest.get("version") == base_version and latest.get("minio_uri"):
                    base_dir = tempfile.mkdtemp(prefix="base_model_")
                    path_in_bucket = latest["minio_uri"].split(f"s3://{self.storage.bucket}/", 1)[1]
                    self.storage.download_to_dir(path_in_bucket, base_dir)
                    steps.append(f"warm-start a partir da {base_version}")

            train, dev = self.ds_builder.build_subject_dataset(subject_id)
            intent_labels = sorted({x["intent"] for x in train + dev})
            has_ner = any(len(x.get("entities", [])) for x in train + dev)
            has_ner_flag = bool(has_ner)

            n_samples = len(train) + len(dev)
            n_labels = len(intent_labels)

            if n_labels < 2:
                raise ValueError("dataset do subject precisa de pelo menos 2 intents distintas")

            nlp = self.pipeline.load_base(base_dir, base_lang_model)
            nlp = self.pipeline.build_subject_pipeline(nlp, intent_labels, has_ner)

            nlp, metrics = self.pipeline.train_subject(
                nlp, train, dev,
                epochs_textcat=settings.epochs_textcat,
                epochs_ner=settings.epochs_ner,
                batch_size=settings.batch_size,
                patience=settings.early_stop_patience
            )

            accuracy = (metrics.get("textcat", {}) or {}).get("accuracy") or metrics.get("accuracy")
            f1_macro = (metrics.get("textcat", {}) or {}).get("f1_macro") or metrics.get("f1_macro")
            if isinstance(accuracy, str):
                try:
                    accuracy = float(accuracy)
                except Exception:
                    accuracy = None
            if isinstance(f1_macro, str):
                try:
                    f1_macro = float(f1_macro)
                except Exception:
                    f1_macro = None

            self.model_repo.create_status(
                MODEL_SCOPE_SUBJECT, subject_id, None, version, TRAINING, correlation_id
            )
            steps.append(f"model_versions criado com status TRAINING (v={version})")

            with tempfile.TemporaryDirectory(prefix="spacy_model_") as tmpdir:
                nlp.to_disk(tmpdir)
                path = self.storage.subject_path(channel_name, subject_name, version)
                uri = self.storage.upload_dir_as_tar_gz(path, tmpdir)
            steps.append(f"modelo publicado no MinIO: {uri}")

            self.model_repo.set_ready(MODEL_SCOPE_SUBJECT, subject_id, None, version, metrics, uri)
            steps.append("model_versions marcado como READY")

            self.subjects_repo.set_active_version(subject_id, version)
            steps.append(f"subjects.active_model_version = {version}")

            status = "READY"
            log.info(
                "Treino de subject concluído (subject=%s, version=%s, uri=%s)",
                subject_name, version, uri
            )
            return version, metrics, uri, steps

        except Exception:
            log.exception("Falha no treinamento do subject '%s'", subject.get("name"))
            raise

        finally:
            duration = time.time() - start
            push_training_metrics(
                engine=engine_name,
                scope=scope,
                channel=channel_name,
                subject_id=str(subject.get("_id")) if subject and subject.get("_id") else None,
                version=version,
                status=status,
                duration_s=duration,
                n_samples=n_samples,
                n_labels=n_labels,
                has_ner=has_ner_flag,
                textcat_epochs=getattr(settings, "epochs_textcat", None),
                ner_epochs=getattr(settings, "epochs_ner", None),
                accuracy=accuracy if isinstance(accuracy, (int, float)) else None,
                f1_macro=f1_macro if isinstance(f1_macro, (int, float)) else None,
            )
