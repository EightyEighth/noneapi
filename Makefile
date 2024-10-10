.PHONY: pre-build

test:
	pytest --cov=noneapi tests/ --full-trace -vvv

pre-build:
	pip install flake8 mypy isort black pytest requests pytest-cov
	flake8 noneapi/
	mypy noneapi/
	isort noneapi/
	pytest --cov=noneapi tests/ --full-trace -vvv
	rm -rf dist/
	python -m build

publish:
	python -m twine upload dist/*