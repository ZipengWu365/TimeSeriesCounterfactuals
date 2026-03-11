from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v090_docs_exist() -> None:
    expected = [
        ROOT / 'docs' / 'start-here.md',
        ROOT / 'docs' / 'workflow-recipes.md',
        ROOT / 'docs' / 'benchmark-cards.md',
        ROOT / 'docs' / 'tutorials' / 'notebooks.md',
        ROOT / 'examples' / 'recommend_path_demo.py',
        ROOT / 'examples' / 'benchmark_card_demo.py',
    ]
    for path in expected:
        assert path.exists(), path


def test_v090_notebooks_are_valid_json() -> None:
    for name in [
        '01_start_here.ipynb',
        '02_package_tour.ipynb',
        '03_canonical_benchmark.ipynb',
        '04_custom_panel_data.ipynb',
        '05_agent_workflow.ipynb',
        '06_impact_workflow.ipynb',
        '07_method_paper_sweep.ipynb',
    ]:
        path = ROOT / 'notebooks' / name
        payload = json.loads(path.read_text(encoding='utf-8'))
        assert payload['nbformat'] == 4
        assert payload['cells']
