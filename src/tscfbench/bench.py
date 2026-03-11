from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from tscfbench.core import ImpactCase, PanelCase, PredictionResult
from tscfbench.metrics import cumulative_effect_error, effect_summary, interval_coverage, regression_metrics
from tscfbench.models.base import CounterfactualModel


@dataclass
class BenchmarkOutput:
    prediction: PredictionResult
    metrics: Dict[str, float]


def benchmark(case: Any, model: CounterfactualModel) -> BenchmarkOutput:
    """Generic benchmark for cases that have ground-truth counterfactuals."""

    pred = model.fit_predict(case)
    metrics: Dict[str, float] = {}

    if isinstance(case, ImpactCase):
        y_obs = case.y_obs
        post = case.post_mask
        metrics.update(effect_summary(y_obs, pred.y_cf_mean, post))
        if case.y_cf_true is not None:
            metrics.update(regression_metrics(case.y_cf_true[post], pred.y_cf_mean[post]))
            eff_true = y_obs - case.y_cf_true
            eff_pred = y_obs - pred.y_cf_mean
            metrics.update(cumulative_effect_error(eff_true[post], eff_pred[post]))
            if pred.y_cf_lower is not None and pred.y_cf_upper is not None:
                metrics.update(interval_coverage(case.y_cf_true[post], pred.y_cf_lower[post], pred.y_cf_upper[post]))

    elif isinstance(case, PanelCase):
        y_obs = case.treated_series()
        post = case.post_mask
        metrics.update(effect_summary(y_obs, pred.y_cf_mean, post))
        if case.y_cf_true is not None:
            metrics.update(regression_metrics(case.y_cf_true[post], pred.y_cf_mean[post]))
            eff_true = y_obs - case.y_cf_true
            eff_pred = y_obs - pred.y_cf_mean
            metrics.update(cumulative_effect_error(eff_true[post], eff_pred[post]))
    else:
        raise TypeError("Unsupported case type")

    return BenchmarkOutput(prediction=pred, metrics=metrics)
