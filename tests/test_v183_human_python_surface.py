from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from tscfbench import load_demo_data, run_impact_data, run_panel_data

ROOT = Path(__file__).resolve().parents[1]


def test_v183_load_demo_data_returns_frame() -> None:
    df = load_demo_data("city-traffic")
    assert not df.empty
    assert {"city", "date", "traffic_index"} <= set(df.columns)


def test_v183_run_panel_data_accepts_dataframe(tmp_path: Path) -> None:
    periods = pd.date_range("2024-01-01", periods=18, freq="D")
    rows = []
    for unit, offset in [("A", 0.0), ("B", -1.0), ("C", 1.5)]:
        for idx, date in enumerate(periods):
            value = 100 + idx * 0.6 + offset
            if unit == "A" and idx >= 12:
                value += 8
            rows.append({"unit": unit, "date": date.strftime("%Y-%m-%d"), "outcome": value})
    df = pd.DataFrame(rows)

    payload = run_panel_data(
        df,
        unit_col="unit",
        time_col="date",
        y_col="outcome",
        treated_unit="A",
        intervention_t="2024-01-13",
        output_dir=tmp_path / "panel_run",
        min_pre_periods=6,
        max_time_placebos=3,
        plot=False,
        data_name="toy_panel",
    )

    assert payload["kind"] == "panel_data_run"
    assert payload["data_name"] == "toy_panel"
    assert (tmp_path / "panel_run" / "panel_report.md").exists()
    assert payload["summary"]["treated_unit"] == "A"


def test_v183_run_impact_data_accepts_dataframe(tmp_path: Path) -> None:
    periods = pd.date_range("2024-04-01", periods=24, freq="D")
    peer = np.linspace(100, 123, len(periods))
    search = np.linspace(50, 62, len(periods))
    effect = np.where(np.arange(len(periods)) >= 16, 12.0, 0.0)
    signups = 0.7 * peer + 0.8 * search + effect
    df = pd.DataFrame(
        {
            "date": periods.strftime("%Y-%m-%d"),
            "signups": signups,
            "peer_signups": peer,
            "search_interest": search,
        }
    )

    payload = run_impact_data(
        df,
        time_col="date",
        y_col="signups",
        x_cols=["peer_signups", "search_interest"],
        intervention_t="2024-04-17",
        output_dir=tmp_path / "impact_run",
        plot=False,
        data_name="toy_impact",
    )

    assert payload["kind"] == "impact_data_run"
    assert payload["data_name"] == "toy_impact"
    assert (tmp_path / "impact_run" / "impact_report.md").exists()
    assert payload["summary"]["controls"] == 2


def test_v183_docs_lead_with_python_examples() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    docs_home = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    own_data = (ROOT / "docs" / "bring-your-own-data.md").read_text(encoding="utf-8")

    assert "## Python-first quickstart" in readme
    assert "from tscfbench import run_panel_data" in readme
    assert "## Start in Python" in docs_home
    assert "from tscfbench import run_demo" in docs_home
    assert "run_panel_data" in own_data
    assert "run_impact_data" in own_data
