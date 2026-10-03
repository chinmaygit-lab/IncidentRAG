# Validation snapshot

Validated in the build environment on 2026-10-03.

- `python -m pytest -q` -> **26 passed**
- `python -m compileall -q src tests` -> passed
- editable package build/install with `pip install -e . --no-deps --no-build-isolation` -> passed
- sample corpus seed -> **5 runbooks + 5 incidents**
- benchmark fixtures -> **10 queries**
- Recall@3 -> **1.0000**
- MRR -> **1.0000**
- nDCG@3 -> **1.0000**
- Hit@1 -> **1.0000**

The benchmark corpus is small and synthetic. These scores validate the retrieval/evaluation pipeline and its deterministic behavior; they are **not** a production-quality retrieval claim.

Ruff is configured in `pyproject.toml` and enforced by GitHub Actions. The build environment used for this handoff did not have Ruff installed and could not reach PyPI, so the local handoff validation used tests + compile checks instead of claiming a Ruff result.
