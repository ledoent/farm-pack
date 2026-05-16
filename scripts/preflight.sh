#!/bin/bash
# preflight.sh — run pre-commit, auto-restage anything it modifies, verify clean.
#
# Solves the silent-abort problem: pre-commit's auto-formatters (ruff-format,
# prettier, oca-init-pyproject) modify files DURING the commit, which causes
# the commit to abort silently. The subsequent `git push` then says
# "Everything up-to-date" without ever surfacing the failure.
#
# Usage:
#   ./scripts/preflight.sh             — auto-format + re-stage + verify clean
#   ./scripts/preflight.sh --check-only — fail if anything would be modified

set -e

CHECK_ONLY=0
if [ "$1" = "--check-only" ]; then
  CHECK_ONLY=1
fi

cd "$(dirname "$0")/.."

if ! command -v pre-commit > /dev/null 2>&1; then
  echo "ERROR: pre-commit not installed. Run: pip install pre-commit" >&2
  exit 2
fi

# First pass: run pre-commit, capture whether anything was modified
echo "→ pre-commit run --all-files (pass 1)"
if pre-commit run --all-files; then
  echo "✓ pre-commit clean on first pass"
  exit 0
fi

if [ "$CHECK_ONLY" = "1" ]; then
  echo "✗ pre-commit reported issues (check-only mode, not fixing)"
  exit 1
fi

# Pass 1 made changes (or reported errors). Re-stage anything modified and
# re-run to verify the changes resolve everything.
echo "→ staging pre-commit auto-fixes"
git add -A

echo "→ pre-commit run --all-files (pass 2)"
if pre-commit run --all-files; then
  echo "✓ pre-commit clean after auto-fix; staged for commit"
  exit 0
fi

echo "✗ pre-commit still reports issues after auto-fix — manual intervention needed" >&2
exit 1
