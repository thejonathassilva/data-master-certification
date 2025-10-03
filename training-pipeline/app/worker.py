import json
import logging
from app.adapters.kafka_consumer import create_consumer
from app.adapters.kafka_producer import create_producer
from app.adapters.mongo_client import get_mongo, ensure_indexes
from app.repositories.channels_repository import ChannelsRepository
from app.repositories.subjects_repository import SubjectsRepository
from app.repositories.intents_repository import IntentsRepository
from app.repositories.mongo_reference_repository import MongoReferenceRepository
from app.domain.dtos import TrainRequest, TrainStatus

from app.services.training_pipeline import TrainingPipeline
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
    mongo_reference_repo    = MongoReferenceRepository(db)

    producer = create_producer()

    req = TrainRequest(**msg_value)
    status_base = dict(
        subject_id=req.subject_id, channel=req.channel, scope=req.scope,
        correlation_id=req.correlation_id
    )
    # RUNNING inicial
    publish_status(producer, TrainStatus(**status_base, status=STATUS_RUNNING, ts=now_ts(), message="início do processamento"))

    try:
        metrics = {}

        if req.scope in (SCOPE_SUBJECT, SCOPE_BOTH):
            if not req.subject_id:
                raise ValueError("subject_id obrigatório para scope != channel")
            subject = subjects_repo.get_by_id(req.subject_id)
            if not subject:
                raise ValueError("subject não encontrado")
            train_subject = TrainingPipeline(db, mongo_reference_repo, channels_repo, subjects_repo, intents_repo)

            train_subject.run(req.subject_id)

        publish_status(producer, TrainStatus(**status_base,
                                            status=STATUS_SUCCESS,
                                            metrics=metrics,
                                            message="Treino concluído",
                                            ts=now_ts()))
    except Exception as e:
        log.exception("Falha ao processar pedido de treino")
        publish_status(producer, TrainStatus(**status_base,
                                            status=STATUS_FAILED,
                                            metrics=None,
                                            message=str(e),
                                            ts=now_ts()))
