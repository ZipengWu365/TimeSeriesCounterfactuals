from __future__ import annotations

from tscfbench.agent import export_openai_function_tools
from tscfbench.cli import build_parser


def test_v110_cli_surface_includes_new_story_and_case_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'package-story' in names
    assert 'capability-map' in names
    assert 'api-atlas' in names
    assert 'scenario-matrix' in names
    assert 'tutorial-index' in names
    assert 'high-traffic-cases' in names
    assert 'public-data-sources' in names
    assert 'fetch-github-stars' in names
    assert 'fetch-coingecko' in names
    assert 'fetch-fred' in names
    assert 'make-release-kit' in names


def test_v110_agent_tool_surface_includes_new_story_and_case_tools() -> None:
    names = {tool['name'] for tool in export_openai_function_tools()}
    assert 'tscf_package_story' in names
    assert 'tscf_capability_map' in names
    assert 'tscf_api_atlas' in names
    assert 'tscf_scenario_matrix' in names
    assert 'tscf_tutorial_index' in names
    assert 'tscf_high_traffic_cases' in names
    assert 'tscf_public_data_sources' in names
    assert 'tscf_make_release_kit' in names
