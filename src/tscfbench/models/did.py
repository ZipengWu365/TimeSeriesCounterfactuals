from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist
from typing import Any

import numpy as np

from tscfbench.core import PanelCase, PredictionResult
from tscfbench.models.base import CounterfactualModel


@dataclass
class DifferenceInDifferences(CounterfactualModel):
    """Simple panel DiD baseline with one treated unit and averaged controls."""

    alpha: float = 0.05
    name: str = "did"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, PanelCase):
            raise TypeError("DifferenceInDifferences expects a PanelCase")

        y_treated = case.treated_series()
        X_controls, control_units = case.control_matrix()
        control_mean = np.nanmean(X_controls, axis=1)

        pre = case.pre_mask
        treated_pre_mean = float(np.nanmean(y_treated[pre]))
        control_pre_mean = float(np.nanmean(control_mean[pre]))
        shifts = control_mean - control_pre_mean
        y_cf = treated_pre_mean + shifts

        resid = y_treated[pre] - y_cf[pre]
        sigma = float(np.sqrt(np.nanmean(resid**2)))
        z = float(NormalDist().inv_cdf(1 - self.alpha / 2))
        lower = y_cf - z * sigma
        upper = y_cf + z * sigma

        return PredictionResult(
            y_cf_mean=y_cf,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={
                "treated_pre_mean": treated_pre_mean,
                "control_pre_mean": control_pre_mean,
                "sigma": sigma,
                "n_controls": len(control_units),
            },
        )
