from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from tscfbench.csv_runner import run_csv_impact
from tscfbench.demo_cases import demo_data_path, run_demo
from tscfbench.visuals import _prepare_post_intervention_visuals


def test_v181_post_intervention_payload_masks_pre_counterfactual() -> None:
    payload = _prepare_post_intervention_visuals(
        t=["t0", "t1", "t2", "t3"],
        y_obs=np.asarray([10.0, 11.0, 14.0, 15.0]),
        y_cf=np.asarray([10.5, 10.5, 11.5, 11.0]),
        intervention_index=2,
        y_cf_lower=np.asarray([9.5, 9.5, 10.5, 10.0]),
        y_cf_upper=np.asarray([11.5, 11.5, 12.5, 12.0]),
    )
    assert np.isnan(payload["y_cf_masked"][:2]).all()
    assert np.isnan(payload["point_effect_masked"][:2]).all()
    assert np.isnan(payload["cumulative_effect_masked"][:2]).all()
    assert np.isfinite(payload["y_obs"]).all()
    assert payload["post_t"] == ["t2", "t3"]
    np.testing.assert_allclose(payload["cumulative_effect_post"], np.asarray([2.5, 6.5]))


def test_v181_prediction_frame_effects_start_at_intervention(tmp_path: Path) -> None:
    payload = run_csv_impact(
        demo_data_path("heatwave-health"),
        time_col="date",
        y_col="er_visits",
        x_cols=["nearby_city_er", "temperature_proxy"],
        intervention_t="2024-07-14",
        output_dir=tmp_path / "impact_demo",
        plot=False,
    )
    frame = pd.read_csv(payload["generated_files"]["prediction_csv"])
    intervention = pd.Timestamp(payload["summary"]["intervention_t"])
    pre = pd.to_datetime(frame["t"]) < intervention
    assert frame.loc[pre, "effect"].isna().all()
    assert frame.loc[pre, "cumulative_effect"].isna().all()
    assert {"effect_lower", "effect_upper", "cumulative_effect_lower", "cumulative_effect_upper"} <= set(frame.columns)


def test_v181_demo_outputs_include_point_effect_assets(tmp_path: Path) -> None:
    payload = run_demo("repo-breakout", output_dir=tmp_path, plot=True)
    generated = payload["generated_files"]
    assert Path(generated["point_effect_png"]).exists()
    assert Path(generated["point_effect_svg"]).exists()
