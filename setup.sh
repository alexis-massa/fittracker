#!/usr/bin/env bash
# One-shot dev environment setup: writes .env, installs dependencies and
# git hooks (lint/format/type-check on commit, changelog on commit).
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .env ]; then
  echo ".env already exists - remove it first if you want to regenerate it."
  exit 1
fi

echo "MongoDB connection (leave blank to use a local MongoDB):"
read -rp "  Mongo URI [mongodb://localhost:27017]: " MONGO_URI
MONGO_URI=${MONGO_URI:-mongodb://localhost:27017}

cat > .env << EOF
MONGO_URI=${MONGO_URI}
DB_NAME=fittracker
APP_PORT=8080
EOF
echo "Wrote .env"

uv sync
uv run lefthook install
echo "Installed dependencies and git hooks"

echo
echo "Ready: uv run main.py"
