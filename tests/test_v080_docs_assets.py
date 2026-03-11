from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v080_docs_exist() -> None:
    expected = [
        ROOT / 'docs' / 'what-is-tscfbench.md',
        ROOT / 'docs' / 'api-handbook.md',
        ROOT / 'docs' / 'use-cases.md',
        ROOT / 'docs' / 'environments.md',
        ROOT / 'docs' / 'cli-guide.md',
        ROOT / 'docs' / 'faq.md',
        ROOT / 'docs' / 'tutorials' / 'custom-panel-workflow.md',
        ROOT / 'examples' / 'package_tour.py',
        ROOT / 'examples' / 'custom_panel_data_demo.py',
    ]
    for path in expected:
        assert path.exists(), path
