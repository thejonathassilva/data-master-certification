import json
import logging
from app.adapters.kafka_consumer import create_consumer
from app.adapters.kafka_producer import create_producer
from app.adapters.mongo_client import get_mongo, ensure_indexes
from app.repositories.channels_repository import ChannelsRepository
from app.repositories.subjects_repository import SubjectsRepository
from app.repositories.intents_repository import IntentsRepository
from app.repositories.entities_repository import EntitiesRepository
from app.repositories.model_versions_repository import ModelVersionsRepository
from app.services.versioning_service import VersioningService
from app.services.train_subject_usecase import TrainSubjectUseCase
from app.services.train_channel_usecase import TrainChannelUseCase
from app.domain.dtos import TrainRequest, TrainStatus
from app.utils.time_utils import now_ts
from app.constants import (
    SCOPE_BOTH, SCOPE_CHANNEL, SCOPE_SUBJECT,
    STATUS_RUNNING, STATUS_SUCCESS, STATUS_FAILED
)
from app.config import settings

log = logging.getLogger(__name__)

def publish_status(producer, status: TrainStatus):
    producer.send(
        settings.kafka_topic_status,
        key=(status.subject_id or ""),
        value=json.loads(status.model_dump_json())
    )

def handle_request(msg_value: dict):
    db = get_mongo()
    ensure_indexes(db)

    channels_repo  = ChannelsRepository(db)
    subjects_repo  = SubjectsRepository(db)
    intents_repo   = IntentsRepository(db)
    entities_repo  = EntitiesRepository(db)
    models_repo    = ModelVersionsRepository(db)
    versioning     = VersioningService(models_repo)

    producer = create_producer()

    req = TrainRequest(**msg_value)
    status_base = dict(
        subject_id=req.subject_id, channel=req.channel, scope=req.scope,
        correlation_id=req.correlation_id
    )
    publish_status(producer, TrainStatus(**status_base, status=STATUS_RUNNING, ts=now_ts(), message="início do processamento"))

    try:
        subject_version = None
        channel_version = None
        metrics = {}

        if req.scope in (SCOPE_SUBJECT, SCOPE_BOTH):
            if not req.subject_id:
                raise ValueError("subject_id obrigatório para scope != channel")
            subject = subjects_repo.get_by_id(req.subject_id)
            if not subject:
                raise ValueError("subject não encontrado")
            channel_doc = channels_repo.get_by_id_or_name(subject.get("channelId")) or {"name": req.channel or subject.get("channelId")}
            train_subject = TrainSubjectUseCase(db, models_repo, subjects_repo, intents_repo, entities_repo)

            subject_version, m, subject_uri, step_msgs = train_subject.run(
                subject=subject,
                channel_name=channel_doc["name"],
                versioning=versioning,
                strategy=req.versioning_strategy,
                base_version=req.base_version,
                base_lang_model=req.base_lang_model,
                correlation_id=req.correlation_id
            )
            metrics["subject"] = m
            for msg in step_msgs:
                publish_status(producer, TrainStatus(**status_base, status=STATUS_RUNNING, ts=now_ts(), message=f"[subject] {msg}"))

        if req.scope in (SCOPE_CHANNEL, SCOPE_BOTH):
            channel_name = req.channel
            if not channel_name and req.subject_id:
                subj = subjects_repo.get_by_id(req.subject_id)
                channel_name = subj.get("channelId")
            if not channel_name:
                raise ValueError("channel obrigatório para scope == channel")

            train_channel = TrainChannelUseCase(db, models_repo, channels_repo, subjects_repo, intents_repo, entities_repo)
            channel_version, m, channel_uri, step_msgs = train_channel.run(
                channel_name=channel_name,
                versioning=versioning,
                strategy=req.versioning_strategy,
                base_version=req.base_version,
                base_lang_model=req.base_lang_model,
                correlation_id=req.correlation_id
            )
            metrics["channel"] = m
            for msg in step_msgs:
                publish_status(producer, TrainStatus(**status_base, status=STATUS_RUNNING, ts=now_ts(), message=f"[channel] {msg}"))

        version = subject_version or channel_version or None
        publish_status(producer, TrainStatus(**status_base,
                                            status=STATUS_SUCCESS,
                                            version=version,
                                            metrics=metrics,
                                            message="Treino concluído",
                                            ts=now_ts()))
    except Exception as e:
        log.exception("Falha ao processar pedido de treino")
        publish_status(producer, TrainStatus(**status_base,
                                            status=STATUS_FAILED,
                                            version=None,
                                            metrics=None,
                                            message=str(e),
                                            ts=now_ts()))
