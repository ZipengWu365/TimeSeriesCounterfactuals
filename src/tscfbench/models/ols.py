from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist
from typing import Any

import numpy as np

from tscfbench.core import ImpactCase, PredictionResult
from tscfbench.models.base import CounterfactualModel


@dataclass
class OLSImpact(CounterfactualModel):
    """Simple impact baseline: y_t ~ intercept + controls + optional trend."""

    ridge: float = 1e-6
    add_trend: bool = False
    alpha: float = 0.05
    name: str = "ols"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, ImpactCase):
            raise TypeError("OLSImpact expects an ImpactCase")

        y = case.y_obs
        X = case.X
        t = case.t.astype(float)

        parts = [np.ones((len(y), 1), dtype=float)]
        if X.shape[1] > 0:
            parts.append(X)
        if self.add_trend:
            parts.append(t.reshape(-1, 1))
        Z = np.concatenate(parts, axis=1)

        pre = case.pre_mask
        Z_pre = Z[pre]
        y_pre = y[pre]

        k = Z_pre.shape[1]
        A = Z_pre.T @ Z_pre + self.ridge * np.eye(k)
        b = Z_pre.T @ y_pre
        beta = np.linalg.solve(A, b)

        y_hat = Z @ beta
        resid = y_pre - (Z_pre @ beta)
        dof = max(len(y_pre) - k, 1)
        sigma = float(np.sqrt(np.sum(resid**2) / dof))

        z = float(NormalDist().inv_cdf(1 - self.alpha / 2))
        lower = y_hat - z * sigma
        upper = y_hat + z * sigma

        return PredictionResult(
            y_cf_mean=y_hat,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"beta": beta, "sigma": sigma, "alpha": self.alpha, "add_trend": self.add_trend},
        )
