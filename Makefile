run:
	uv run python3 pacman.py config.json

install:
	uv sync
	uv pip install ./mazegenerator*.whl

debug:
	uv run python3 -m pdb pacman.py config.json

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .mypy_cache

lint:
	flake8 pacman.py paclib/
	mypy pacman.py paclib/ --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

package:
	pip install nuitka patchelf
	python3 -m nuitka --standalone --include-data-dir=assets=assets --include-package=pydantic --include-package=pydantic_core --include-module=contextvars --include-module=decimal --collect-all=pyray --collect-all=raylib pacman.py
	cp config.json pacman.dist/
	mv pacman.dist PacMan-1337
	rm -rf pacman.build
	zip -r PacMan-1337.zip PacMan-1337
	@echo "Packaging complete! PacMan-1337.zip is ready for Itch.io."