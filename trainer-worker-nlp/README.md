# trainer-worker-nlp (Python 3.11)

Worker de treinamento NLU para spaCy 3.7.x consumindo pedidos via Kafka, montando datasets a partir do MongoDB, versionando e publicando modelos no MinIO e registrando versões/métricas no Mongo. Emite status no Kafka.

## Objetivos
- **Escopos**: `subject`, `channel` ou `both`
- **Warm-start** de versão READY ou usando modelo base (ex.: `pt_core_news_md`)
- **Cold-start** (spaCy blank)
- **Treino**:
  - Subject: `textcat` exclusivo (intenções) + `ner` (entidades fracas via regex/gazetteer)
  - Channel: `textcat` exclusivo por `subject`
- **Publicação**: `nlp.to_disk()` → `model.tar.gz` → MinIO
- **Registro**: coleção `model_versions` no Mongo
- **Status**: publica em `train.status`

## Tópicos Kafka
- Pedidos: `train.requests`
- Status: `train.status`
- Key: `subject_id`
- Grupo do worker: `trainer-worker`

## Requisitos
- Python 3.11
- spaCy 3.7.x, kafka-python 2.x, pymongo 4.8, minio 7.2, click, pytest

## Variáveis (.env)
Veja `.env.example`.

## Execução local
```bash
python -m venv .venv && source .venv/bin/activate    # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python -m spacy download pt_core_news_md             # opcional, se quiser base linguística
export $(grep -v '^#' .env | xargs)                  # ou use direnv
python -m app.cli run-worker                         # inicia o loop do worker (Kafka)
