from __future__ import annotations

import copy
import importlib
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from tscfbench.core import ImpactCase, PanelCase, PredictionResult
from tscfbench.models.base import CounterfactualModel


class OptionalDependencyError(ImportError):
    pass


def _require_module(import_names: Iterable[str], install_hint: str) -> Any:
    last_error: Optional[Exception] = None
    for name in import_names:
        try:
            return importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise OptionalDependencyError(f"Missing optional dependency. Install with: {install_hint}") from last_error


def _require_attr(import_names: Iterable[str], attr: str, install_hint: str) -> Any:
    last_error: Optional[Exception] = None
    for name in import_names:
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, attr):
                return getattr(mod, attr)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise OptionalDependencyError(f"Could not import {attr!r}. Install with: {install_hint}") from last_error


def _filter_kwargs(fn: Any, kwargs: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        sig = inspect.signature(fn)
    except Exception:  # noqa: BLE001
        return dict(kwargs)
    accepts_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    if accepts_var_kw:
        return {k: v for k, v in kwargs.items() if v is not None}
    return {k: v for k, v in kwargs.items() if k in sig.parameters and v is not None}


def _call_with_supported_kwargs(fn: Any, *args: Any, **kwargs: Any) -> Any:
    return fn(*args, **_filter_kwargs(fn, kwargs))


_ALIAS_MAP: Dict[str, Sequence[str]] = {
    "data": ["data", "df", "foo"],
    "predictors": ["predictors"],
    "predictors_op": ["predictors_op"],
    "dependent": ["dependent", "outcome", "outcome_var"],
    "unit_variable": ["unit_variable", "unit_var", "id_var"],
    "time_variable": ["time_variable", "time_var"],
    "treatment_identifier": ["treatment_identifier", "unit_tr", "treated_unit", "treatment_unit"],
    "controls_identifier": ["controls_identifier", "unit_co", "control_units", "donor_units"],
    "time_predictors_prior": ["time_predictors_prior", "predictor_time", "period_predictors"],
    "time_optimize_ssr": ["time_optimize_ssr", "optimization_time", "period_pre"],
    "time_plot": ["time_plot", "period_plot", "time_periods"],
    "special_predictors": ["special_predictors"],
}


def _kwargs_from_aliases(callable_obj: Any, canonical_kwargs: Mapping[str, Any]) -> Dict[str, Any]:
    try:
        sig = inspect.signature(callable_obj)
        param_names = set(sig.parameters)
        accepts_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    except Exception:  # noqa: BLE001
        param_names = set()
        accepts_var_kw = True

    out: Dict[str, Any] = {}
    for canon, value in canonical_kwargs.items():
        aliases = _ALIAS_MAP.get(canon, [canon])
        for alias in aliases:
            if accepts_var_kw or alias in param_names:
                if value is not None:
                    out[alias] = value
                break
    return out


def _first_attr(obj: Any, names: Sequence[str]) -> Any:
    for name in names:
        if isinstance(obj, Mapping) and name in obj:
            return obj[name]
        if hasattr(obj, name):
            return getattr(obj, name)
    return None


def _collect_frames(obj: Any, max_depth: int = 3) -> List[pd.DataFrame]:
    frames: List[pd.DataFrame] = []
    seen: set[int] = set()

    def rec(x: Any, depth: int) -> None:
        if depth < 0:
            return
        xid = id(x)
        if xid in seen:
            return
        seen.add(xid)
        if x is None:
            return
        if isinstance(x, pd.DataFrame):
            frames.append(x)
            return
        if isinstance(x, pd.Series):
            frames.append(x.to_frame())
            return
        if isinstance(x, Mapping):
            for v in x.values():
                rec(v, depth - 1)
            return
        if isinstance(x, (list, tuple)):
            for v in x:
                rec(v, depth - 1)
            return
        if hasattr(x, "__dict__"):
            for v in vars(x).values():
                rec(v, depth - 1)

    rec(obj, max_depth)
    return frames


_MEAN_CANDIDATES = [
    "point_pred",
    "preds",
    "predicted",
    "predicted_mean",
    "prediction",
    "mean",
    "counterfactual",
    "synthetic",
    "y_cf_mean",
]
_LOWER_CANDIDATES = ["point_pred_lower", "predicted_lower", "lower", "low", "lo", "lb", "y_cf_lower"]
_UPPER_CANDIDATES = ["point_pred_upper", "predicted_upper", "upper", "high", "hi", "ub", "y_cf_upper"]


def _match_column(columns: Sequence[str], candidates: Sequence[str]) -> Optional[str]:
    lower_map = {str(c).lower(): str(c) for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    for col in columns:
        col_l = str(col).lower()
        for cand in candidates:
            if cand.lower() in col_l:
                return str(col)
    return None


def _find_prediction_frame(obj: Any, *, min_rows: int = 1) -> Optional[pd.DataFrame]:
    frames = _collect_frames(obj, max_depth=4)
    best: Optional[pd.DataFrame] = None
    best_score = -1.0
    for df in frames:
        if len(df) < min_rows:
            continue
        cols = [str(c) for c in df.columns]
        score = 0.0
        if _match_column(cols, _MEAN_CANDIDATES):
            score += 3.0
        if _match_column(cols, _LOWER_CANDIDATES):
            score += 1.0
        if _match_column(cols, _UPPER_CANDIDATES):
            score += 1.0
        numeric_cols = int(df.select_dtypes(include=[np.number]).shape[1])
        score += min(numeric_cols, 3) * 0.1
        if score > best_score:
            best = df
            best_score = score
    return best


def _coerce_array(x: Any) -> np.ndarray:
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 1:
            return x.iloc[:, 0].to_numpy(dtype=float)
        return x.to_numpy(dtype=float).reshape(-1)
    if isinstance(x, pd.Series):
        return x.to_numpy(dtype=float)
    return np.asarray(x, dtype=float).reshape(-1)


def _extract_prediction_columns(df: pd.DataFrame, *, horizon: Optional[int] = None, model_hint: Optional[str] = None) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    cols = [str(c) for c in df.columns]

    mean_col = None
    if model_hint and model_hint in cols:
        mean_col = model_hint
    if mean_col is None:
        mean_col = _match_column(cols, _MEAN_CANDIDATES)
    if mean_col is None:
        blacklist = {"t", "time", "ds", "date", "unique_id", "id", "unit"}
        numeric = [c for c in cols if c.lower() not in blacklist and pd.api.types.is_numeric_dtype(df[c])]
        if not numeric:
            raise ValueError(f"Could not infer prediction column from columns: {cols}")
        mean_col = numeric[0]

    lower_col = _match_column(cols, _LOWER_CANDIDATES)
    upper_col = _match_column(cols, _UPPER_CANDIDATES)

    if model_hint:
        hint_l = model_hint.lower()
        for c in cols:
            cl = c.lower()
            if lower_col is None and hint_l in cl and any(tag in cl for tag in ["lo", "lower", "lb"]):
                lower_col = c
            if upper_col is None and hint_l in cl and any(tag in cl for tag in ["hi", "upper", "ub"]):
                upper_col = c

    mean = df[mean_col].to_numpy(dtype=float)
    lower = df[lower_col].to_numpy(dtype=float) if lower_col else None
    upper = df[upper_col].to_numpy(dtype=float) if upper_col else None
    if horizon is not None:
        mean = mean[-horizon:]
        if lower is not None:
            lower = lower[-horizon:]
        if upper is not None:
            upper = upper[-horizon:]
    return mean, lower, upper


def _align_weight_series(weights: Any, control_units: Sequence[Any]) -> np.ndarray:
    if weights is None:
        raise ValueError("No weights found on fitted external model")
    if isinstance(weights, pd.DataFrame):
        numeric = weights.select_dtypes(include=[np.number])
        if numeric.empty:
            raise ValueError("Weights dataframe did not contain numeric columns")
        if numeric.shape[1] == 1:
            weights = numeric.iloc[:, 0]
        else:
            weights = pd.Series(numeric.iloc[:, 0].to_numpy(), index=weights.index)
    if isinstance(weights, pd.Series):
        controls_list = list(control_units)
        if set(controls_list).issubset(set(weights.index)):
            return np.asarray([float(weights.loc[idx]) for idx in controls_list], dtype=float)
        index_str = [str(i) for i in weights.index]
        controls_str = [str(u) for u in controls_list]
        if set(controls_str).issubset(set(index_str)):
            lookup = {str(idx): float(val) for idx, val in weights.items()}
            return np.asarray([lookup[idx] for idx in controls_str], dtype=float)
        if len(weights) == len(control_units):
            return weights.to_numpy(dtype=float)
        raise ValueError(f"Could not align weight index {list(weights.index)} to control units {list(control_units)}")
    arr = np.asarray(weights, dtype=float).reshape(-1)
    if arr.size != len(control_units):
        raise ValueError(f"Weight vector has length {arr.size}; expected {len(control_units)}")
    return arr


def _extract_weights_from_obj(obj: Any, control_units: Sequence[Any]) -> np.ndarray:
    candidates = [
        _first_attr(obj, ["weights", "weights_", "w", "W", "w_hat", "solution"]),
    ]
    if hasattr(obj, "weights") and callable(getattr(obj, "weights")):
        try:
            candidates.insert(0, _call_with_supported_kwargs(getattr(obj, "weights"), round=10, threshold=None))
        except Exception:  # noqa: BLE001
            try:
                candidates.insert(0, getattr(obj, "weights")())
            except Exception:  # noqa: BLE001
                pass
    for cand in candidates:
        if cand is None:
            continue
        if hasattr(cand, "w"):
            cand = getattr(cand, "w")
        try:
            return _align_weight_series(cand, control_units)
        except Exception:  # noqa: BLE001
            continue
    raise ValueError("Could not extract donor weights from fitted object")


def _series_payload(case: Any, use_controls: bool = True) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray], np.ndarray, np.ndarray]:
    if isinstance(case, ImpactCase):
        y = case.y_obs
        X = case.X if use_controls and case.X.size else None
        x_pre = X[case.pre_mask] if X is not None else None
        x_post = X[case.post_mask] if X is not None else None
        return np.asarray(case.t), y, x_pre, x_post, case.pre_mask, case.post_mask
    if isinstance(case, PanelCase):
        return np.asarray(case.times), case.treated_series(), None, None, case.pre_mask, case.post_mask
    raise TypeError("Expected ImpactCase or PanelCase")


def _impact_periods(case: ImpactCase) -> Tuple[List[Any], List[Any]]:
    return [case.t[0], case.t[case.intervention_index - 1]], [case.t[case.intervention_index], case.t[-1]]


def _prepend_pre_period(
    y_pre: np.ndarray,
    y_post_cf: np.ndarray,
    *,
    strategy: str = "repeat_observed",
    lower_post: Optional[np.ndarray] = None,
    upper_post: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    if strategy == "repeat_observed":
        pre = y_pre.copy()
        lower_pre = pre.copy() if lower_post is not None else None
        upper_pre = pre.copy() if upper_post is not None else None
    elif strategy == "pre_mean":
        pre = np.full_like(y_pre, float(np.nanmean(y_pre)))
        lower_pre = pre.copy() if lower_post is not None else None
        upper_pre = pre.copy() if upper_post is not None else None
    else:
        raise ValueError(f"Unknown pre strategy: {strategy}")

    mean = np.concatenate([pre, np.asarray(y_post_cf, dtype=float)], axis=0)
    lower = np.concatenate([lower_pre, np.asarray(lower_post, dtype=float)], axis=0) if lower_post is not None else None
    upper = np.concatenate([upper_pre, np.asarray(upper_post, dtype=float)], axis=0) if upper_post is not None else None
    return mean, lower, upper


@dataclass
class MetadataOnlyAdapter(CounterfactualModel):
    name: str = "metadata_only_adapter"
    install_hint: str = "pip install <package>"
    message: str = "This adapter is intentionally metadata-only."

    def fit_predict(self, case: Any) -> PredictionResult:
        raise OptionalDependencyError(f"{self.message} Install/use via: {self.install_hint}")


@dataclass
class GenericForecastCounterfactualAdapter(CounterfactualModel):
    estimator: Any = None
    name: str = "generic_forecast_cf"
    use_controls: bool = False
    pre_strategy: str = "repeat_observed"
    clone_estimator: bool = True
    fit_kwargs: Dict[str, Any] = field(default_factory=dict)
    predict_kwargs: Dict[str, Any] = field(default_factory=dict)

    def _clone(self) -> Any:
        if self.estimator is None:
            raise ValueError("GenericForecastCounterfactualAdapter requires an estimator instance")
        return copy.deepcopy(self.estimator) if self.clone_estimator else self.estimator

    def _fit(self, est: Any, y_pre: np.ndarray, x_pre: Optional[np.ndarray]) -> None:
        kwargs = dict(self.fit_kwargs)
        if x_pre is not None:
            kwargs.setdefault("X", x_pre)
        for attempt in [
            lambda: est.fit(y_pre, **kwargs),
            lambda: est.fit(y=y_pre, **kwargs),
            lambda: est.fit(pd.Series(y_pre), **kwargs),
        ]:
            try:
                attempt()
                return
            except TypeError:
                continue
        raise TypeError("Wrapped estimator does not support a recognized fit signature")

    def _predict(self, est: Any, horizon: int, x_post: Optional[np.ndarray]) -> np.ndarray:
        kwargs = dict(self.predict_kwargs)
        if x_post is not None:
            kwargs.setdefault("X", x_post)
        try:
            pred = est.predict(horizon, **kwargs)
        except TypeError:
            pred = est.predict(n=horizon, **kwargs)
        pred = _coerce_array(pred)
        if len(pred) != horizon:
            raise ValueError(f"Wrapped estimator returned {len(pred)} predictions; expected {horizon}")
        return pred

    def fit_predict(self, case: Any) -> PredictionResult:
        _, y, x_pre, x_post, pre_mask, post_mask = _series_payload(case, use_controls=self.use_controls)
        y_pre = np.asarray(y[pre_mask], dtype=float)
        horizon = int(np.sum(post_mask))
        est = self._clone()
        self._fit(est, y_pre, x_pre)
        y_post_cf = self._predict(est, horizon, x_post)
        mean, _, _ = _prepend_pre_period(y_pre, y_post_cf, strategy=self.pre_strategy)
        return PredictionResult(
            y_cf_mean=mean,
            meta={
                "backend": getattr(est, "__class__", type(est)).__name__,
                "adapter": self.name,
                "use_controls": self.use_controls,
            },
        )


@dataclass
class PysynconPanelAdapter(CounterfactualModel):
    method: str = "synth"
    fit_options: Dict[str, Any] = field(default_factory=dict)
    pre_strategy: str = "repeat_observed"
    name: str = "pysyncon_adapter"

    def _study_class(self, mod: ModuleType) -> Any:
        name_map = {
            "synth": ["Synth"],
            "augsynth": ["AugSynth"],
            "robust": ["RobustSynth", "RobustSCM", "RobustSynthControl"],
            "penalized": ["PenSynth", "PenalizedSynth", "PenalizedSCM"],
        }
        for name in name_map.get(self.method.lower(), [self.method]):
            if hasattr(mod, name):
                return getattr(mod, name)
        raise OptionalDependencyError(f"pysyncon does not expose a class for method={self.method!r}")

    def _build_dataprep(self, mod: ModuleType, case: PanelCase) -> Any:
        if not hasattr(mod, "Dataprep"):
            raise OptionalDependencyError("pysyncon does not expose Dataprep")
        Dataprep = getattr(mod, "Dataprep")
        control_units = [u for u in case.units if u != case.treated_unit]
        canonical = {
            "data": case.df.copy(),
            "predictors": [case.y_col],
            "predictors_op": "mean",
            "dependent": case.y_col,
            "unit_variable": case.unit_col,
            "time_variable": case.time_col,
            "treatment_identifier": case.treated_unit,
            "controls_identifier": control_units,
            "time_predictors_prior": list(case.times[case.pre_mask]),
            "time_optimize_ssr": list(case.times[case.pre_mask]),
            "time_plot": list(case.times),
            "special_predictors": None,
        }
        kwargs = _kwargs_from_aliases(Dataprep, canonical)
        return Dataprep(**kwargs)

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, PanelCase):
            raise TypeError("PysynconPanelAdapter expects a PanelCase")
        mod = _require_module(["pysyncon"], install_hint="pip install pysyncon")
        dataprep = self._build_dataprep(mod, case)
        StudyCls = self._study_class(mod)
        study = StudyCls()
        _call_with_supported_kwargs(study.fit, dataprep, **self.fit_options)

        X_controls, control_units = case.control_matrix()
        weights = _extract_weights_from_obj(study, control_units)
        y_cf = X_controls @ weights
        return PredictionResult(
            y_cf_mean=np.asarray(y_cf, dtype=float),
            meta={
                "backend": "pysyncon",
                "method": self.method,
                "weights": weights,
                "control_units": control_units,
                "adapter": self.name,
            },
        )


@dataclass
class SCPIAdapter(CounterfactualModel):
    w_constr: Dict[str, Any] = field(default_factory=lambda: {"name": "simplex"})
    constant: bool = True
    cointegrated_data: bool = True
    compute_intervals: bool = False
    scpi_options: Dict[str, Any] = field(default_factory=dict)
    name: str = "scpi_adapter"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, PanelCase):
            raise TypeError("SCPIAdapter expects a PanelCase")

        scdata = _require_attr(["scpi_pkg.scdata", "scpi.scdata"], "scdata", "pip install scpi_pkg")
        scest = _require_attr(["scpi_pkg.scest", "scpi.scest"], "scest", "pip install scpi_pkg")
        scpi_fn = None
        if self.compute_intervals:
            try:
                scpi_fn = _require_attr(["scpi_pkg.scpi", "scpi.scpi"], "scpi", "pip install scpi_pkg")
            except Exception:  # noqa: BLE001
                scpi_fn = None

        control_units = [u for u in case.units if u != case.treated_unit]
        prep = _call_with_supported_kwargs(
            scdata,
            df=case.df.copy(),
            id_var=case.unit_col,
            time_var=case.time_col,
            outcome_var=case.y_col,
            period_pre=np.asarray(case.times[case.pre_mask]),
            period_post=np.asarray(case.times[case.post_mask]),
            unit_tr=case.treated_unit,
            unit_co=control_units,
            constant=self.constant,
            cointegrated_data=self.cointegrated_data,
        )
        est = _call_with_supported_kwargs(scest, prep, w_constr=self.w_constr)
        X_controls, _ = case.control_matrix()
        weights = _extract_weights_from_obj(est, control_units)
        y_cf = X_controls @ weights

        lower = upper = None
        if scpi_fn is not None:
            try:
                inf = _call_with_supported_kwargs(scpi_fn, est, **self.scpi_options)
                pred_df = _find_prediction_frame(inf, min_rows=max(1, int(case.post_mask.sum())))
                if pred_df is not None:
                    mean_post, lower_post, upper_post = _extract_prediction_columns(pred_df, horizon=int(case.post_mask.sum()))
                    _, lower, upper = _prepend_pre_period(case.treated_series()[case.pre_mask], mean_post, strategy="repeat_observed", lower_post=lower_post, upper_post=upper_post)
            except Exception:  # noqa: BLE001
                lower = upper = None

        return PredictionResult(
            y_cf_mean=np.asarray(y_cf, dtype=float),
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={
                "backend": "scpi_pkg",
                "weights": weights,
                "control_units": control_units,
                "w_constr": dict(self.w_constr),
                "adapter": self.name,
            },
        )


@dataclass
class SyntheticControlMethodsAdapter(CounterfactualModel):
    pen: float = 0.0
    name: str = "synthetic_control_methods_adapter"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, PanelCase):
            raise TypeError("SyntheticControlMethodsAdapter expects a PanelCase")
        mod = _require_module(["SyntheticControlMethods"], install_hint="pip install SyntheticControlMethods")
        if not hasattr(mod, "Synth"):
            raise OptionalDependencyError("SyntheticControlMethods does not expose Synth")
        Synth = getattr(mod, "Synth")
        study = Synth(case.df.copy(), case.y_col, case.unit_col, case.time_col, case.intervention_t, case.treated_unit, pen=self.pen)

        pred_df = _find_prediction_frame(study, min_rows=len(case.times))
        if pred_df is None:
            raise ValueError("Could not extract a prediction dataframe from SyntheticControlMethods result")
        mean, lower, upper = _extract_prediction_columns(pred_df, horizon=len(case.times))
        return PredictionResult(
            y_cf_mean=mean,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"backend": "SyntheticControlMethods", "adapter": self.name, "pen": self.pen},
        )


@dataclass
class CausalPyAdapter(MetadataOnlyAdapter):
    name: str = "causalpy_adapter"
    install_hint: str = "pip install CausalPy"
    message: str = "CausalPy remains study-planning oriented in v0.6; its experiment-specific wrappers are not normalized yet."


@dataclass
class CImpactAdapter(CounterfactualModel):
    model_config: Dict[str, Any] = field(
        default_factory=lambda: {
            "model_type": "tensorflow",
            "model_args": {"standardize": True, "fit_method": "vi", "num_variational_steps": 200},
        }
    )
    name: str = "cimpact_adapter"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, ImpactCase):
            raise TypeError("CImpactAdapter expects an ImpactCase")
        mod = _require_module(["cimpact"], install_hint="pip install cimpact")
        if not hasattr(mod, "CausalImpactAnalysis"):
            raise OptionalDependencyError("cimpact does not expose CausalImpactAnalysis")
        Analysis = getattr(mod, "CausalImpactAnalysis")

        df = case.df[[case.time_col, case.y_col] + list(case.x_cols)].copy()
        pre_period, post_period = _impact_periods(case)
        analysis = Analysis(
            df,
            pre_period,
            post_period,
            self.model_config,
            case.time_col,
            case.y_col,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        result = analysis.run_analysis()
        pred_df = _find_prediction_frame(result, min_rows=len(case.df)) or _find_prediction_frame(analysis, min_rows=len(case.df))
        if pred_df is None:
            raise ValueError("Could not extract a prediction dataframe from CImpact result")
        mean, lower, upper = _extract_prediction_columns(pred_df, horizon=len(case.df))
        return PredictionResult(
            y_cf_mean=mean,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"backend": "cimpact", "adapter": self.name, "model_config": self.model_config},
        )


@dataclass
class StatsForecastCounterfactualAdapter(CounterfactualModel):
    model_name: str = "AutoARIMA"
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {"season_length": 1})
    freq: Any = None
    levels: Optional[List[int]] = field(default_factory=lambda: [95])
    use_controls: bool = True
    pre_strategy: str = "repeat_observed"
    unique_id: str = "treated"
    name: str = "statsforecast_cf"

    def _infer_freq(self, t: np.ndarray) -> Any:
        if self.freq is not None:
            return self.freq
        if np.issubdtype(np.asarray(t).dtype, np.datetime64):
            return "D"
        return 1

    def _make_train_df(self, t: np.ndarray, y: np.ndarray, X: Optional[np.ndarray], cols: Optional[Sequence[str]]) -> pd.DataFrame:
        df = pd.DataFrame({"unique_id": self.unique_id, "ds": t, "y": y})
        if X is not None and cols is not None:
            for j, c in enumerate(cols):
                df[str(c)] = X[:, j]
        return df

    def fit_predict(self, case: Any) -> PredictionResult:
        mod = _require_module(["statsforecast"], install_hint="pip install statsforecast")
        models_mod = _require_module(["statsforecast.models"], install_hint="pip install statsforecast")
        if not hasattr(mod, "StatsForecast"):
            raise OptionalDependencyError("statsforecast does not expose StatsForecast")
        if not hasattr(models_mod, self.model_name):
            raise OptionalDependencyError(f"statsforecast.models does not expose {self.model_name}")
        StatsForecast = getattr(mod, "StatsForecast")
        ModelCls = getattr(models_mod, self.model_name)

        t, y, x_pre, x_post, pre_mask, post_mask = _series_payload(case, use_controls=self.use_controls)
        y_pre = y[pre_mask]
        t_pre = t[pre_mask]
        t_post = t[post_mask]
        cols = list(getattr(case, "x_cols", [])) if isinstance(case, ImpactCase) and self.use_controls else None
        train_df = self._make_train_df(t_pre, y_pre, x_pre, cols)
        future_df = None
        if x_post is not None and cols is not None:
            future_df = pd.DataFrame({"unique_id": self.unique_id, "ds": t_post})
            for j, c in enumerate(cols):
                future_df[str(c)] = x_post[:, j]

        model = ModelCls(**_filter_kwargs(ModelCls, self.model_kwargs))
        sf = StatsForecast(models=[model], freq=self._infer_freq(t), n_jobs=1)
        if hasattr(sf, "forecast"):
            pred_df = _call_with_supported_kwargs(sf.forecast, df=train_df, h=int(np.sum(post_mask)), X_df=future_df, level=self.levels)
        else:
            _call_with_supported_kwargs(sf.fit, train_df)
            pred_df = _call_with_supported_kwargs(sf.predict, h=int(np.sum(post_mask)), X_df=future_df, level=self.levels)
        pred_df = pd.DataFrame(pred_df)
        mean_post, lower_post, upper_post = _extract_prediction_columns(pred_df, horizon=int(np.sum(post_mask)), model_hint=self.model_name)
        mean, lower, upper = _prepend_pre_period(y_pre, mean_post, strategy=self.pre_strategy, lower_post=lower_post, upper_post=upper_post)
        return PredictionResult(
            y_cf_mean=mean,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"backend": "statsforecast", "adapter": self.name, "model_name": self.model_name, "use_controls": self.use_controls},
        )


@dataclass
class DartsForecastAdapter(CounterfactualModel):
    model_name: str = "ExponentialSmoothing"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    use_controls: bool = False
    covariate_kind: str = "future_covariates"
    num_samples: int = 1
    quantiles: Tuple[float, float] = (0.025, 0.975)
    pre_strategy: str = "repeat_observed"
    name: str = "darts_forecast_cf"

    def _series_to_array(self, obj: Any) -> np.ndarray:
        if hasattr(obj, "pd_dataframe"):
            return obj.pd_dataframe().iloc[:, 0].to_numpy(dtype=float)
        if hasattr(obj, "values") and callable(getattr(obj, "values")):
            vals = obj.values()
            return np.asarray(vals, dtype=float).reshape(-1)
        if hasattr(obj, "univariate_values"):
            return np.asarray(obj.univariate_values(), dtype=float).reshape(-1)
        return _coerce_array(obj)

    def fit_predict(self, case: Any) -> PredictionResult:
        darts_mod = _require_module(["darts"], install_hint="pip install darts")
        models_mod = _require_module(["darts.models"], install_hint="pip install darts")
        if not hasattr(darts_mod, "TimeSeries"):
            raise OptionalDependencyError("darts does not expose TimeSeries")
        if not hasattr(models_mod, self.model_name):
            raise OptionalDependencyError(f"darts.models does not expose {self.model_name}")
        TimeSeries = getattr(darts_mod, "TimeSeries")
        ModelCls = getattr(models_mod, self.model_name)

        t, y, x_pre, x_post, pre_mask, post_mask = _series_payload(case, use_controls=self.use_controls)
        y_pre = y[pre_mask]
        t_pre = t[pre_mask]
        t_all = t
        h = int(np.sum(post_mask))

        target_train_df = pd.DataFrame({"t": t_pre, "y": y_pre})
        series_train = TimeSeries.from_dataframe(target_train_df, "t", "y")
        covariates = None
        cov_kwargs: Dict[str, Any] = {}
        if self.use_controls and isinstance(case, ImpactCase) and case.X.size:
            cov_df = pd.DataFrame({"t": t_all})
            for j, c in enumerate(case.x_cols):
                cov_df[str(c)] = case.X[:, j]
            covariates = TimeSeries.from_dataframe(cov_df, "t", list(case.x_cols))
            cov_kwargs[self.covariate_kind] = covariates

        model = ModelCls(**_filter_kwargs(ModelCls, self.model_kwargs))
        _call_with_supported_kwargs(model.fit, series_train, **cov_kwargs)
        pred_obj = _call_with_supported_kwargs(model.predict, n=h, num_samples=self.num_samples, **cov_kwargs)
        mean_post = self._series_to_array(pred_obj)

        lower_post = upper_post = None
        if self.num_samples > 1 and hasattr(pred_obj, "quantile_timeseries"):
            try:
                lower_ts = pred_obj.quantile_timeseries(self.quantiles[0])
                upper_ts = pred_obj.quantile_timeseries(self.quantiles[1])
                lower_post = self._series_to_array(lower_ts)
                upper_post = self._series_to_array(upper_ts)
            except Exception:  # noqa: BLE001
                lower_post = upper_post = None

        mean, lower, upper = _prepend_pre_period(y_pre, mean_post, strategy=self.pre_strategy, lower_post=lower_post, upper_post=upper_post)
        return PredictionResult(
            y_cf_mean=mean,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"backend": "darts", "adapter": self.name, "model_name": self.model_name, "use_controls": self.use_controls},
        )


__all__ = [
    "CImpactAdapter",
    "CausalPyAdapter",
    "DartsForecastAdapter",
    "GenericForecastCounterfactualAdapter",
    "MetadataOnlyAdapter",
    "OptionalDependencyError",
    "PysynconPanelAdapter",
    "SCPIAdapter",
    "StatsForecastCounterfactualAdapter",
    "SyntheticControlMethodsAdapter",
    "_extract_prediction_columns",
    "_find_prediction_frame",
    "_require_module",
]
