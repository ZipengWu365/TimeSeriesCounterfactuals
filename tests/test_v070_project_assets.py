from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_and_workflows_exist() -> None:
    expected = [
        ROOT / 'mkdocs.yml',
        ROOT / 'docs' / 'index.md',
        ROOT / 'docs' / 'quickstart.md',
        ROOT / '.github' / 'workflows' / 'ci.yml',
        ROOT / '.github' / 'workflows' / 'docs.yml',
        ROOT / '.github' / 'workflows' / 'release.yml',
        ROOT / 'CITATION.cff',
        ROOT / 'CONTRIBUTING.md',
    ]
    for path in expected:
        assert path.exists(), path
