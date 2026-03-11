from __future__ import annotations

import json
from pathlib import Path

from tscfbench.agent import export_openai_function_tools
from tscfbench.agent.tokens import estimate_json_tokens
from tscfbench.cli import build_parser, main
from tscfbench.demo_cases import demo_catalog
from tscfbench.onramp import doctor_report, run_quickstart
from tscfbench.share_packages import make_share_package_for_demo


def test_v150_cli_surface_includes_share_package_command() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'make-share-package' in names


def test_v150_doctor_reports_viz_ready_field() -> None:
    rep = doctor_report()
    assert 'viz_ready' in rep
    assert 'starter' in rep['recommended_installs']


def test_v150_quickstart_writes_generated_files_json(tmp_path: Path) -> None:
    payload = run_quickstart(tmp_path / 'quickstart', plot=True)
    assert payload['summary']['errors'] == 0
    assert Path(payload['generated_files_path']).exists()
    manifest = json.loads(Path(payload['generated_files_path']).read_text(encoding='utf-8'))
    assert 'plotting_mode' in manifest
    assert manifest['visual_assets']


def test_v150_make_share_package_for_demo(tmp_path: Path) -> None:
    payload = make_share_package_for_demo('repo-breakout', output_dir=tmp_path / 'share', plot=True)
    share_dir = Path(payload['share_package_dir'])
    assert share_dir.exists()
    assert (share_dir / 'SUMMARY.md').exists()
    assert (share_dir / 'CITATION.txt').exists()
    assert (share_dir / 'manifest.json').exists()


def test_v150_demo_catalog_has_new_flagships() -> None:
    ids = {row['id'] for row in demo_catalog()}
    assert {'climate-grid', 'hospital-surge', 'repo-breakout'} <= ids


def test_v150_tool_profiles_still_fit_onboarding_budget() -> None:
    minimal = export_openai_function_tools(profile='minimal')
    research = export_openai_function_tools(profile='research')
    assert estimate_json_tokens(minimal).approx_tokens < 3000
    assert estimate_json_tokens(research).approx_tokens < 5000


def test_v150_cli_make_share_package_runs(tmp_path: Path, capsys) -> None:
    code = main(['make-share-package', '--demo-id', 'city-traffic', '-o', str(tmp_path / 'share_pkg')])
    captured = json.loads(capsys.readouterr().out)
    assert code == 0
    assert Path(captured['share_package_dir']).exists()
