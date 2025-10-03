🚀 IA de Contingência – Projeto de Alta Disponibilidade no Chat
1. Visão Geral – O “Porquê” do Projeto
📌 Problema Real

Hoje, quando a IA principal (Watson) oscila ou falha, não existe contingência — a operação para.
Isso compromete diretamente a experiência do cliente e a disponibilidade do chat.

💡 Proposta

Construir uma IA de contingência plugável, com pipeline de treinamento tradicional e bibliotecas compatíveis com a stack existente de dados (IA secundária com as mesmas libs disponiveis de uso no banco) - Menção honroza a ideia para: Mirela Souto Felix Cavalcanti:

MongoDB para metadados

MinIO para armazenamento de artefatos

Kafka para orquestração

Essa IA secundária pode assumir automaticamente quando a primária falhar, preservando a continuidade do atendimento. (Justamente o que procuro estruturar no case para trazer a dor do banco)

🔑 Como entregamos isso

Dois motores de IA convivendo:

spacy → Intenção + NER

J_Assistant → Scikit-learn (TfidfVectorizer + RandomForest) para intenção

Treinamento assíncrono via Kafka:

Trainers consomem o mesmo tópico

Artefatos versionados no MinIO

Metadados no Mongo

Config-API:

Roteamento por engine (ex.: spacy-IA ↔ /api/predict, J_assistant ↔ /api/predict)

Fallback elegante: 404/500 → "Precisa de mais treinamento..."

Console Angular:

Seletor de Canal e IA

CRUD de Canais / Assuntos / Intenções / Entidades / Nós

Prévia com nível de confiança

2. Arquitetura Proposta
flowchart LR
  subgraph Console["Console (Angular)"]
    A[Simulador\nEscolhe Canal/IA] -->|POST texto| P(Config-API)
    CRUD[CRUD Configs] --> CfgAPI(Config-API)
  end

  %% Roteamento por engine no Predict-API
  P -->|IA=spacy-IA| S1[/Predictor spaCy/]
  P -->|IA=J_Assistant| S2[/Predictor J_Assistant/]
  P --> M[(MongoDB)]

  %% Config e dados de treino
  CfgAPI <--> M[(MongoDB)]
  CfgAPI -->|enqueue train| TrReq[[Kafka: train.requests]]

  %% Trainers
  TrReq --> TW1(Trainer spaCy)
  TrReq --> TW2(Trainer J_Assistant\nTF-IDF+RandomForest)

  TW1 --> MinIO[(MinIO: modelos)]
  TW2 --> MinIO
  TW1 --> M
  TW2 --> M

  %% Predição -> consulta meta no Mongo e baixa artefato no MinIO
  S1 -->|read meta/version| M
  S2 -->|read meta/version| M
  S1 -->|load model| MinIO
  S2 -->|load model| MinIO

  %% Observabilidade
  Obs[(Prometheus/Grafana)] -. metrics/logs .-> P
  Obs -. metrics/logs .-> CfgAPI
  Obs -. metrics/logs .-> TW1
  Obs -. metrics/logs .-> TW2

Pontos-Chave

Roteamento por engine → alternância/contingência em tempo de execução

Treinadores desacoplados → idempotentes via Kafka

Artefatos versionados → ex.: s3://nlp-models/{Canal}/{Subject}/{Versão}/model.pkl

Observabilidade → métricas/logs em Prometheus/Grafana

Escalabilidade → serviços stateless, Kafka particionado, MinIO replicável

3. Como Cobrimos os Requisitos
3.1 Treinamento do Modelo

Dados de treino via Config-API/Mongo

Suporte a múltiplos algoritmos:

spaCy-IA → NLU (intenção + NER)

J_Assistant → TfidfVectorizer + RandomForest

Persistência:

Exemplos/defs → Mongo

Artefatos → MinIO

Metadados (métricas, versões) → model_versions

3.2 CI/CD

CI:

Testes unitários (Config-API, trainers)

Build de containers

CD:

Cada merge ou trigger → envia mensagem a Kafka

Trainers versionam e publicam modelo no MinIO

Config-API lê versão ativa (subjects.activeModelVersion.{engine})

Implantação sem downtime

3.3 Orquestração

Kafka como orquestrador

Pipeline auto-contido:
Config-API → Kafka → Trainers → MinIO/Mongo → Predictors

3.4 Gerenciamento de Artefatos

MinIO centraliza modelos (.pkl, .tar.gz)

model_versions no Mongo referencia:

minio_uri

engine, scope, channel, subject_id

métricas, status, correlation_id

3.5 Observabilidade

Logs estruturados com correlation_id

Exporters Prometheus: treinos, latência, taxa de erro

Alertas automáticos:

Latência do Watson ↑ → chavear engine para J_assistant

Confiança ↓ → acionar retreino

3.6 Escalabilidade

Serviços stateless e replicáveis (Docker/K8s)

Kafka partitions → escalam trainers/predictors

MinIO horizontal

Mongo replicado para HA

Config-API com cache leve de modelos ativos

4. Dor de Negócio Endereçada

“Quando a IA principal (Watson) apresenta problemas, a operação fica sem resposta.”

Como o projeto resolve:

Dual engine no Config-API (spaCy + StickLearn)

Fallback controlado → resposta neutra ou engine secundária

Pipeline sob nosso domínio (MinIO/Mongo/Kafka)

Roteiro de contingência simples:

chavear engine ativa

degrade para respostas default

5. Justificativa Tecnológica

Angular + Material → console produtivo e consistente

Spring Boot → Config-API robusto

Python FastAPI → workers rápidos e leves

spaCy → NER + intenção (suporte a PT-BR)

Scikit-learn → simplicidade + eficácia (Tfidf + RF)

Kafka → orquestração e reprocessamento

MinIO → S3-like on-prem

MongoDB → configs flexíveis

Prometheus/Grafana/ELK → observabilidade

6. Plano de Implementação (End-to-End)
🏗️ Fundação

Subir Kafka, MinIO, Mongo e serviços (docker-compose/k8s)

# docker compose build

# docker compose up -d

Criar bucket nlp-models

Criar coleções: intents, subjects, model_versions

⚙️ Modelagem & Config

Cadastrar canais (PF/PJ), assuntos, intenções e entidades

Exemplos de curadoria para treinamentos do assuntos em csv na pasta "exemplos-curadoria"

Definir thresholds e vincular nós de diálogo

🎓 Treinamento

Front envia comando “Treinar” → mensagem Kafka

Trainers:

versionam

publicam no MinIO

registram no Mongo

Ativar versão: subjects.activeModelVersion.{engine} = vX

🤖 Predição & Contingência

Config-API lê versão ativa do engine

Carrega modelo do MinIO e responde

Falha no primário → fallback mensagem / engine secundária

📊 Observabilidade & CI/CD

Pipelines de build/test/deploy

Alarmes de erro/latência/confiança