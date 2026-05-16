#!/bin/bash
# Entrypoint for the farm-pack review env container.
# 1. Wait for postgres
# 2. Initialize the DB with farm_pack + farm_pack_demo on first run
# 3. Serve Odoo
set -e

: "${HOST:=db}"
: "${USER:=odoo}"
: "${PASSWORD:?POSTGRES_PASSWORD not set}"
: "${ADMIN_PASSWORD:?ADMIN_PASSWORD not set}"
: "${DB_NAME:=farm_demo}"
: "${INIT_MODULES:=farm_pack,farm_pack_demo}"
: "${DEMO:=1}"

ADDONS=/mnt/farm-pack
ODOO_RC=/tmp/odoo.conf

cat > "$ODOO_RC" <<EOF
[options]
admin_passwd = ${ADMIN_PASSWORD}
db_host = ${HOST}
db_user = ${USER}
db_password = ${PASSWORD}
db_name = ${DB_NAME}
addons_path = ${ADDONS},/opt/odoo/odoo/addons,/opt/odoo/addons
data_dir = /var/lib/odoo
list_db = False
proxy_mode = True
xmlrpc_interface = 0.0.0.0
EOF

echo "[farm-entrypoint] waiting for postgres at ${HOST}..."
for i in $(seq 1 30); do
  if pg_isready -h "${HOST}" -U "${USER}" > /dev/null 2>&1; then
    break
  fi
  sleep 2
done

# If the DB doesn't exist yet, create + initialize.
if ! psql -h "${HOST}" -U "${USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
  echo "[farm-entrypoint] initializing ${DB_NAME} with ${INIT_MODULES}..."
  DEMO_FLAG=""
  if [ "${DEMO}" = "0" ]; then
    DEMO_FLAG="--without-demo=all"
  fi
  odoo \
    --config="$ODOO_RC" \
    --init="${INIT_MODULES}" \
    --stop-after-init \
    --log-level=info \
    ${DEMO_FLAG}
fi

echo "[farm-entrypoint] starting Odoo..."
exec odoo --config="$ODOO_RC" "$@"
