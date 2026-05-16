# CI workflow & how to keep it green

The repo runs two GitHub Actions jobs on every push to `19.0`:

| Job            | What it gates on                                                                                                                                                           | Typical time |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| **pre-commit** | OCA template's ruff, ruff-format, prettier-with-plugin-xml, pylint-odoo, oca-checks-odoo-module, whool pyproject init, README fragment generation, requirements.txt regen  | ~45s         |
| **tests**      | `odoo_install_addons` (pip-resolves deps via OCA wheelhouse) → `oca_init_test_database` → `oca_run_tests` → `OCA_ENABLE_CHECKLOG_ODOO=1` promotes log WARNINGs to failures | ~2-3 min     |

The test job is the slow one. **A failure on the test job costs you 2-3 minutes per fix
iteration.** Run the local preflight first.

## Local preflight (matches CI in under a minute)

```bash
make lint          # pre-commit on all files (~30s after first install)
make smoke         # docker-based --init=farm_pack --stop-after-init (~45s)
make test          # smoke + --test-enable (runs every test)
make ci            # lint + smoke + test, the whole gate
```

First run will be slower because docker builds the image. Subsequent runs hit Docker's
layer cache.

## The pre-commit auto-fix gotcha

Several pre-commit hooks **modify files during commit** (ruff-format, prettier,
oca-init-pyproject, oca-gen-addon-readme). When they modify a file, the commit **aborts
silently** — git's exit code is non-zero but the next `git push` doesn't notice and
reports "Everything up-to-date."

Workaround: use `make format` (or `./scripts/preflight.sh`) before `git commit`. It runs
pre-commit, re-stages anything the hooks modified, and re-runs to verify clean. Then
your commit lands first try.

```bash
make format
git commit -m "..."
git push
```

## OCA checklog promotes WARNINGs to failures

`OCA_ENABLE_CHECKLOG_ODOO=1` (set in the workflow) means Odoo log WARNINGs cause CI to
fail even when tests pass. Watch out for:

- `tracking=True` on a model that doesn't inherit `mail.thread`
- Deprecation warnings (`group_operator=`, etc.)
- Field label collisions on the same model
- `return request.not_found()` instead of `raise request.not_found()`
- View attribute deprecations

If you see "0 failed, 0 error(s) of N tests" followed by "errors that caused failure"
listing WARNINGs, that's checklog. Mute the relevant logger in tests with
`mute_logger("odoo.http")` or fix the underlying cause.

## The OCA wheelhouse lag

The OCA wheelhouse at `https://wheelhouse.odoo-community.org/oca-simple-and-pypi`
publishes wheels lagging behind the repos. **The repo having a `19.0` branch does NOT
mean the wheel exists yet.** Before adding an OCA dep:

```bash
pip install --index-url=https://wheelhouse.odoo-community.org/oca-simple-and-pypi \
  --dry-run "odoo-addon-<MODULE>==19.0.*"
```

If "No matching distribution found," mark your module `installable: False` and re-enable
when the wheel ships. (We have `farm_csa_contract_glue` on this hold right now.)

## How to read a red CI

1. Open the failed run. Look for "errors that caused failure".
2. If you see `0 failed, 0 error(s)` — it's checklog catching a log message. Search for
   `WARNING` in the surrounding lines.
3. If you see a Python traceback — it's a real test failure or install error. Trace to
   the first line in the farm-pack source.
4. If you see `No matching distribution found` — it's the wheelhouse lag. Hold the
   affected module.

## Useful run-level commands

```bash
# List recent runs
gh run list --repo ledoent/farm-pack --limit 4

# View the failure log of the most recent test run
gh run view $(gh run list --repo ledoent/farm-pack --limit 1 --json databaseId --jq '.[0].databaseId') --log-failed | tail -40
```
