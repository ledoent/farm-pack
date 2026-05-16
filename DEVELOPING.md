# Developing farm-pack

## Local dev: install via the industry-packs workspace

This repo follows OCA conventions — it doesn't ship its own docker-compose. Use the
**ledoent industry-packs Doodba workspace** for local install and iteration:

```bash
cd /Users/dkendall/projects/ledoent/oca/industry-packs
invoke img-pull
invoke git-aggregate
invoke img-build
invoke develop
```

The workspace symlinks this repo into
`industry-packs/odoo/custom/src/private/farm-pack`, so edits in
`/Users/dkendall/projects/ledoent/farm-pack/` are immediately visible to Odoo. Update
the module after a code change:

```bash
invoke install -m farm_pack    # re-install / upgrade
invoke test farm_pack          # run the test suite
invoke restart                 # quick container restart
invoke logs odoo               # tail logs
```

Full workspace docs: `/Users/dkendall/projects/ledoent/oca/industry-packs/README.md`.

## Pre-commit workflow (in this repo)

```bash
# install pre-commit once
pip install pre-commit
pre-commit install

# before every commit
./scripts/preflight.sh    # runs pre-commit, re-stages auto-fixes
git commit -m "..."
git push
```

`./scripts/preflight.sh` is critical. Several pre-commit hooks auto-modify files during
commit (ruff-format, prettier-with-plugin-xml, oca-init-pyproject,
oca-gen-addon-readme). When they modify, **the commit aborts silently** — git exits
non-zero but `git push` reports "Everything up-to-date" without surfacing the failure.
`preflight.sh` re-stages and re-runs until clean.

## When something breaks

Read `docs/ODOO_19_GOTCHAS.md` first — every CI failure we've hit is catalogued with the
fix. Read `docs/CI_WORKFLOW.md` for what each gate catches and how to interpret a red
run.

## Module conventions

Each `farm_*` directory is one addon following OCA conventions:

- `farm_<noun>` snake_case naming
- `__manifest__.py` with `"version": "19.0.x.y.z"`
- AGPL-3 license
- Readme fragments in `readme/` (DESCRIPTION.md, USAGE.md, CONTRIBUTORS.md,
  newsfragments/)
- Tests in `tests/test_*.py`

The umbrella `farm_pack` is the customer install entry point. `farm_pack_demo` is heavy
demo data loaded on top.

## Held-back modules

`farm_csa_contract_glue` is currently `installable: False` because `odoo-addon-contract`
has no 19.0 wheel on the OCA wheelhouse yet. Re-enable when OCA publishes (see
ODOO_19_GOTCHAS.md → "OCA wheelhouse caveats").

## CI

GitHub Actions runs the OCA copier template's pre-commit + tests workflows on every push
to `19.0`. The CI lives entirely in this repo's `.github/workflows/`. The industry-packs
workspace is **not** part of this CI — it's a local dev convenience.
