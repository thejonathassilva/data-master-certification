import time
import logging
import tempfile
from typing import Tuple, Optional, List
from bson import ObjectId

from app.constants import MODEL_SCOPE_CHANNEL, TRAINING
from app.services.spacy_pipeline_service import SpacyPipelineService
from app.services.dataset_builder import DatasetBuilder
from app.services.minio_storage_service import MinioStorageService
from app.services.versioning_service import VersioningService
from app.config import settings
from app.observability.metrics import push_training_metrics
log = logging.getLogger(__name__)


class TrainChannelUseCase:
    def __init__(self, db, model_repo, channels_repo, subjects_repo, intents_repo, entities_repo):
        self.db = db
        self.model_repo = model_repo
        self.channels_repo = channels_repo
        self.subjects_repo = subjects_repo
        self.intents_repo = intents_repo
        self.entities_repo = entities_repo

        self.pipeline = SpacyPipelineService()
        self.ds_builder = DatasetBuilder(intents_repo, entities_repo)
        self.storage = MinioStorageService()

    def run(
        self,
        channel_name: str,
        versioning: VersioningService,
        strategy: str,
        base_version: Optional[str],
        base_lang_model: Optional[str],
        correlation_id: Optional[str],
    ) -> Tuple[str, dict, str, List[str]]:

        steps: List[str] = []
        engine_name = "spacy-IA"
        scope = "channel"
        status = "FAILED"
        version: Optional[str] = None
        start = time.time()

        n_samples: Optional[int] = None
        n_labels: Optional[int] = None
        accuracy: Optional[float] = None
        f1_macro: Optional[float] = None

        channel_name = (channel_name or "").strip().upper()

        try:
            log.info("Iniciando treino de canal (engine=%s, channel=%s)", engine_name, channel_name)

            chan = self.channels_repo.get_by_id_or_name(channel_name)
            if not chan:
                raise ValueError(f"canal não encontrado: {channel_name}")

            chan_oid = chan.get("_id")
            chan_oid_hex = str(chan_oid) if isinstance(chan_oid, ObjectId) else str(chan_oid)

            subjects = self.subjects_repo.find_by_channel(chan_oid_hex)
            if not subjects:
                raise ValueError(f"nenhum subject encontrado para canal {channel_name}")

            train, dev = self.ds_builder.build_channel_dataset(subjects, self.intents_repo)
            labels = sorted({x["subject"] for x in train + dev})

            n_samples = len(train) + len(dev)
            n_labels = len(labels)

            if n_labels < 2:
                raise ValueError("dataset de canal precisa de pelo menos 2 subjects distintos")

            base_dir = None
            if base_version:
                latest = self.model_repo.get_latest_ready(MODEL_SCOPE_CHANNEL, None, channel_name)
                if latest and latest.get("version") == base_version and latest.get("minio_uri"):
                    base_dir = tempfile.mkdtemp(prefix="base_model_")
                    path_in_bucket = latest["minio_uri"].split(f"s3://{self.storage.bucket}/", 1)[1]
                    self.storage.download_to_dir(path_in_bucket, base_dir)
                    steps.append(f"warm-start a partir da {base_version}")

            nlp = self.pipeline.load_base(base_dir, base_lang_model)
            nlp = self.pipeline.build_channel_pipeline(nlp, labels)

            nlp, metrics = self.pipeline.train_channel(
                nlp,
                train,
                dev,
                epochs=settings.epochs_textcat,
                batch_size=settings.batch_size,
                patience=settings.early_stop_patience,
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

            target_version = versioning.resolve_target_version(
                strategy, MODEL_SCOPE_CHANNEL, None, channel_name, base_version
            )
            version = target_version

            self.model_repo.create_status(
                MODEL_SCOPE_CHANNEL, None, channel_name, target_version, TRAINING, correlation_id
            )
            steps.append(f"model_versions (channel) TRAINING v={target_version}")

            with tempfile.TemporaryDirectory(prefix="spacy_model_") as tmpdir:
                nlp.to_disk(tmpdir)
                path = self.storage.channel_path(channel_name, target_version)
                uri = self.storage.upload_dir_as_tar_gz(path, tmpdir)
            steps.append(f"modelo (channel) publicado em {uri}")

            self.model_repo.set_ready(
                MODEL_SCOPE_CHANNEL, None, channel_name, target_version, metrics, uri
            )
            steps.append("model_versions (channel) marcado como READY")

            status = "READY"
            log.info(
                "Treino de canal concluído (channel=%s, version=%s, uri=%s)",
                channel_name, target_version, uri
            )
            return target_version, metrics, uri, steps

        except Exception:
            log.exception("Falha no treinamento do canal '%s'", channel_name)
            raise

        finally:
            duration = time.time() - start
            push_training_metrics(
                engine=engine_name,
                scope=scope,
                channel=channel_name,
                subject_id=None,
                version=version,
                status=status,
                duration_s=duration,
                n_samples=n_samples,
                n_labels=n_labels,
                has_ner=None,  # não aplicável para 'channel'
                textcat_epochs=getattr(settings, "epochs_textcat", None),
                ner_epochs=None,
                accuracy=accuracy if isinstance(accuracy, (int, float)) else None,
                f1_macro=f1_macro if isinstance(f1_macro, (int, float)) else None,
            )
