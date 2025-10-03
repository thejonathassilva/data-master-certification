from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",           # não erro com chaves desconhecidas
    )

    kafka_bootstrap_servers: str = Field(
        "localhost:9092",
        validation_alias=AliasChoices("KAFKA_BOOTSTRAP_SERVERS", "kafka_bootstrap"),
    )
    kafka_group_id: str = Field(
        "trainer-worker",
        validation_alias=AliasChoices("KAFKA_GROUP_ID", "kafka_group_id"),
    )
    kafka_topic_requests: str = Field(
        "train.requests",
        validation_alias=AliasChoices("KAFKA_TOPIC_REQUESTS", "train_requests_topic"),
    )
    kafka_topic_status: str = Field(
        "train.status",
        validation_alias=AliasChoices("KAFKA_TOPIC_STATUS", "train_status_topic"),
    )
    kafka_security_protocol: str = Field(
        "PLAINTEXT",
        validation_alias=AliasChoices("KAFKA_SECURITY_PROTOCOL", "kafka_security_protocol"),
    )

    mongo_uri: str = Field(
        "mongodb://localhost:27017",
        validation_alias=AliasChoices("MONGO_URI", "mongo_uri"),
    )
    mongo_db: str = Field(
        "nlp",
        validation_alias=AliasChoices("MONGO_DB", "mongo_db"),
    )

    minio_endpoint: str = Field(
        "localhost:9000",
        validation_alias=AliasChoices("MINIO_ENDPOINT", "minio_endpoint"),
    )
    minio_access_key: str = Field(
        "minioadmin",
        validation_alias=AliasChoices("MINIO_ACCESS_KEY", "minio_access_key"),
    )
    minio_secret_key: str = Field(
        "minioadmin",
        validation_alias=AliasChoices("MINIO_SECRET_KEY", "minio_secret_key"),
    )
    minio_secure: bool = Field(
        False,
        validation_alias=AliasChoices("MINIO_SECURE", "minio_secure"),
    )
    minio_bucket: str = Field(
        "nlp-models",
        validation_alias=AliasChoices("MINIO_BUCKET", "models_bucket"),
    )

    random_seed: int = Field(42, validation_alias=AliasChoices("RANDOM_SEED", "random_seed"))
    epochs_textcat: int = Field(15, validation_alias=AliasChoices("EPOCHS_TEXTCAT", "epochs_textcat"))
    epochs_ner: int = Field(20, validation_alias=AliasChoices("EPOCHS_NER", "epochs_ner"))
    batch_size: int = Field(128, validation_alias=AliasChoices("BATCH_SIZE", "batch_size"))
    dev_split: float = Field(0.2, validation_alias=AliasChoices("DEV_SPLIT", "dev_split"))
    early_stop_patience: int = Field(
        3, validation_alias=AliasChoices("EARLY_STOP_PATIENCE", "early_stop_patience")
    )

settings = Settings()
