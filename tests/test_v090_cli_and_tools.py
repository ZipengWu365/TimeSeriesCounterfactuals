from __future__ import annotations

from tscfbench.agent import export_openai_function_tools
from tscfbench.cli import build_parser


def test_v090_cli_surface_includes_new_onboarding_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'start-here' in names
    assert 'workflow-recipes' in names
    assert 'benchmark-cards' in names
    assert 'recommend-path' in names


def test_v090_agent_tool_surface_includes_new_onboarding_tools() -> None:
    names = {tool['name'] for tool in export_openai_function_tools()}
    assert 'tscf_start_here' in names
    assert 'tscf_workflow_recipes' in names
    assert 'tscf_benchmark_cards' in names
    assert 'tscf_recommend_path' in names
