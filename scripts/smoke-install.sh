#!/bin/bash
# smoke-install.sh — boot a throwaway Odoo via the deploy/ docker-compose
# stack, run --init=<MODULES> --stop-after-init, report install failures
# fast (typically 30-60s vs CI's 2-3 min round-trip).
#
# Usage:
#   ./scripts/smoke-install.sh                              # init farm_pack only
#   ./scripts/smoke-install.sh farm_pack,farm_pack_demo     # init multiple
#   ./scripts/smoke-install.sh --test farm_pack             # init + run tests

set -e

cd "$(dirname "$0")/.."

TEST_FLAG=""
if [ "$1" = "--test" ]; then
  TEST_FLAG="--test-enable"
  shift
fi
MODULES="${1:-farm_pack}"

cd deploy

# Use a unique DB per invocation so multiple smoke runs don't collide
DB_NAME="${DB_NAME:-smoke_$(date +%s)}"
export DB_NAME

# Make sure .env exists (auto-generate a throwaway one if not)
if [ ! -f .env ]; then
  cat > .env <<EOF
POSTGRES_PASSWORD=smoke_$(openssl rand -hex 8 2>/dev/null || echo throwaway)
ADMIN_PASSWORD=smoke_admin
DB_NAME=$DB_NAME
INIT_MODULES=$MODULES
DEMO=1
ODOO_PORT=8069
EOF
  echo "→ generated throwaway deploy/.env"
fi

echo "→ docker compose up -d db (postgres)"
docker compose up -d db

echo "→ docker compose build odoo"
docker compose build odoo

echo "→ initialising DB '$DB_NAME' with modules: $MODULES $TEST_FLAG"
docker compose run --rm \
  -e DB_NAME="$DB_NAME" \
  -e INIT_MODULES="$MODULES" \
  odoo \
  bash -c "odoo --config=/tmp/odoo.conf --init=$MODULES --stop-after-init --log-level=info $TEST_FLAG 2>&1 | tail -80"

echo ""
echo "✓ smoke install completed without crashing for DB '$DB_NAME'"
echo "   To clean up: docker compose down -v"
