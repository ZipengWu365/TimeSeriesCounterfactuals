from __future__ import annotations

from tscfbench.showcases import (
    high_traffic_cases,
    public_data_sources,
    render_high_traffic_cases_markdown,
    render_public_data_sources_markdown,
)


def test_v110_showcase_catalogs_have_expected_cases() -> None:
    case_ids = {card["id"] for card in high_traffic_cases()}
    assert "openclaw_stars" in case_ids
    assert "crypto_event_impact" in case_ids
    assert "gold_oil_shocks" in case_ids

    source_ids = {card["id"] for card in public_data_sources()}
    assert "github_stars_api" in source_ids
    assert "coingecko_market_chart" in source_ids
    assert "fred_series" in source_ids


def test_v110_showcase_markdown_has_key_sections() -> None:
    cases_md = render_high_traffic_cases_markdown()
    sources_md = render_public_data_sources_markdown()
    assert "# High-traffic public cases" in cases_md
    assert "OpenClaw GitHub stars" in cases_md
    assert "# Public data sources for high-attention case studies" in sources_md
