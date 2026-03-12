from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v182_readme_has_copy_paste_own_data_commands() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Use your own data" in readme
    assert "python -m tscfbench run-csv-panel" in readme
    assert "python -m tscfbench run-csv-impact" in readme
    assert "docs/bring-your-own-data.md" in readme


def test_v182_docs_have_bring_your_own_data_page() -> None:
    doc = (ROOT / "docs" / "bring-your-own-data.md").read_text(encoding="utf-8")
    assert "run-csv-panel" in doc
    assert "run-csv-impact" in doc
    assert "Expected CSV shape" in doc
    assert "point-effect and cumulative-impact charts" in doc


def test_v182_mkdocs_nav_links_own_data_page() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "Bring your own data: bring-your-own-data.md" in mkdocs
