#!/usr/bin/env bash
set -euo pipefail

COMMAND="${1:-start}"

usage() {
  cat <<'EOF'
Usage: ./run.sh [command]

Commands:
  start      Build if needed and start all services in the background
  dev        Build if needed and start all services in the foreground
  stop       Stop and remove the running containers
  restart    Stop, rebuild, and start again in the background
  build      Build the Docker images
  logs       Follow logs from all services
  status     Show container status
  ticket     Follow Ticket Agent logs only
  knowledge  Follow Knowledge Base Agent logs only
  backend    Alias for ticket
  kb         Alias for knowledge
  frontend   Follow frontend logs only
EOF
}

print_urls() {
  echo "Frontend:          http://localhost:3003"
  echo "Ticket backend:    http://localhost:8003"
  echo "Knowledge backend: http://localhost:8004"
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
    print_urls
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
    print_urls
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
  ticket|backend)
    docker compose logs -f ticket-agent
    ;;
  knowledge|kb)
    docker compose logs -f knowledge-agent
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
