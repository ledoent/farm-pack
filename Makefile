.PHONY: help lint format smoke test ci precommit clean

# Default DB name for local smoke testing
DB_NAME ?= farm_smoke
INIT_MODULES ?= farm_pack,farm_pack_demo

help: ## Show this help
	@echo "Farm Pack — local dev targets"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

lint: ## Run pre-commit on all files (does not modify; reports issues)
	@./scripts/preflight.sh --check-only

format: ## Run pre-commit and re-stage anything it modifies (commit-ready)
	@./scripts/preflight.sh

smoke: ## Boot Odoo via docker-compose and run --init=farm_pack to catch install errors
	@./scripts/smoke-install.sh "$(INIT_MODULES)"

test: ## Boot Odoo via docker-compose and run module tests (no UI)
	@DB_NAME=$(DB_NAME) ./scripts/smoke-install.sh --test "$(INIT_MODULES)"

ci: lint smoke test ## Full preflight — matches what GitHub Actions runs

precommit: format ## Alias for format

clean: ## Tear down the smoke-test docker stack and its volumes
	@cd deploy && docker compose down -v 2>/dev/null || true
