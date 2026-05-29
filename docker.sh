#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if present
if [ -f "${SCRIPT_DIR}/.env" ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/.env"
  set +o allexport
fi

ENVIRONMENT="${NODE_ENV:-production}"
ENVIRONMENT="$(printf '%s' "${ENVIRONMENT}" | tr '[:upper:]' '[:lower:]')"

if [[ "${ENVIRONMENT}" == "development" ]]; then
  PROFILE="dev"
elif [[ "${ENVIRONMENT}" == "test" ]]; then
  PROFILE="test"
else
  PROFILE="prod"
fi

echo "Running app in ${ENVIRONMENT} mode (profile: ${PROFILE})..."

COMPOSE_FILE="${SCRIPT_DIR}/docker-compose-${PROFILE}.yml"

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "Compose file docker-compose-${PROFILE}.yml not found in ${SCRIPT_DIR}." >&2
  echo "Check that NODE_ENV maps to an existing profile (development->dev, test->test, production->prod)." >&2
  exit 1
fi

usage() {
  cat <<'USAGE'
Usage: ./docker.sh <command> [args...]

Environment:
  NODE_ENV=development|test|production   Select compose profile (default: production)

Commands:
  build   Build and start services (detached)
  down    Stop and remove services
  logs    Follow logs from all services
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
shift || true

case "${cmd}" in
  build)
    docker compose -f "${COMPOSE_FILE}" up --build -d "$@"
    ;;
  down)
    docker compose -f "${COMPOSE_FILE}" down "$@"
    ;;
  logs)
    docker compose -f "${COMPOSE_FILE}" logs -f "$@"
    ;;
  *)
    usage
    exit 1
    ;;
esac
