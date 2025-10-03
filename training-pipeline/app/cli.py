import json
import logging
import click
from app.logging_config import configure_logging
from app.worker import handle_request
from app.adapters.kafka_consumer import create_consumer

@click.group()
def cli():
    configure_logging()

@cli.command("run-worker")
def run_worker():
    log = logging.getLogger("worker")
    consumer = create_consumer()
    log.info("Worker iniciado. Aguardando mensagens...")
    for msg in consumer:
        key = msg.key
        val = msg.value
        log.info(f"Mensagem recebida key={key} value={json.dumps(val)[:300]}...")
        handle_request(val)

@cli.command("train")
@click.option("--scope", required=True, type=click.Choice(["subject","channel","both"]))
@click.option("--subject-id", required=False, default=None)
@click.option("--channel", required=False, default=None)
@click.option("--versioning-strategy", default="auto")
@click.option("--base-version", default=None)
@click.option("--base-lang-model", default=None)
@click.option("--requested-by", default="console")
@click.option("--notes", default=None)
@click.option("--correlation-id", default=None)
def train_cmd(**kwargs):
    """Dispara um treino ad-hoc (sem Kafka)."""
    handle_request(kwargs)

if __name__ == "__main__":
    cli()
