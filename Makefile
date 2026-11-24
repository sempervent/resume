.PHONY: validate test build build-all audit clean

validate:
	uv run career-docs validate

test:
	uv run pytest

build:
	uv run career-docs build --profile data_architect

build-all:
	uv run career-docs build --all

audit:
	uv run career-docs audit

clean:
	rm -rf dist
