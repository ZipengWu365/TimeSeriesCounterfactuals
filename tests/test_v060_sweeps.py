import importlib.machinery
import json
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd

from tscfbench.model_zoo import list_model_ids, materialize_model
from tscfbench.sweeps import SweepMatrixSpec, make_default_sweep_spec, render_sweep_markdown, run_sweep


def _install_module(monkeypatch, name: str, module: types.ModuleType, *, is_package: bool = False) -> None:
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, is_package=is_package)
    if is_package:
        module.__path__ = []  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, name, module)


def _install_fake_external_stack(monkeypatch):
    # causalimpact
    causalimpact = types.ModuleType("causalimpact")
    causalimpact.fit_causalimpact = lambda data, pre_period=None, post_period=None, **kwargs: types.SimpleNamespace(
        inferences=pd.DataFrame({
            "point_pred": np.linspace(0.0, 1.0, len(data)),
            "point_pred_lower": np.linspace(-0.1, 0.9, len(data)),
            "point_pred_upper": np.linspace(0.1, 1.1, len(data)),
        })
    )
    _install_module(monkeypatch, "causalimpact", causalimpact)

    # pysyncon
    pysyncon = types.ModuleType("pysyncon")
    class Dataprep:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
    class Synth:
        def fit(self, dataprep, **kwargs):
            self.dataprep = dataprep
            return self
        def weights(self, **kwargs):
            controls = self.dataprep.kwargs["controls_identifier"]
            return pd.Series(np.repeat(1.0 / len(controls), len(controls)), index=controls)
    pysyncon.Dataprep = Dataprep
    pysyncon.Synth = Synth
    _install_module(monkeypatch, "pysyncon", pysyncon)

    # scpi_pkg
    pkg = types.ModuleType("scpi_pkg")
    _install_module(monkeypatch, "scpi_pkg", pkg, is_package=True)
    mod_scdata = types.ModuleType("scpi_pkg.scdata")
    mod_scest = types.ModuleType("scpi_pkg.scest")
    mod_scpi = types.ModuleType("scpi_pkg.scpi")
    mod_scdata.scdata = lambda **kwargs: kwargs
    class FakeEst:
        def __init__(self, prep):
            self.prep = prep
        def weights(self, **kwargs):
            controls = self.prep["unit_co"]
            return pd.Series(np.repeat(1.0 / len(controls), len(controls)), index=controls)
    mod_scest.scest = lambda prep, w_constr=None: FakeEst(prep)
    mod_scpi.scpi = lambda est, **kwargs: types.SimpleNamespace(pred_df=pd.DataFrame({"mean": np.zeros(len(est.prep["period_post"])), "lower": -0.2, "upper": 0.2}))
    _install_module(monkeypatch, "scpi_pkg.scdata", mod_scdata)
    _install_module(monkeypatch, "scpi_pkg.scest", mod_scest)
    _install_module(monkeypatch, "scpi_pkg.scpi", mod_scpi)

    # SyntheticControlMethods
    scm = types.ModuleType("SyntheticControlMethods")
    class SCMStudy:
        def __init__(self, data, outcome, unit, time, treatment_time, treated_unit, pen=0.0):
            self.predictions = pd.DataFrame({"synthetic": np.linspace(0.0, 1.0, len(data[data[unit] == treated_unit]))})
    scm.Synth = SCMStudy
    _install_module(monkeypatch, "SyntheticControlMethods", scm)

    # statsforecast
    statsforecast = types.ModuleType("statsforecast")
    models = types.ModuleType("statsforecast.models")
    class AutoARIMA:
        def __init__(self, season_length=1):
            self.season_length = season_length
    class StatsForecast:
        def __init__(self, models, freq, n_jobs=1):
            self.models = models
        def forecast(self, df, h, X_df=None, level=None):
            mean = np.repeat(float(df["y"].mean()), h)
            return pd.DataFrame({"unique_id": [df["unique_id"].iloc[0]] * h, "ds": np.arange(h), "AutoARIMA": mean, "AutoARIMA-lo-95": mean - 0.5, "AutoARIMA-hi-95": mean + 0.5})
    statsforecast.StatsForecast = StatsForecast
    models.AutoARIMA = AutoARIMA
    _install_module(monkeypatch, "statsforecast", statsforecast, is_package=True)
    _install_module(monkeypatch, "statsforecast.models", models)

    # darts
    darts = types.ModuleType("darts")
    models_mod = types.ModuleType("darts.models")
    class FakeTS:
        def __init__(self, df):
            self._df = df.reset_index(drop=True)
        @classmethod
        def from_dataframe(cls, df, time_col, value_cols):
            cols = [value_cols] if isinstance(value_cols, str) else list(value_cols)
            return cls(df[[time_col] + cols].copy())
        def pd_dataframe(self):
            return self._df[[c for c in self._df.columns if c != self._df.columns[0]]]
        def values(self):
            return self.pd_dataframe().to_numpy()
        def quantile_timeseries(self, q):
            arr = self.values().reshape(-1)
            delta = 0.3 if q < 0.5 else 0.7
            return FakeTS(pd.DataFrame({"t": np.arange(len(arr)), "y": arr + delta}))
    class ExponentialSmoothing:
        def fit(self, series, **kwargs):
            self.last = float(series.values().reshape(-1)[-1])
            return self
        def predict(self, n, num_samples=1, **kwargs):
            return FakeTS(pd.DataFrame({"t": np.arange(n), "y": np.repeat(self.last, n)}))
    darts.TimeSeries = FakeTS
    models_mod.ExponentialSmoothing = ExponentialSmoothing
    _install_module(monkeypatch, "darts", darts, is_package=True)
    _install_module(monkeypatch, "darts.models", models_mod)


def test_model_zoo_includes_v060_models():
    panel_ids = set(list_model_ids("panel"))
    impact_ids = set(list_model_ids("impact"))
    forecast_ids = set(list_model_ids("forecast_cf"))
    assert {"pysyncon", "scpi", "synthetic_control_methods"}.issubset(panel_ids)
    assert {"tfp_causalimpact", "cimpact"}.issubset(impact_ids)
    assert {"statsforecast_cf", "darts_forecast_cf"}.issubset(forecast_ids)
    assert materialize_model("statsforecast_cf").name == "statsforecast_cf"


def test_default_sweep_no_external_panel_runs():
    spec = make_default_sweep_spec(task_family="panel", include_external=False, seed=11)
    run = run_sweep(spec)
    summary = run.summary()
    assert summary["cells"] == 2
    assert summary["ok"] == 2
    assert summary["errors"] == 0


def test_default_sweep_no_external_impact_runs():
    spec = make_default_sweep_spec(task_family="impact", include_external=False, seed=11)
    run = run_sweep(spec)
    summary = run.summary()
    assert summary["cells"] == 1
    assert summary["ok"] == 1
    assert summary["errors"] == 0


def test_external_sweep_runs_with_fake_modules(monkeypatch, tmp_path: Path):
    _install_fake_external_stack(monkeypatch)

    panel_spec = make_default_sweep_spec(task_family="panel", include_external=True, seed=13)
    panel_run = run_sweep(panel_spec)
    panel_summary = panel_run.summary()
    assert panel_summary["cells"] == 5
    assert panel_summary["ok"] == 5

    impact_spec = make_default_sweep_spec(task_family="impact", include_external=True, seed=13)
    impact_run = run_sweep(impact_spec)
    impact_summary = impact_run.summary()
    assert impact_summary["cells"] == 5
    assert impact_summary["ok"] >= 4

    md = render_sweep_markdown(panel_run)
    assert "Sweep report" in md

    path = tmp_path / "sweep.json"
    panel_spec.to_json(path)
    loaded = SweepMatrixSpec.from_json(path)
    assert len(loaded.cells) == len(panel_spec.cells)
