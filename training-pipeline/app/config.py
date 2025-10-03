from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",           # não erro com chaves desconhecidas
    )

    # Kafka
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

    # Mongo
    mongo_uri: str = Field(
        "mongodb://localhost:27017",
        validation_alias=AliasChoices("MONGO_URI", "mongo_uri"),
    )
    mongo_db: str = Field(
        "nlp",
        validation_alias=AliasChoices("MONGO_DB", "mongo_db"),
    )

    # MinIO
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

    # Treino/Hiperparâmetros
    n_estimators: int = Field('250', validation_alias=AliasChoices("N_ESTIMATORS", "n_estimators"))
    class_weight: str = Field('balanced', validation_alias=AliasChoices("CLASS_WEIGHT", "class_weight"))
    random_state: int = Field('42', validation_alias=AliasChoices("RANDOM_STATE", "random_state"))
    n_jobs: int = Field('1', validation_alias=AliasChoices("N_JOBS", "n_jobs"))
    verbose: int = Field('1', validation_alias=AliasChoices("VERBOSE", "verbose"))
    ngram_min_range: int = Field('1', validation_alias=AliasChoices("NGRAM_MIN_RANGE", "ngram_min_range"))
    ngram_max_range: int = Field('1', validation_alias=AliasChoices("NGRAM_MAX_RANGE", "ngram_max_range"))
    max_features: int = Field('5000', validation_alias=AliasChoices("MAX_FEATURES", "max_features"))

settings = Settings()
