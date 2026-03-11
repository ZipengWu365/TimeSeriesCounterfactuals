from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from tscfbench.bench import benchmark
from tscfbench.core import PanelCase, PredictionResult
from tscfbench.metrics import effect_summary, post_pre_rmspe_ratio, regression_metrics, rmspe
from tscfbench.models.base import CounterfactualModel


@dataclass(frozen=True)
class PanelProtocolConfig:
    """Research-style evaluation protocol for single-treated panel designs."""

    run_space_placebo: bool = True
    run_time_placebo: bool = True
    placebo_pre_rmspe_factor: float = 5.0
    min_pre_periods: int = 8
    time_placebo_step: int = 1
    max_time_placebos: Optional[int] = 10


@dataclass
class PanelBenchmarkOutput:
    prediction: PredictionResult
    metrics: Dict[str, float]
    space_placebos: pd.DataFrame = field(default_factory=pd.DataFrame)
    time_placebos: pd.DataFrame = field(default_factory=pd.DataFrame)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _clone_model(model: CounterfactualModel) -> CounterfactualModel:
    return copy.deepcopy(model)


def _safe_fit_predict(model: CounterfactualModel, case: PanelCase) -> PredictionResult:
    mdl = _clone_model(model)
    return mdl.fit_predict(case)


def _space_placebos(case: PanelCase, model: CounterfactualModel, treated_pre_rmspe: float, factor: float) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for unit in case.units:
        if unit == case.treated_unit:
            continue
        placebo_case = case.with_treated_unit(unit)
        try:
            pred = _safe_fit_predict(model, placebo_case)
            y_obs = placebo_case.treated_series()
            fit = post_pre_rmspe_ratio(y_obs, pred.y_cf_mean, placebo_case.pre_mask, placebo_case.post_mask)
            eff = effect_summary(y_obs, pred.y_cf_mean, placebo_case.post_mask)
            row = {"unit": unit, "eligible": True, **fit, **eff}
        except Exception as exc:  # noqa: BLE001
            row = {
                "unit": unit,
                "eligible": False,
                "error": str(exc),
                "pre_rmspe": np.nan,
                "post_rmspe": np.nan,
                "post_pre_rmspe_ratio": np.nan,
                "avg_effect": np.nan,
                "avg_abs_effect": np.nan,
                "cum_effect": np.nan,
                "max_abs_effect": np.nan,
            }
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    threshold = factor * max(treated_pre_rmspe, 1e-12)
    valid = np.isfinite(df["pre_rmspe"]) & np.isfinite(df["post_pre_rmspe_ratio"])
    df["eligible"] = df["eligible"].fillna(True) & valid & (df["pre_rmspe"] <= threshold)
    df["eligible_threshold"] = threshold
    return df.sort_values("post_pre_rmspe_ratio", ascending=False, na_position="last").reset_index(drop=True)


def _time_placebos(
    case: PanelCase,
    model: CounterfactualModel,
    min_pre_periods: int,
    step: int,
    max_time_placebos: Optional[int],
) -> pd.DataFrame:
    real_post_len = int(case.post_mask.sum())
    total_t = len(case.times)

    candidate_indices = []
    for idx in range(min_pre_periods, case.intervention_index, max(step, 1)):
        if idx + real_post_len <= total_t:
            candidate_indices.append(idx)

    if max_time_placebos is not None and len(candidate_indices) > max_time_placebos:
        # keep evenly spread candidates for reproducibility
        take = np.linspace(0, len(candidate_indices) - 1, num=max_time_placebos)
        candidate_indices = [candidate_indices[int(round(i))] for i in take]
        candidate_indices = sorted(set(candidate_indices))

    rows: List[Dict[str, Any]] = []
    y_obs = case.treated_series()

    for idx in candidate_indices:
        pseudo_t = case.times[idx]
        pseudo_case = case.with_intervention_t(pseudo_t)
        try:
            pred = _safe_fit_predict(model, pseudo_case)
            pre_mask = np.zeros(total_t, dtype=bool)
            pre_mask[:idx] = True
            post_mask = np.zeros(total_t, dtype=bool)
            post_mask[idx:idx + real_post_len] = True

            fit = post_pre_rmspe_ratio(y_obs, pred.y_cf_mean, pre_mask, post_mask)
            eff = effect_summary(y_obs, pred.y_cf_mean, post_mask)
            row = {
                "pseudo_intervention_t": pseudo_t,
                "pseudo_intervention_index": idx,
                "pseudo_post_length": real_post_len,
                **fit,
                **eff,
            }
        except Exception as exc:  # noqa: BLE001
            row = {
                "pseudo_intervention_t": pseudo_t,
                "pseudo_intervention_index": idx,
                "pseudo_post_length": real_post_len,
                "error": str(exc),
                "pre_rmspe": np.nan,
                "post_rmspe": np.nan,
                "post_pre_rmspe_ratio": np.nan,
                "avg_effect": np.nan,
                "avg_abs_effect": np.nan,
                "cum_effect": np.nan,
                "max_abs_effect": np.nan,
            }
        rows.append(row)

    return pd.DataFrame(rows).sort_values("pseudo_intervention_index").reset_index(drop=True)


def benchmark_panel(
    case: PanelCase,
    model: CounterfactualModel,
    config: Optional[PanelProtocolConfig] = None,
) -> PanelBenchmarkOutput:
    """Run a research-oriented benchmark for a single-treated panel case."""

    if config is None:
        config = PanelProtocolConfig()

    pred = model.fit_predict(case)
    y_obs = case.treated_series()

    metrics: Dict[str, float] = {}
    fit = post_pre_rmspe_ratio(y_obs, pred.y_cf_mean, case.pre_mask, case.post_mask)
    eff = effect_summary(y_obs, pred.y_cf_mean, case.post_mask)
    metrics.update(fit)
    metrics.update(eff)
    metrics["n_units"] = float(len(case.units))
    metrics["n_periods"] = float(len(case.times))
    metrics["pre_periods"] = float(case.pre_mask.sum())
    metrics["post_periods"] = float(case.post_mask.sum())

    if case.y_cf_true is not None:
        metrics.update({
            f"truth_{k}": v
            for k, v in regression_metrics(case.y_cf_true[case.post_mask], pred.y_cf_mean[case.post_mask]).items()
        })
        true_eff = effect_summary(case.treated_series(), case.y_cf_true, case.post_mask)
        metrics.update({f"truth_{k}": v for k, v in true_eff.items()})

    space_df = pd.DataFrame()
    time_df = pd.DataFrame()

    if config.run_space_placebo:
        space_df = _space_placebos(
            case=case,
            model=model,
            treated_pre_rmspe=metrics["pre_rmspe"],
            factor=config.placebo_pre_rmspe_factor,
        )
        eligible = space_df[space_df.get("eligible", False)].copy()
        treated_ratio = metrics["post_pre_rmspe_ratio"]
        if not eligible.empty:
            ge = int(np.sum(eligible["post_pre_rmspe_ratio"].to_numpy(dtype=float) >= treated_ratio))
            metrics["space_placebo_pvalue"] = float((ge + 1) / (len(eligible) + 1))
            metrics["space_placebo_eligible_controls"] = float(len(eligible))
            metrics["space_placebo_rank"] = float(ge + 1)
        else:
            metrics["space_placebo_pvalue"] = float("nan")
            metrics["space_placebo_eligible_controls"] = 0.0
            metrics["space_placebo_rank"] = float("nan")

    if config.run_time_placebo:
        time_df = _time_placebos(
            case=case,
            model=model,
            min_pre_periods=config.min_pre_periods,
            step=config.time_placebo_step,
            max_time_placebos=config.max_time_placebos,
        )
        if not time_df.empty:
            treated_abs = abs(metrics["cum_effect"])
            time_abs = np.abs(time_df["cum_effect"].to_numpy(dtype=float))
            metrics["time_placebo_pvalue"] = float((np.sum(time_abs >= treated_abs) + 1) / (len(time_abs) + 1))
            metrics["time_placebo_count"] = float(len(time_df))
        else:
            metrics["time_placebo_pvalue"] = float("nan")
            metrics["time_placebo_count"] = 0.0

    return PanelBenchmarkOutput(
        prediction=pred,
        metrics=metrics,
        space_placebos=space_df,
        time_placebos=time_df,
        metadata={
            "protocol": config,
            "treated_unit": case.treated_unit,
            "intervention_t": case.intervention_t,
            "model_name": getattr(model, "name", model.__class__.__name__),
        },
    )
