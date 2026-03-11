from __future__ import annotations

import numpy as np
import pandas as pd

from tscfbench.core import ImpactCase, PanelCase


def make_arma_impact(
    T: int = 200,
    intervention_t: int = 140,
    n_controls: int = 2,
    effect: float = 5.0,
    beta_scale: float = 1.0,
    ar: float = 0.7,
    noise: float = 1.0,
    seed: int = 0,
) -> ImpactCase:
    """Synthetic impact dataset with known counterfactual truth."""

    rng = np.random.default_rng(seed)
    X = np.zeros((T, n_controls), dtype=float)
    for k in range(n_controls):
        e = rng.normal(scale=1.0, size=T)
        for t in range(1, T):
            X[t, k] = ar * X[t - 1, k] + e[t]

    beta = rng.normal(scale=beta_scale, size=n_controls)
    eps = rng.normal(scale=noise, size=T)
    y_cf = X @ beta + eps

    y_obs = y_cf.copy()
    y_obs[intervention_t:] += effect

    df = pd.DataFrame({"t": np.arange(T, dtype=int), "y": y_obs})
    for k in range(n_controls):
        df[f"x{k+1}"] = X[:, k]

    x_cols = [f"x{k+1}" for k in range(n_controls)]
    return ImpactCase(
        df=df,
        time_col="t",
        y_col="y",
        x_cols=x_cols,
        intervention_t=intervention_t,
        y_cf_true=y_cf,
        metadata={"dataset_id": "synthetic_arma_impact", "seed": seed},
    )


def make_panel_latent_factor(
    T: int = 120,
    N: int = 8,
    intervention_t: int = 70,
    treated_unit: int = 0,
    n_factors: int = 2,
    effect: float = 3.0,
    noise: float = 0.5,
    seed: int = 0,
) -> PanelCase:
    """Low-rank synthetic panel with treated-unit counterfactual truth."""

    rng = np.random.default_rng(seed)

    F = rng.normal(size=(T, n_factors))
    for r in range(n_factors):
        for t in range(1, T):
            F[t, r] = 0.8 * F[t - 1, r] + 0.2 * F[t, r]

    L = rng.normal(size=(N, n_factors))
    Y_cf = F @ L.T + rng.normal(scale=noise, size=(T, N))

    Y_obs = Y_cf.copy()
    Y_obs[intervention_t:, treated_unit] += effect

    rows = []
    for i in range(N):
        for t in range(T):
            rows.append({"unit": i, "t": t, "y": float(Y_obs[t, i])})
    df = pd.DataFrame(rows)

    return PanelCase(
        df=df,
        unit_col="unit",
        time_col="t",
        y_col="y",
        treated_unit=treated_unit,
        intervention_t=intervention_t,
        y_cf_true=Y_cf[:, treated_unit],
        metadata={"dataset_id": "synthetic_latent_factor", "seed": seed},
    )
