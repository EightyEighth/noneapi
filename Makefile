.PHONY: pre-build

pre-build:
	pip install flake8 mypy isort black pytest requests pytest-cov
	flake8 zero_connect/
	mypy zero_connect/
	isort zero_connect/
	black zero_connect/
	pytest zero_connect/ --full-trace -vvv --cov=zero_connect --cov-report=term-missing --cov-report=html
	python setup.py sdist bdist_wheel