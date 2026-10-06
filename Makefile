.PHONY: install test coverage validate demo

install:
	python -m pip install -e ".[api,dev]"

test:
	pytest -q

coverage:
	coverage run -m pytest -q
	coverage report

validate:
	python scripts/validate.py

demo:
	python scripts/run_demo.py
