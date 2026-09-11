#!/usr/bin/env bash
# One-shot dev environment setup: writes .env, installs dependencies and
# git hooks (lint/format/type-check on commit, changelog on commit).
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists - remove it first if you want to regenerate it."
  exit 1
fi

cat > .env << EOF
DATABASE_URL=postgresql://fittracker:fittracker@localhost:5433/fittracker
APP_PORT=8080
COMPOSE_PROFILES=dev
EOF
echo "Wrote .env"

uv sync
uv run lefthook install
echo "Installed dependencies and git hooks"

echo
echo "Ready: docker compose up -d to start the local Postgres, then uv run main.py"
