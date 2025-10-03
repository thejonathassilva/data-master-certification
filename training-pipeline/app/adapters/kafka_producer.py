import json
from kafka import KafkaProducer
from app.config import settings

def create_producer():
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
        security_protocol=settings.kafka_security_protocol
    )
