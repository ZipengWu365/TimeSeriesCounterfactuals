from __future__ import annotations

from tscfbench.guidebook import (
    benchmark_cards,
    recommend_start_path,
    render_benchmark_cards_markdown,
    render_start_here_markdown,
    render_workflow_recipes_markdown,
    workflow_recipes,
)


def test_v090_guidebook_catalogs_are_populated() -> None:
    assert len(workflow_recipes()) >= 6
    assert len(benchmark_cards()) >= 5


def test_v090_recommend_path_prefers_custom_panel_recipe() -> None:
    payload = recommend_start_path(persona="applied researcher", task_family="panel", environment="notebook", goal="own data")
    assert payload["primary_recipe"]["id"] == "custom-panel-data"
    assert any("custom_panel_data" in nb or "custom_panel" in nb for nb in payload["recommended_notebooks"])


def test_v090_markdown_surfaces_have_key_sections() -> None:
    start_md = render_start_here_markdown()
    recipes_md = render_workflow_recipes_markdown()
    cards_md = render_benchmark_cards_markdown()
    assert "# Start here" in start_md
    assert "## Common first paths" in start_md
    assert "# Workflow recipes" in recipes_md
    assert "# Benchmark cards" in cards_md
