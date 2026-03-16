#!/bin/bash
# Usage: ./scripts/new-poc.sh <experiments|pocs> <name>
set -e

TYPE=$1
NAME=$2
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ -z "$TYPE" || -z "$NAME" ]]; then
  echo "Usage: $0 <experiments|pocs> <name>"
  exit 1
fi

if [[ "$TYPE" != "experiments" && "$TYPE" != "pocs" ]]; then
  echo "Type must be 'experiments' or 'pocs'"
  exit 1
fi

TARGET="$ROOT/$TYPE/$NAME"

if [[ -d "$TARGET" ]]; then
  echo "Already exists: $TARGET"
  exit 1
fi

cp -r "$ROOT/$TYPE/_template" "$TARGET"
echo "Created: $TARGET"
echo ""
echo "Next steps:"
echo "  cd $TARGET"
echo "  python -m venv .venv && source .venv/bin/activate"
echo "  pip install -r requirements.txt"
if [[ -f "$TARGET/.env.example" ]]; then
  echo "  cp .env.example .env"
fi
