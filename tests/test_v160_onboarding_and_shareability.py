from __future__ import annotations

import json
from pathlib import Path

from tscfbench.csv_runner import run_csv_impact
from tscfbench.demo_cases import demo_data_path
from tscfbench.onramp import doctor_report
from tscfbench.share_packages import make_share_package_for_demo


def test_v160_doctor_uses_starter_path() -> None:
    rep = doctor_report()
    commands = rep["safe_first_run"]["commands"]
    assert commands[0] == 'python -m pip install -e ".[starter]"'
    assert "release_asset" in rep["recommended_installs"]


def test_v160_repo_breakout_summary_has_no_null_metrics(tmp_path: Path) -> None:
    payload = run_csv_impact(
        demo_data_path("repo-breakout"),
        time_col="date",
        y_col="repo_stars_new",
        x_cols=["peer_repo_a", "peer_repo_b"],
        intervention_t="2025-12-18",
        output_dir=tmp_path / "repo_breakout",
        plot=False,
        title="Repo breakout after a launch",
    )
    summary = payload["summary"]
    assert summary["cum_effect"] > 0
    assert summary["post_period_points"] > 0
    assert summary["controls"] == 2
    assert all(value is not None for value in summary.values())


def test_v160_share_package_writes_summary_json_and_non_null_summary(tmp_path: Path) -> None:
    payload = make_share_package_for_demo("repo-breakout", output_dir=tmp_path / "share_pkg", plot=False)
    share_manifest = payload["share_manifest"]
    summary = payload["summary"]
    assert summary["cum_effect"] > 0
    assert Path(share_manifest["summary_json_path"]).exists()
    loaded = json.loads(Path(share_manifest["summary_json_path"]).read_text(encoding="utf-8"))
    assert loaded["summary_metrics"]["cum_effect"] > 0
    assert "headline_result" in loaded and loaded["headline_result"]


def test_v160_readme_mentions_release_asset_install() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "README.md").read_text(encoding="utf-8")
    assert 'python -m pip install -e ".[starter]"' in text
    assert 'python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib' in text
