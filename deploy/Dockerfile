# Base on OCA's CI image — Odoo 19.0 with whool, manifestoo, pre-commit
# tooling pre-installed. Same image the test workflow uses, so the local
# review env behaves identically to CI.
FROM ghcr.io/oca/oca-ci/py3.10-odoo19.0:latest

USER root

# Pin pip cache outside the read-only repo mount.
ENV PIP_CACHE_DIR=/var/cache/pip
RUN mkdir -p ${PIP_CACHE_DIR} && chown -R odoo:odoo ${PIP_CACHE_DIR}

# Optional external Python deps for farm_quickbooks_io. If the OCA
# wheelhouse doesn't have them, this still succeeds because we don't
# pin versions strictly here — the package falls back to stub mode at
# runtime if libs are missing.
RUN pip install --no-cache-dir --index-url=https://wheelhouse.odoo-community.org/oca-simple-and-pypi \
    intuit-oauth python-quickbooks || true

COPY entrypoint.sh /usr/local/bin/farm-entrypoint
RUN chmod +x /usr/local/bin/farm-entrypoint

USER odoo
WORKDIR /opt/odoo
EXPOSE 8069

ENTRYPOINT ["/usr/local/bin/farm-entrypoint"]
