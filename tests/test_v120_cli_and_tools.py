from __future__ import annotations

from tscfbench.agent import export_openai_function_tools
from tscfbench.cli import build_parser



def test_v120_cli_surface_includes_positioning_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'ecosystem-audit' in names
    assert 'feature-coverage' in names
    assert 'differentiators' in names
    assert 'github-readme' in names
    assert 'website-home' in names
    assert 'agent-first-design' in names
    assert 'make-positioning-assets' in names



def test_v120_agent_tool_surface_includes_positioning_tools() -> None:
    names = {tool['name'] for tool in export_openai_function_tools()}
    assert 'tscf_ecosystem_audit' in names
    assert 'tscf_feature_coverage' in names
    assert 'tscf_differentiators' in names
    assert 'tscf_github_readme' in names
    assert 'tscf_website_home' in names
    assert 'tscf_agent_first_design' in names
    assert 'tscf_make_positioning_assets' in names
