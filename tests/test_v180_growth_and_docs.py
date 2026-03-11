from __future__ import annotations

import json
from pathlib import Path

import nbformat

from tscfbench.demo_cases import demo_catalog
from tscfbench.onramp import run_quickstart, tool_profile_notes
from tscfbench.agent.tools import export_openai_function_tools
from tscfbench.agent.tokens import estimate_json_tokens
from tscfbench.share_packages import make_share_package_for_demo

ROOT = Path(__file__).resolve().parents[1]


def test_v180_new_flagship_demos_exist() -> None:
    ids = {row['id'] for row in demo_catalog()}
    assert {'detector-downtime', 'minimum-wage-employment', 'viral-attention'} <= ids


def test_v180_starter_profile_is_smallest() -> None:
    rows = {row['id']: row for row in tool_profile_notes()}
    assert rows['starter']['approx_tokens'] < rows['minimal']['approx_tokens'] < rows['research']['approx_tokens']
    assert rows['starter']['approx_tokens'] < 2000


def test_v180_export_default_cli_profile_stays_compact() -> None:
    starter = export_openai_function_tools(profile='starter')
    assert estimate_json_tokens(starter).approx_tokens < 2000


def test_v180_quickstart_writes_summary_json(tmp_path: Path) -> None:
    payload = run_quickstart(tmp_path / 'quickstart', plot=False)
    summary_path = Path(payload['summary_path'])
    assert summary_path.exists()
    data = json.loads(summary_path.read_text(encoding='utf-8'))
    assert data['kind'] == 'quickstart_summary'


def test_v180_new_share_package_has_headline(tmp_path: Path) -> None:
    payload = make_share_package_for_demo('detector-downtime', output_dir=tmp_path / 'share_pkg', plot=False)
    summary_json = Path(payload['share_manifest']['summary_json_path'])
    data = json.loads(summary_json.read_text(encoding='utf-8'))
    assert data['headline_result']


def test_v180_notebooks_have_real_outputs() -> None:
    nb_dir = ROOT / 'notebooks'
    notebooks = sorted(nb_dir.glob('*.ipynb'))
    assert len(notebooks) >= 20
    with_outputs = 0
    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        assert len(nb.cells) >= 5
        if any(getattr(cell, 'outputs', None) for cell in nb.cells if cell.cell_type == 'code'):
            with_outputs += 1
    assert with_outputs >= 12


def test_v180_docs_add_try_now_and_plain_language() -> None:
    assert (ROOT / 'docs' / 'try-now.md').exists()
    assert (ROOT / 'docs' / 'plain-language-guide.md').exists()
