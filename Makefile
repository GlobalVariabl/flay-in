# ─────────────────────────────────────────────
#  Makefile — FLY-IN Project
# ─────────────────────────────────────────────

PYTHON      := python3
MAIN        := route_all.py
VENV        := fly_env
PIP         := $(VENV)/bin/pip

.PHONY: install run debug lint lint-strict clean help

run:
	$(PYTHON) $(MAIN)

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy colorama
	@echo ""
	@echo "📌 Run this command manually:"
	@echo "   source $(VENV)/bin/activate"


debug:
	$(PYTHON) -m pdb $(MAIN)

lint:
	flake8 *.py
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs


lint-strict:
	flake8 *.py
	mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc"       -delete
	find . -type f -name "*.pyo"       -delete
