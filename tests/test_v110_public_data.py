from __future__ import annotations

import pandas as pd

from tscfbench.datasets import public_data as pdmod
from tscfbench.datasets.public_data import (
    load_coingecko_market_chart,
    load_fred_series,
    load_github_star_history,
    make_event_impact_case,
    to_log_returns,
)


def test_v110_load_github_star_history_aggregates_daily(monkeypatch) -> None:
    payloads = {
        1: [
            {"starred_at": "2026-02-01T01:00:00Z"},
            {"starred_at": "2026-02-01T10:00:00Z"},
            {"starred_at": "2026-02-02T00:00:00Z"},
        ],
        2: [],
    }

    def fake_json_url(url: str, **kwargs):
        page = int(url.split("page=")[-1])
        return payloads[page]

    monkeypatch.setattr(pdmod, "_json_url", fake_json_url)
    df = load_github_star_history("openclaw", "openclaw")
    assert list(df["stars_new"]) == [2, 1]
    assert list(df["stars_cumulative"]) == [2, 3]


def test_v110_load_coingecko_market_chart_merges_series(monkeypatch) -> None:
    def fake_json_url(url: str, **kwargs):
        return {
            "prices": [[1704067200000, 100.0], [1704153600000, 110.0]],
            "market_caps": [[1704067200000, 1000.0], [1704153600000, 1200.0]],
            "total_volumes": [[1704067200000, 50.0], [1704153600000, 70.0]],
        }

    monkeypatch.setattr(pdmod, "_json_url", fake_json_url)
    df = load_coingecko_market_chart("bitcoin", days=2)
    assert list(df.columns) == ["date", "price", "market_cap", "total_volume"]
    assert len(df) == 2


def test_v110_load_fred_series_normalizes_columns(monkeypatch) -> None:
    def fake_csv_url(url: str, **kwargs):
        return pd.DataFrame({"DATE": ["2026-01-01", "2026-01-02"], "VALUE": ["1.0", "."]})

    monkeypatch.setattr(pdmod, "_csv_url", fake_csv_url)
    df = load_fred_series("DCOILWTICO")
    assert list(df.columns) == ["date", "value"]
    assert len(df) == 2
    assert pd.isna(df.loc[1, "value"])


def test_v110_make_event_impact_case_builds_shared_schema() -> None:
    outcome = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=4), "value": [10.0, 11.0, 13.0, 12.0]})
    ctrl_a = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=4), "value": [9.0, 9.5, 10.0, 10.5]})
    ctrl_b = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=4), "value": [8.0, 8.2, 8.1, 8.4]})
    case = make_event_impact_case(outcome, {"a": ctrl_a, "b": ctrl_b}, intervention_t="2026-01-03")
    assert case.y_col == "y"
    assert case.x_cols == ["a", "b"]
    assert case.intervention_index == 2

    ret_df = to_log_returns(outcome)
    assert "log_return" in ret_df.columns
