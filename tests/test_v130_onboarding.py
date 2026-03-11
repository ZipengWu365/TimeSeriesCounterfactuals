from __future__ import annotations

import json
from pathlib import Path

from tscfbench.agent import export_openai_function_tools, export_runtime_profile
from tscfbench.cli import build_parser, main
from tscfbench.integrations.adapters import OptionalDependencyError
from tscfbench.onramp import run_quickstart
from tscfbench.sweeps import SweepCellSpec, SweepMatrixSpec, run_sweep


def test_v130_cli_surface_includes_onramp_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'quickstart' in names
    assert 'doctor' in names
    assert 'essentials' in names
    assert 'list-tool-profiles' in names



def test_v130_quickstart_writes_zero_error_run(tmp_path: Path) -> None:
    payload = run_quickstart(tmp_path / 'quickstart')
    assert payload['kind'] == 'quickstart_run'
    assert Path(payload['spec_path']).exists()
    assert Path(payload['results_path']).exists()
    assert Path(payload['report_path']).exists()
    assert payload['summary']['errors'] == 0



def test_v130_runtime_profile_aliases_work() -> None:
    default_profile = export_runtime_profile('default')
    planning_profile = export_runtime_profile('planning')
    analysis_profile = export_runtime_profile('analysis')
    editing_profile = export_runtime_profile('editing')
    assert default_profile['profile']['phase'] == 'planning'
    assert planning_profile['profile']['id'] == default_profile['profile']['id']
    assert analysis_profile['profile']['phase'] == 'analysis'
    assert editing_profile['profile']['phase'] == 'editing'



def test_v130_openai_tool_profiles_are_smaller_for_minimal() -> None:
    full = export_openai_function_tools(profile='full')
    minimal = export_openai_function_tools(profile='minimal')
    full_names = {tool['name'] for tool in full}
    minimal_names = {tool['name'] for tool in minimal}
    assert len(minimal) < len(full)
    assert 'tscf_start_here' in minimal_names
    assert 'tscf_make_canonical_spec' in minimal_names
    assert 'tscf_ecosystem_audit' in full_names
    assert 'tscf_ecosystem_audit' not in minimal_names



def test_v130_estimate_tokens_accepts_positional_path_and_serializes(tmp_path: Path, capsys) -> None:
    sample = tmp_path / 'README.md'
    sample.write_text('# hello\nthis is a test\n', encoding='utf-8')
    exit_code = main(['estimate-tokens', str(sample)])
    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert exit_code == 0
    assert payload['source'].endswith('README.md')
    assert payload['text_tokens']['approx_tokens'] > 0
    assert payload['json_tokens']['approx_tokens'] >= payload['text_tokens']['approx_tokens']



def test_v130_missing_optional_backend_is_marked_skipped(monkeypatch) -> None:
    def boom(_cell):
        raise OptionalDependencyError('Missing optional dependency. Install with: pip install somepkg')

    monkeypatch.setattr('tscfbench.sweeps._run_panel_cell', boom)
    spec = SweepMatrixSpec(cells=[SweepCellSpec(task_family='panel', dataset='synthetic_latent_factor', model='pysyncon')])
    run = run_sweep(spec)
    assert run.results[0].status == 'skipped_optional_dependency'
    assert run.summary()['skipped'] == 1
    assert run.summary()['errors'] == 0
