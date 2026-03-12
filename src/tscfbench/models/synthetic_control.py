from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist
from typing import Any

import numpy as np

from tscfbench.core import PanelCase, PredictionResult
from tscfbench.models.base import CounterfactualModel


def _project_to_simplex(v: np.ndarray) -> np.ndarray:
    """Project a vector onto the simplex {w >= 0, sum w = 1}."""
    v = np.asarray(v, dtype=float).reshape(-1)
    n = v.size
    if n == 0:
        return v

    u = np.sort(v)[::-1]
    cssv = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, n + 1) > (cssv - 1))[0]
    if len(rho) == 0:
        return np.ones(n) / n
    rho = rho[-1]
    theta = (cssv[rho] - 1) / (rho + 1)
    w = np.maximum(v - theta, 0)
    s = w.sum()
    if s <= 0:
        return np.ones(n) / n
    return w / s


@dataclass
class SimpleSyntheticControl(CounterfactualModel):
    """Lightweight SCM baseline using ridge fit + simplex projection."""

    ridge: float = 1e-6
    alpha: float = 0.05
    name: str = "simple_scm"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, PanelCase):
            raise TypeError("SimpleSyntheticControl expects a PanelCase")

        y_treated = case.treated_series()
        X_controls, control_units = case.control_matrix()

        pre = case.pre_mask
        y_pre = y_treated[pre]
        X_pre = X_controls[pre]

        valid = np.isfinite(y_pre) & np.all(np.isfinite(X_pre), axis=1)
        y_pre_v = y_pre[valid]
        X_pre_v = X_pre[valid]
        if X_pre_v.size == 0:
            raise ValueError("No valid pre-period rows after removing NaNs")

        j = X_pre_v.shape[1]
        A = X_pre_v.T @ X_pre_v + self.ridge * np.eye(j)
        b = X_pre_v.T @ y_pre_v
        w_raw = np.linalg.solve(A, b)
        w = _project_to_simplex(w_raw)

        y_cf = X_controls @ w
        resid = y_pre_v - (X_pre_v @ w)
        sigma = float(np.sqrt(np.mean(resid**2))) if len(resid) else 0.0
        z = float(NormalDist().inv_cdf(1 - self.alpha / 2))
        lower = y_cf - z * sigma
        upper = y_cf + z * sigma
        return PredictionResult(
            y_cf_mean=y_cf,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={
                "weights": w,
                "weights_raw": w_raw,
                "control_units": control_units,
                "ridge": self.ridge,
                "sigma": sigma,
                "alpha": self.alpha,
            },
        )
