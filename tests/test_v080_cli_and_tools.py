from __future__ import annotations

from tscfbench.agent import export_openai_function_tools
from tscfbench.cli import build_parser


def test_cli_surface_includes_v080_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'intro' in names
    assert 'api-handbook' in names
    assert 'use-cases' in names
    assert 'environments' in names
    assert 'cli-guide' in names


def test_agent_tool_surface_includes_v080_self_description_tools() -> None:
    names = {tool['name'] for tool in export_openai_function_tools()}
    assert 'tscf_package_overview' in names
    assert 'tscf_api_handbook' in names
    assert 'tscf_use_case_catalog' in names
    assert 'tscf_environment_profiles' in names
    assert 'tscf_cli_guide' in names
