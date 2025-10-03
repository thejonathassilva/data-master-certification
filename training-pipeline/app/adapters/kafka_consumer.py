import json
from kafka import KafkaConsumer
from app.config import settings
from app.constants import WORKER_GROUP_ID

def create_consumer():
    return KafkaConsumer(
        settings.kafka_topic_requests,
        bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        group_id=settings.kafka_group_id or WORKER_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        enable_auto_commit=True,
        auto_offset_reset="earliest",
        security_protocol=settings.kafka_security_protocol
    )
