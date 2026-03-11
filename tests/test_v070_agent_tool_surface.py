from __future__ import annotations

from tscfbench.agent import export_openai_function_tools


def test_agent_tool_surface_includes_v070_tools() -> None:
    names = {tool['name'] for tool in export_openai_function_tools()}
    assert 'tscf_install_matrix' in names
    assert 'tscf_list_canonical_studies' in names
    assert 'tscf_make_canonical_spec' in names
    assert 'tscf_run_canonical' in names
