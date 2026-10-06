import json

from incidentrag.cli import main


def test_cli_seed_and_health(tmp_path, sample_root, capsys):
    db = tmp_path / "cli.db"
    assert main(["--db", str(db), "seed-sample", "--root", str(sample_root)]) == 0
    seeded = json.loads(capsys.readouterr().out)
    assert seeded["documents"] == 20
    assert main(["--db", str(db), "health"]) == 0
    health = json.loads(capsys.readouterr().out)
    assert health["documents"] == 20


def test_cli_search(tmp_path, sample_root, capsys):
    db = tmp_path / "cli-search.db"
    main(["--db", str(db), "seed-sample", "--root", str(sample_root)])
    capsys.readouterr()
    assert main(["--db", str(db), "search", "service=orders HTTP 504", "--top-k", "2"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hits"][0]["document_id"] in {"orders_504", "inc_orders_2026"}


def test_cli_postgres_schema(capsys):
    assert main(["postgres-schema"]) == 0
    output = capsys.readouterr().out
    assert "PostgreSQL FTS schema" in output
    assert "pgvector extension" in output
