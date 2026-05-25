#!/usr/bin/env bash
set -euo pipefail

COMMAND="${1:-start}"

usage() {
  cat <<'EOF'
Usage: ./run.sh [command]

Commands:
  start      Build if needed and start backend + frontend in the background
  dev        Build if needed and start backend + frontend in the foreground
  stop       Stop and remove the running containers
  restart    Stop, rebuild, and start again in the background
  build      Build the Docker images
  logs       Follow logs from both services
  status     Show container status
  backend    Follow backend logs only
  frontend   Follow frontend logs only
EOF
}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not available in PATH." >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required. Install Docker Desktop or the docker compose plugin." >&2
  exit 1
fi

if [ "$COMMAND" != "stop" ] && [ "$COMMAND" != "status" ] && [ ! -f .env ]; then
  echo ".env is missing. Create it from .env.example and fill your OpenRouter and GLPI credentials." >&2
  echo "cp .env.example .env" >&2
  exit 1
fi

case "$COMMAND" in
  start)
    docker compose up --build -d
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000"
    ;;
  dev)
    docker compose up --build
    ;;
  stop)
    docker compose down
    ;;
  restart)
    docker compose down
    docker compose up --build -d
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:8000"
    ;;
  build)
    docker compose build
    ;;
  logs)
    docker compose logs -f
    ;;
  status)
    docker compose ps
    ;;
  backend)
    docker compose logs -f backend
    ;;
  frontend)
    docker compose logs -f frontend
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    usage >&2
    exit 1
    ;;
esac
