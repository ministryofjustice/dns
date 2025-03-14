CONFIG_FILE ?= config.yaml
ZONES_DIR ?= hostedzones

AWS_ACCESS_KEY_ID ?= $(shell aws configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY ?= $(shell aws configure get aws_secret_access_key)

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY

define check_aws_creds
	@if [ -z "$(AWS_ACCESS_KEY_ID)" ] || [ -z "$(AWS_SECRET_ACCESS_KEY)" ]; then \
		echo "AWS credentials are not set. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."; \
		exit 1; \
	fi
endef

.PHONY: help install edit-zone validate-zones sync-dry-run sync-apply list-zones dump-zone compare-zone clean test

help:
	@echo "Available commands:"
	@echo "  make check-empty-zones        - Run check for empty zones"
	@echo "  make clean                    - Clean up generated files"
	@echo "  make compare-zone zone=<zone> - Compare a zone file with its live configuration"
	@echo "  make dump-zone zone=<zone>    - Dump the current live configuration for a zone"
	@echo "  make edit-zone zone=<zone>    - Edit a hosted zone file"
	@echo "  make help                     - Show this help message"
	@echo "  make install                  - Set up the Python environment"
	@echo "  make list-zones               - List all zones"
	@echo "  make print-github-delegations - Identify GitHub Pages delegations and print the results"
	@echo "  make sync-apply               - Apply changes to all zones"
	@echo "  make sync-dry-run             - Perform a dry-run sync for all zones"
	@echo "  make test                     - Run the test suite"
	@echo "  make validate-zones           - Validate all zone files"

install:
	pip3 install pipenv
	pipenv install --dev

edit-zone:
	@if [ -z "$(zone)" ]; then \
		echo "Please specify a zone to edit. Usage: make edit-zone zone=example.com"; \
		exit 1; \
	fi
	@if [ ! -f "$(ZONES_DIR)/$(zone).yaml" ]; then \
		echo "Zone file for $(zone) not found. Creating a new file."; \
		touch "$(ZONES_DIR)/$(zone).yaml"; \
	fi
	$(EDITOR) "$(ZONES_DIR)/$(zone).yaml"

validate-zones:
	$(call check_aws_creds)
	octodns-validate --config-file=$(CONFIG_FILE) --quiet

sync-dry-run:
	$(call check_aws_creds)
	octodns-sync --config-file=$(CONFIG_FILE) --quiet

sync-apply:
	$(call check_aws_creds)
	octodns-sync --config-file=$(CONFIG_FILE) --doit

list-zones:
	@ls -1 $(ZONES_DIR)/*.yaml | sed 's/.*\///' | sed 's/\.yaml//'

dump-zone:
	$(call check_aws_creds)
	@if [ -z "$(zone)" ]; then \
		echo "Please specify a zone to dump. Usage: make dump-zone zone=example.com"; \
		exit 1; \
	fi
	octodns-dump --config-file=$(CONFIG_FILE) --output-dir=tmp $(zone). route53

compare-zone:
	$(call check_aws_creds)
	@if [ -z "$(zone)" ]; then \
		echo "Please specify a zone to compare. Usage: make compare-zone zone=example.com"; \
		exit 1; \
	fi
	@if [ ! -f "$(ZONES_DIR)/$(zone).yaml" ]; then \
		echo "Zone file for $(zone) not found."; \
		exit 1; \
	fi
	octodns-dump --config-file=$(CONFIG_FILE) --output-dir=tmp $(zone). route53
	@echo "Differences between local and live configuration:"
	@diff -u $(ZONES_DIR)/$(zone).yaml tmp/$(zone).yaml || true
	@rm -f tmp/$(zone).yaml

check-unmanaged-zones: install
	$(call check_aws_creds)
	@pipenv run python3 -m  bin.check_unmanaged_zones

check-empty-zones: install
	$(call check_aws_creds)
	@pipenv run python3 -m bin.check_empty_zones

clean:
	@pipenv --rm
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete

test: install
	@pipenv run python3 -m pytest tests/

print-github-delegations:
	@echo "Identifying GitHub Pages delegations..."
	@pipenv run python3 -m bin.identify_github_pages_delegations
	@echo "The file './.github_pages' has been updated with the latest GitHub Pages delegations."
	@cat .github_pages

.DEFAULT_GOAL := help

