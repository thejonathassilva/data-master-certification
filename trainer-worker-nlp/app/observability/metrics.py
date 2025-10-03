import os
from typing import Optional
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://pushgateway:9091")

def push_training_metrics(
    *,
    engine: str,                      # 'spacy-IA'
    scope: str,                       # 'channel' | 'subject'
    channel: Optional[str],           # ex.: 'PF' (para scope=channel) ou do próprio subject
    subject_id: Optional[str],        # string com _id quando scope=subject
    version: Optional[str],           # versão alvo (ex.: v20250930-120000)
    status: str,                      # 'READY' | 'FAILED'
    duration_s: Optional[float] = None,
    n_samples: Optional[int] = None,
    n_labels: Optional[int] = None,   # nº de classes: subjects (no canal) ou intents (no subject)
    has_ner: Optional[bool] = None,   # somente para scope=subject
    textcat_epochs: Optional[int] = None,
    ner_epochs: Optional[int] = None,
    accuracy: Optional[float] = None,
    f1_macro: Optional[float] = None,
):
    """
    Empurra um conjunto de métricas do job de treinamento para o Pushgateway.
    Só publica o que não for None. Labels padronizados: engine, scope, channel, subject_id, version.
    """
    reg = CollectorRegistry()

    g_status   = Gauge('trainer_status', '1=READY,0=FAILED', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_duration = Gauge('trainer_duration_seconds', 'Duração total do treinamento', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_samples  = Gauge('trainer_samples_total', 'Amostras usadas no treinamento', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_labels   = Gauge('trainer_labels_total', 'Total de classes (subjects no canal, intents no subject)', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_acc      = Gauge('trainer_accuracy', 'Acurácia (se disponível)', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_f1m      = Gauge('trainer_f1_macro', 'F1 macro (se disponível)', ['engine','scope','channel','subject_id','version'], registry=reg)

    g_has_ner  = Gauge('trainer_has_ner', '1=tem NER no subject, 0=não', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_ep_tc    = Gauge('trainer_textcat_epochs', 'Épocas de treino do textcat', ['engine','scope','channel','subject_id','version'], registry=reg)
    g_ep_ner   = Gauge('trainer_ner_epochs', 'Épocas de treino do NER', ['engine','scope','channel','subject_id','version'], registry=reg)

    labels = (engine, scope, channel or '', subject_id or '', version or '')

    g_status.labels(*labels).set(1.0 if status == 'READY' else 0.0)
    if duration_s is not None: g_duration.labels(*labels).set(duration_s)
    if n_samples  is not None: g_samples.labels(*labels).set(n_samples)
    if n_labels   is not None: g_labels.labels(*labels).set(n_labels)
    if accuracy   is not None: g_acc.labels(*labels).set(accuracy)
    if f1_macro   is not None: g_f1m.labels(*labels).set(f1_macro)
    if has_ner    is not None: g_has_ner.labels(*labels).set(1.0 if has_ner else 0.0)
    if textcat_epochs is not None: g_ep_tc.labels(*labels).set(textcat_epochs)
    if ner_epochs is not None: g_ep_ner.labels(*labels).set(ner_epochs)

    job = f"trainer_{engine}_{scope}"
    grouping_key = {k: v for k, v in {
        'channel': channel or '',
        'subject_id': subject_id or '',
        'version': version or ''
    }.items() if v}

    push_to_gateway(PUSHGATEWAY_URL, job=job, grouping_key=grouping_key, registry=reg)
