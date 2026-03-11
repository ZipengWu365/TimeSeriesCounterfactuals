import importlib.machinery
import sys
import types

import numpy as np
import pandas as pd

from tscfbench.bench import benchmark
from tscfbench.datasets.synthetic import make_arma_impact, make_panel_latent_factor
from tscfbench.integrations import TFPCausalImpactAdapter
from tscfbench.integrations.adapters import (
    DartsForecastAdapter,
    PysynconPanelAdapter,
    SCPIAdapter,
    StatsForecastCounterfactualAdapter,
    SyntheticControlMethodsAdapter,
)


def _install_module(monkeypatch, name: str, module: types.ModuleType, *, is_package: bool = False) -> None:
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, is_package=is_package)
    if is_package:
        module.__path__ = []  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, name, module)


def test_tfp_causalimpact_adapter_with_fake_module(monkeypatch):
    causalimpact = types.ModuleType("causalimpact")

    def fit_causalimpact(data, pre_period=None, post_period=None, **kwargs):
        n = len(data)
        mean = np.linspace(0.0, 1.0, n)
        return types.SimpleNamespace(
            inferences=pd.DataFrame(
                {
                    "point_pred": mean,
                    "point_pred_lower": mean - 0.1,
                    "point_pred_upper": mean + 0.1,
                }
            )
        )

    causalimpact.fit_causalimpact = fit_causalimpact
    _install_module(monkeypatch, "causalimpact", causalimpact)

    case = make_arma_impact(T=60, intervention_t=40, seed=2)
    out = benchmark(case, TFPCausalImpactAdapter())
    assert "rmse" in out.metrics
    assert len(out.prediction.y_cf_mean) == len(case.t)
    assert out.prediction.y_cf_lower is not None
    assert out.prediction.y_cf_upper is not None


def test_pysyncon_adapter_with_fake_module(monkeypatch):
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
            w = np.repeat(1.0 / len(controls), len(controls))
            return pd.Series(w, index=controls)

    pysyncon.Dataprep = Dataprep
    pysyncon.Synth = Synth
    _install_module(monkeypatch, "pysyncon", pysyncon)

    case = make_panel_latent_factor(T=50, N=6, intervention_t=30, seed=3)
    pred = PysynconPanelAdapter().fit_predict(case)
    assert pred.y_cf_mean.shape[0] == len(case.times)
    assert len(pred.meta["control_units"]) == len(case.units) - 1
    assert len(pred.meta["weights"]) == len(case.units) - 1


def test_scpi_adapter_with_fake_modules(monkeypatch):
    pkg = types.ModuleType("scpi_pkg")
    _install_module(monkeypatch, "scpi_pkg", pkg, is_package=True)

    mod_scdata = types.ModuleType("scpi_pkg.scdata")
    mod_scest = types.ModuleType("scpi_pkg.scest")
    mod_scpi = types.ModuleType("scpi_pkg.scpi")

    def scdata(**kwargs):
        return kwargs

    class FakeEst:
        def __init__(self, prep):
            self.prep = prep

        def weights(self, **kwargs):
            controls = self.prep["unit_co"]
            w = np.repeat(1.0 / len(controls), len(controls))
            return pd.Series(w, index=controls)

    def scest(prep, w_constr=None):
        return FakeEst(prep)

    def scpi(est, **kwargs):
        h = len(est.prep["period_post"])
        mean = np.repeat(0.0, h)
        return types.SimpleNamespace(
            pred_df=pd.DataFrame({"mean": mean, "lower": mean - 0.2, "upper": mean + 0.2})
        )

    mod_scdata.scdata = scdata
    mod_scest.scest = scest
    mod_scpi.scpi = scpi
    _install_module(monkeypatch, "scpi_pkg.scdata", mod_scdata)
    _install_module(monkeypatch, "scpi_pkg.scest", mod_scest)
    _install_module(monkeypatch, "scpi_pkg.scpi", mod_scpi)

    case = make_panel_latent_factor(T=60, N=7, intervention_t=35, seed=4)
    pred = SCPIAdapter(compute_intervals=True).fit_predict(case)
    assert pred.y_cf_mean.shape[0] == len(case.times)
    assert pred.y_cf_lower is not None
    assert pred.y_cf_upper is not None


def test_synthetic_control_methods_adapter_with_fake_module(monkeypatch):
    scm_mod = types.ModuleType("SyntheticControlMethods")

    class Synth:
        def __init__(self, data, outcome, unit, time, treatment_time, treated_unit, pen=0.0):
            self.predictions = pd.DataFrame({"synthetic": np.linspace(0.0, 1.0, len(data[data[unit] == treated_unit]))})

    scm_mod.Synth = Synth
    _install_module(monkeypatch, "SyntheticControlMethods", scm_mod)

    case = make_panel_latent_factor(T=40, N=5, intervention_t=25, seed=5)
    pred = SyntheticControlMethodsAdapter().fit_predict(case)
    assert pred.y_cf_mean.shape[0] == len(case.times)


def test_statsforecast_adapter_with_fake_modules(monkeypatch):
    statsforecast = types.ModuleType("statsforecast")
    models = types.ModuleType("statsforecast.models")

    class AutoARIMA:
        def __init__(self, season_length=1):
            self.season_length = season_length

    class StatsForecast:
        def __init__(self, models, freq, n_jobs=1):
            self.models = models
            self.freq = freq
            self.n_jobs = n_jobs

        def forecast(self, df, h, X_df=None, level=None):
            mean = np.repeat(float(df["y"].mean()), h)
            return pd.DataFrame(
                {
                    "unique_id": [df["unique_id"].iloc[0]] * h,
                    "ds": np.arange(h),
                    "AutoARIMA": mean,
                    "AutoARIMA-lo-95": mean - 0.5,
                    "AutoARIMA-hi-95": mean + 0.5,
                }
            )

    statsforecast.StatsForecast = StatsForecast
    models.AutoARIMA = AutoARIMA
    _install_module(monkeypatch, "statsforecast", statsforecast, is_package=True)
    _install_module(monkeypatch, "statsforecast.models", models)

    case = make_arma_impact(T=70, intervention_t=45, seed=6)
    pred = StatsForecastCounterfactualAdapter(model_name="AutoARIMA", use_controls=True).fit_predict(case)
    assert pred.y_cf_mean.shape[0] == len(case.t)
    assert pred.y_cf_lower is not None
    assert pred.y_cf_upper is not None


def test_darts_adapter_with_fake_modules(monkeypatch):
    darts = types.ModuleType("darts")
    models = types.ModuleType("darts.models")

    class FakeTS:
        def __init__(self, df):
            self._df = df.reset_index(drop=True)

        @classmethod
        def from_dataframe(cls, df, time_col, value_cols):
            cols = [value_cols] if isinstance(value_cols, str) else list(value_cols)
            return cls(df[[time_col] + cols].copy())

        def pd_dataframe(self):
            value_cols = [c for c in self._df.columns if c != self._df.columns[0]]
            return self._df[value_cols]

        def values(self):
            value_cols = [c for c in self._df.columns if c != self._df.columns[0]]
            return self._df[value_cols].to_numpy()

        def quantile_timeseries(self, q):
            arr = self.values().reshape(-1)
            delta = 0.3 if q < 0.5 else 0.7
            df = pd.DataFrame({"t": np.arange(len(arr)), "y": arr + delta})
            return FakeTS(df)

    class ExponentialSmoothing:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.last = 0.0

        def fit(self, series, **kwargs):
            vals = series.values().reshape(-1)
            self.last = float(vals[-1])
            return self

        def predict(self, n, num_samples=1, **kwargs):
            df = pd.DataFrame({"t": np.arange(n), "y": np.repeat(self.last, n)})
            return FakeTS(df)

    darts.TimeSeries = FakeTS
    models.ExponentialSmoothing = ExponentialSmoothing
    _install_module(monkeypatch, "darts", darts, is_package=True)
    _install_module(monkeypatch, "darts.models", models)

    case = make_arma_impact(T=80, intervention_t=50, seed=7)
    pred = DartsForecastAdapter(model_name="ExponentialSmoothing", num_samples=3, use_controls=False).fit_predict(case)
    assert pred.y_cf_mean.shape[0] == len(case.t)
    assert pred.y_cf_lower is not None
    assert pred.y_cf_upper is not None
