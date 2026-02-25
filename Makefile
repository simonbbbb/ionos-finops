.PHONY: help install install-dev test lint format clean build publish update-pricing validate-pricing

help:
	@echo "IONOS FinOps - Makefile commands"
	@echo ""
	@echo "install          Install package"
	@echo "install-dev      Install package with dev dependencies"
	@echo "test             Run tests"
	@echo "lint             Run linters"
	@echo "format           Format code with black and isort"
	@echo "clean            Clean build artifacts"
	@echo "build            Build distribution packages"
	@echo "publish          Publish to PyPI"
	@echo "update-pricing  Update pricing data from IONOS API"
	@echo "validate-pricing Validate existing pricing data"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=ionos_finops --cov-report=html --cov-report=term

lint:
	flake8 ionos_finops tests
	mypy ionos_finops

format:
	black ionos_finops tests
	isort ionos_finops tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

update-pricing:
	@echo "🔄 Updating pricing data from IONOS API..."
	@if [ -z "$(IONOS_TOKEN)" ]; then \
		echo "❌ Error: IONOS_TOKEN environment variable not set"; \
		echo "Set it with: export IONOS_TOKEN=your_token"; \
		exit 1; \
	fi
	python scripts/manual_pricing_update.py

validate-pricing:
	@echo "🔍 Validating pricing data..."
	python scripts/manual_pricing_update.py --validate-only

force-update-pricing:
	@echo "🔄 Force updating pricing data from IONOS API..."
	@if [ -z "$(IONOS_TOKEN)" ]; then \
		echo "❌ Error: IONOS_TOKEN environment variable not set"; \
		echo "Set it with: export IONOS_TOKEN=your_token"; \
		exit 1; \
	fi
	python scripts/manual_pricing_update.py --force

update-region:
	@if [ -z "$(REGION)" ]; then \
		echo "❌ Error: REGION not specified"; \
		echo "Usage: make update-region REGION=de/fra"; \
		exit 1; \
	fi
	@if [ -z "$(IONOS_TOKEN)" ]; then \
		echo "❌ Error: IONOS_TOKEN environment variable not set"; \
		echo "Set it with: export IONOS_TOKEN=your_token"; \
		exit 1; \
	fi
	@echo "🔄 Updating pricing for region: $(REGION)"
	python scripts/manual_pricing_update.py --region $(REGION)
