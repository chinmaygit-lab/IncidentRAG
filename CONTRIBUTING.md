# Contributing

1. Create a virtual environment.
2. Install with `python -m pip install -e ".[dev]"`.
3. Run `python -m ruff check src tests`.
4. Run `python -m pytest -q`.
5. Keep retrieval behavior deterministic and add benchmark fixtures for ranking changes.
