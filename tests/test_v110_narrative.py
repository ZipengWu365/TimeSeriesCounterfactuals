from __future__ import annotations

from pathlib import Path

from tscfbench.narrative import (
    api_atlas,
    capability_map,
    package_story,
    render_api_atlas_markdown,
    render_capability_map_markdown,
    render_package_story_markdown,
    render_scenario_matrix_markdown,
    render_tutorial_index_markdown,
    scenario_matrix,
    tutorial_index,
    write_release_kit,
)


def test_v110_narrative_catalogs_are_populated() -> None:
    assert package_story()["name"] == "tscfbench"
    assert len(capability_map()) >= 6
    assert len(scenario_matrix()) >= 4
    assert len(tutorial_index()) >= 4
    atlas = api_atlas()
    assert "package_story" in atlas
    assert "api_handbook" in atlas


def test_v110_narrative_markdown_has_key_sections() -> None:
    assert "# tscfbench" in render_package_story_markdown()
    assert "# Capability map" in render_capability_map_markdown()
    assert "# API atlas" in render_api_atlas_markdown()
    assert "# Scenario matrix" in render_scenario_matrix_markdown()
    assert "# Tutorial index" in render_tutorial_index_markdown()


def test_v110_release_kit_writes_key_files(tmp_path: Path) -> None:
    manifest = write_release_kit(tmp_path)
    assert manifest["kind"] == "release_kit"
    assert (tmp_path / "README_LANDING.md").exists()
    assert (tmp_path / "API_ATLAS.md").exists()
    assert (tmp_path / "SCENARIO_MATRIX.md").exists()
