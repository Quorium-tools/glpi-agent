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

COMPOSE_FILE="${SCRIPT_DIR}/docker-compose.yml"

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "Compose file docker-compose.yml not found in ${SCRIPT_DIR}." >&2
  exit 1
fi

usage() {
  cat <<'USAGE'
Usage: ./docker.sh <command> [args...]

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
