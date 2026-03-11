from __future__ import annotations

from pathlib import Path

from tscfbench.positioning import (
    ecosystem_audit,
    feature_coverage_matrix,
    package_differentiators,
    render_agent_first_design_markdown,
    render_differentiators_markdown,
    render_docs_homepage_markdown,
    render_ecosystem_audit_markdown,
    render_feature_coverage_markdown,
    render_github_readme_markdown,
    write_positioning_assets,
)


def test_v120_positioning_catalogs_are_populated() -> None:
    audit = ecosystem_audit()
    assert audit["name"] == "tscfbench ecosystem audit"
    assert len(audit["peers"]) >= 8
    assert any(peer["id"] == "pysyncon" for peer in audit["peers"])
    assert any(peer["id"] == "tfp_causalimpact" for peer in audit["peers"])
    assert len(feature_coverage_matrix()) >= 6
    assert len(package_differentiators()) >= 4



def test_v120_positioning_markdown_has_key_sections() -> None:
    assert "# Ecosystem audit" in render_ecosystem_audit_markdown()
    assert "# Feature coverage matrix" in render_feature_coverage_markdown()
    assert "# Why tscfbench is different" in render_differentiators_markdown()
    assert "# tscfbench (v1.8.0)" in render_github_readme_markdown()
    assert "# Agent-first design" in render_agent_first_design_markdown()
    assert "# tscfbench" in render_docs_homepage_markdown()



def test_v120_positioning_assets_are_written(tmp_path: Path) -> None:
    manifest = write_positioning_assets(tmp_path)
    assert manifest["kind"] == "positioning_assets"
    assert (tmp_path / "README_GITHUB.md").exists()
    assert (tmp_path / "ECOSYSTEM_AUDIT.md").exists()
    assert (tmp_path / "FEATURE_COVERAGE.md").exists()
