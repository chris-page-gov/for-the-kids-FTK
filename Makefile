.PHONY: validate build browser
validate:
	uv run --locked python -m unittest discover -s tests -v
	uv run --locked python scripts/site.py build
	uv run --locked python scripts/site.py check
build:
	uv run --locked python scripts/site.py build
browser:
	uv run --locked python scripts/browser_check.py
