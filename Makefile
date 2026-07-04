PYTHON      := python3
MAIN        := route_all.py
VENV        := fly_env
PIP         := $(VENV)/bin/pip
MAP 		:= ./hard/02_capacity_hell.txt 

run:
	@$(PYTHON) $(MAIN) $(MAP)

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy "webcolors>=25.10.0"
	@echo ""
	@echo "Run this command manually:"
	@echo "   source $(VENV)/bin/activate"


debug:
	$(PYTHON) -m pdb $(MAIN)

lint:
	flake8 *.py
	mypy *.py \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

clean:
	@find . -name "__pycache__" -exec rm -rf {} +
	@find . -name ".mypy_cache" -exec rm -rf {} +

