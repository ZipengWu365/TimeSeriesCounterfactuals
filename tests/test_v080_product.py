from __future__ import annotations

from tscfbench.product import (
    api_handbook,
    cli_guide,
    environment_profiles,
    package_overview,
    render_api_handbook_markdown,
    render_package_overview_markdown,
    render_use_cases_markdown,
    use_case_catalog,
)


def test_product_catalogs_are_populated() -> None:
    overview = package_overview()
    assert overview["name"] == "tscfbench"
    assert len(overview["task_families"]) >= 3
    assert len(api_handbook()) >= 6
    assert len(use_case_catalog()) >= 5
    assert len(environment_profiles()) >= 5
    assert len(cli_guide()) >= 3


def test_markdown_guides_contain_key_sections() -> None:
    intro = render_package_overview_markdown()
    api_md = render_api_handbook_markdown()
    use_md = render_use_cases_markdown()
    assert "# What tscfbench is" in intro
    assert "## Task families" in intro
    assert "# API handbook" in api_md
    assert "Why this API exists" in api_md
    assert "# Use cases" in use_md
    assert "agent" in use_md.lower()
