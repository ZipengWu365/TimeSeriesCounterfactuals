from __future__ import annotations

from typing import Dict, Optional

import numpy as np


def _to_1d(a) -> np.ndarray:
    return np.asarray(a, dtype=float).reshape(-1)


def regression_metrics(y_true, y_pred) -> Dict[str, float]:
    y_true = _to_1d(y_true)
    y_pred = _to_1d(y_pred)
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")

    err = y_pred - y_true
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    denom = np.where(np.abs(y_true) < 1e-12, np.nan, np.abs(y_true))
    mape = float(np.nanmean(np.abs(err) / denom))
    ss_res = float(np.sum(err**2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
    return {"mae": mae, "rmse": rmse, "mape": mape, "r2": r2}


def interval_coverage(y_true, lower, upper) -> Dict[str, float]:
    y_true = _to_1d(y_true)
    lower = _to_1d(lower)
    upper = _to_1d(upper)
    if not (len(y_true) == len(lower) == len(upper)):
        raise ValueError("y_true/lower/upper must have same length")
    covered = (y_true >= lower) & (y_true <= upper)
    coverage = float(np.mean(covered))
    width = float(np.mean(upper - lower))
    return {"coverage": coverage, "avg_width": width}


def cumulative_effect_error(effect_true, effect_pred) -> Dict[str, float]:
    effect_true = _to_1d(effect_true)
    effect_pred = _to_1d(effect_pred)
    if len(effect_true) != len(effect_pred):
        raise ValueError("effect_true and effect_pred must have same length")

    cum_true = np.cumsum(effect_true)
    cum_pred = np.cumsum(effect_pred)
    diff = cum_pred - cum_true
    return {
        "cum_mae": float(np.mean(np.abs(diff))),
        "cum_rmse": float(np.sqrt(np.mean(diff**2))),
        "cum_final_error": float(cum_pred[-1] - cum_true[-1]) if len(diff) else float("nan"),
    }


def rmspe(y_true, y_pred) -> float:
    y_true = _to_1d(y_true)
    y_pred = _to_1d(y_pred)
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")
    err = y_true - y_pred
    return float(np.sqrt(np.mean(err**2)))


def post_pre_rmspe_ratio(y_obs, y_cf, pre_mask, post_mask, eps: float = 1e-12) -> Dict[str, float]:
    y_obs = _to_1d(y_obs)
    y_cf = _to_1d(y_cf)
    pre_mask = np.asarray(pre_mask, dtype=bool)
    post_mask = np.asarray(post_mask, dtype=bool)
    pre = rmspe(y_obs[pre_mask], y_cf[pre_mask])
    post = rmspe(y_obs[post_mask], y_cf[post_mask])
    ratio = float(post / max(pre, eps))
    return {"pre_rmspe": pre, "post_rmspe": post, "post_pre_rmspe_ratio": ratio}


def effect_summary(y_obs, y_cf, mask: Optional[np.ndarray] = None) -> Dict[str, float]:
    y_obs = _to_1d(y_obs)
    y_cf = _to_1d(y_cf)
    if mask is None:
        mask = np.ones_like(y_obs, dtype=bool)
    else:
        mask = np.asarray(mask, dtype=bool)
    eff = y_obs[mask] - y_cf[mask]
    if eff.size == 0:
        return {
            "avg_effect": float("nan"),
            "avg_abs_effect": float("nan"),
            "cum_effect": float("nan"),
            "max_abs_effect": float("nan"),
        }
    return {
        "avg_effect": float(np.mean(eff)),
        "avg_abs_effect": float(np.mean(np.abs(eff))),
        "cum_effect": float(np.sum(eff)),
        "max_abs_effect": float(np.max(np.abs(eff))),
    }
