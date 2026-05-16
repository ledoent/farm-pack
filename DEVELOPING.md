# Contributing to farm-pack

## Quick start

```bash
# install pre-commit once
pip install pre-commit
pre-commit install

# before every commit
make format          # runs pre-commit, re-stages auto-fixes
git commit -m "..."
git push
```

## The two commands you'll run most

| Command       | What it does                                                                                                                        | Time                   |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `make format` | Run pre-commit, auto-stage any fixes, verify clean. Solves the silent-abort-on-commit problem.                                      | ~30s                   |
| `make smoke`  | Docker-boot an Odoo with the repo mounted, run `--init=farm_pack --stop-after-init`. Catches install errors locally before pushing. | ~45s after first build |

Together these catch ~80% of what CI would catch, in under a minute.

## Why `make format` is critical

Several pre-commit hooks auto-modify files during commit (ruff-format,
prettier-with-plugin-xml, oca-init-pyproject, oca-gen-addon-readme). When they modify,
**the commit aborts silently** — git exits non-zero but the subsequent `git push`
reports "Everything up-to-date" without surfacing the failure.

`make format` runs pre-commit, re-stages anything modified, and re-runs to verify clean.
Then your commit lands first try.

## Full CI parity locally

```bash
make ci   # lint + smoke + test  (≈3-4 min after first docker build)
```

This matches what GitHub Actions runs. If `make ci` is green, your push will be green
too.

## When something breaks

Read `docs/ODOO_19_GOTCHAS.md` first — every CI failure we've hit is catalogued there
with the fix. Read `docs/CI_WORKFLOW.md` for what each gate catches and how to interpret
a red run.

## Modules

Each `farm_*` directory is one addon. Module conventions follow OCA:

- `farm_<noun>` snake_case naming
- `__manifest__.py` with `version = "19.0.x.y.z"`
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

## Deployment

The `deploy/` directory has a docker-compose recipe for stand-up. Same image CI uses, so
the local review env behaves identically to the test workflow.
