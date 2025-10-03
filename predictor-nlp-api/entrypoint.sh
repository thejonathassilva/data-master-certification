set -e

# Caminho do env (pode vir por ENV_FILE, senão cai no /app/local.env)
ENV_PATH="${ENV_FILE:-/local.env}"

if [ -f "$ENV_PATH" ]; then
  echo "Loading env from $ENV_PATH"
  set -a
  . "$ENV_PATH"     # exporta as variáveis do arquivo
  set +a
fi

exec uvicorn app.api.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"