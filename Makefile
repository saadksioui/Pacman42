run:
	uv run python3 pacman.py config.json

install:
	uv sync
	uv pip install ./mazegenerator-2.1.0-py3-none-any.whl

debug:
	uv run python3 -m pdb pacman.py config.json

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .mypy_cache

lint:
	flake8 pacman.py paclib/
	mypy pacman.py paclib/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
