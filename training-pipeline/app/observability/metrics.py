import os
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://pushgateway:9091")

def push_training_metrics(
    *,
    engine: str,
    subject_id: str,
    channel: str | None,
    status: str,
    duration_s: float | None = None,
    n_samples: int | None = None,
    n_features: int | None = None,
    n_classes: int | None = None,
    accuracy: float | None = None,
    f1_macro: float | None = None,
    avg_confidence: float | None = None,
):
    """
    Empurra um conjunto de métricas para o Prometheus Pushgateway.

    - engine: 'stick-IA' | 'spacy-IA' | etc
    - subject_id: id do assunto treinado
    - channel: canal (PF/PJ) se você tiver (opcional)
    - status: 'READY' em sucesso, 'FAILED' em falha
    """

    registry = CollectorRegistry()

    g_status       = Gauge('trainer_status', '1=READY, 0=FAILED', ['engine','subject_id','channel'], registry=registry)
    g_duration     = Gauge('trainer_duration_seconds', 'Duração total do treinamento', ['engine','subject_id','channel'], registry=registry)
    g_samples      = Gauge('trainer_samples_total', 'Total de amostras utilizadas', ['engine','subject_id','channel'], registry=registry)
    g_features     = Gauge('trainer_features_total', 'Total de features após vetorização', ['engine','subject_id','channel'], registry=registry)
    g_classes      = Gauge('trainer_classes_total', 'Total de classes (intents)', ['engine','subject_id','channel'], registry=registry)
    g_accuracy     = Gauge('trainer_accuracy', 'Acurácia (validação)', ['engine','subject_id','channel'], registry=registry)
    g_f1_macro     = Gauge('trainer_f1_macro', 'F1 macro (validação)', ['engine','subject_id','channel'], registry=registry)
    g_avg_conf     = Gauge('trainer_avg_confidence', 'Confiança média em amostras do treino', ['engine','subject_id','channel'], registry=registry)

    labels = (engine, subject_id, channel or '')

    g_status.labels(*labels).set(1.0 if status == 'READY' else 0.0)
    if duration_s  is not None: g_duration.labels(*labels).set(duration_s)
    if n_samples   is not None: g_samples.labels(*labels).set(n_samples)
    if n_features  is not None: g_features.labels(*labels).set(n_features)
    if n_classes   is not None: g_classes.labels(*labels).set(n_classes)
    if accuracy    is not None: g_accuracy.labels(*labels).set(accuracy)
    if f1_macro    is not None: g_f1_macro.labels(*labels).set(f1_macro)
    if avg_confidence is not None: g_avg_conf.labels(*labels).set(avg_confidence)

    job = f"trainer_{engine}"
    grouping = {'subject_id': subject_id, 'channel': channel or ''}

    push_to_gateway(PUSHGATEWAY_URL, job=job, grouping_key=grouping, registry=registry)