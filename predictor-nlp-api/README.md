# predict-api (FastAPI + spaCy + MinIO + Mongo)

Serviço de inferência NLU:
- Classifica **assunto (subject)** por **canal**,
- Prediz **intenção** e **entidades (NER)** do subject,
- **Cache** de modelos (LRU + TTL),
- **MinIO** para armazenamento de modelos (`tar.gz` do `nlp.to_disk`),
- **Mongo** para metadados e limiares,
- **Prévia de intenção** (shadow training curto).

## Endpoints

- `GET /health` → `{"status":"ok"}`
- `POST /predict?channel=PF`
  ```json
  { "text": "..." }
