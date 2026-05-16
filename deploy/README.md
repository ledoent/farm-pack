# Farm Pack — Review Environment

Spin up a working `farm_pack + farm_pack_demo` Odoo instance in two commands. Used for
partner demos, design reviews, and integration testing without a full Hetzner k3s
deployment.

## What you get

- Postgres 16
- Odoo 19.0 on the OCA CI image (same image our test workflow uses)
- The whole `farm-pack` repo bind-mounted into the container — iterate on the modules
  without rebuilding
- `farm_pack + farm_pack_demo` pre-installed on first boot:
  - 9 partners, 8 published products, 2 coops with 5 days of egg collection, 3 active
    CSA subscriptions, 1 Tuesday delivery route, a Saturday market event with 2
    preorders ready for the Pick List button, and a QBO sandbox connection
- Reachable at `http://your-host:8069`

## Quick start

```bash
# from the repo root
cd deploy
cp .env.example .env
# edit .env: set strong POSTGRES_PASSWORD and ADMIN_PASSWORD
docker compose up -d
```

Wait ~60 seconds for first-boot DB initialization (the entrypoint runs
`odoo --init=farm_pack,farm_pack_demo --stop-after-init` on first run), then visit
`http://your-host:8069` and log in with `admin` / your `ADMIN_PASSWORD`.

## Per-partner DBs

Each design partner gets their own DB on the same box:

```bash
DB_NAME=acme_review docker compose up -d
DB_NAME=bobs_farm   docker compose up -d
```

(Or run multiple stacks with different `ODOO_PORT` values.)

## Updating

After pulling new commits, restart Odoo with module upgrade:

```bash
docker compose exec odoo odoo --config=/tmp/odoo.conf -u farm_pack --stop-after-init
docker compose restart odoo
```

## Hetzner k3s — coming in v1

The Kubernetes manifests for self-hosted Runboat-style per-PR previews land in
`deploy/k3s/` in a follow-up. For now, point a single domain (e.g. `coop.ledoweb.com`)
at one Hetzner box running this docker-compose and you have a partner-demo URL today.

## Notes

- The `farm_csa_contract_glue` module is held back (`installable: False`) because OCA
  hasn't published `odoo-addon-contract==19.0.*` to its wheelhouse yet. The umbrella
  works without it.
- `intuit-oauth` and `python-quickbooks` are installed best-effort in the Dockerfile; if
  the wheelhouse doesn't have them, the QBO module silently falls back to stub mode
  (still functional for demos).
- The filestore is a named volume — back it up with
  `docker run --rm -v farm-pack-review_filestore:/data alpine tar czf - /data`.
