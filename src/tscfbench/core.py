from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


def _contains_time_value(values: Any, candidate: Any) -> bool:
    arr = np.asarray(values)
    try:
        if pd.api.types.is_datetime64_any_dtype(arr):
            target = pd.Timestamp(candidate)
            mask = pd.to_datetime(arr) == target
            return bool(np.asarray(mask).any())
    except Exception:  # noqa: BLE001
        pass
    try:
        return candidate in set(arr.tolist())
    except Exception:  # noqa: BLE001
        return candidate in list(arr)


def _time_index(values: Any, candidate: Any) -> int:
    arr = np.asarray(values)
    try:
        if pd.api.types.is_datetime64_any_dtype(arr):
            target = pd.Timestamp(candidate)
            mask = pd.to_datetime(arr) == target
            if bool(np.asarray(mask).any()):
                return int(np.flatnonzero(np.asarray(mask))[0])
    except Exception:  # noqa: BLE001
        pass
    try:
        value_list = arr.tolist()
    except Exception:  # noqa: BLE001
        value_list = list(arr)
    if candidate in value_list:
        return int(value_list.index(candidate))
    raise KeyError(candidate)


@dataclass(frozen=True)
class ImpactCase:
    """Single treated time series with optional controls/covariates."""

    df: pd.DataFrame
    time_col: str
    y_col: str
    x_cols: List[str]
    intervention_t: Any
    y_cf_true: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.time_col not in self.df.columns:
            raise ValueError(f"time_col '{self.time_col}' not in df")
        if self.y_col not in self.df.columns:
            raise ValueError(f"y_col '{self.y_col}' not in df")
        missing_x = [c for c in self.x_cols if c not in self.df.columns]
        if missing_x:
            raise ValueError(f"x_cols not in df: {missing_x}")

        object.__setattr__(self, "df", self.df.sort_values(self.time_col).reset_index(drop=True))

        t = self.df[self.time_col].to_numpy()
        if not _contains_time_value(t, self.intervention_t):
            if not (isinstance(self.intervention_t, int) and 0 <= self.intervention_t < len(t)):
                raise ValueError(
                    f"intervention_t={self.intervention_t!r} not present in '{self.time_col}'. "
                    "Provide a time value or an integer position."
                )

        if self.y_cf_true is not None and len(self.y_cf_true) != len(self.df):
            raise ValueError("y_cf_true must have same length as df")

    @property
    def t(self) -> np.ndarray:
        return self.df[self.time_col].to_numpy()

    @property
    def y_obs(self) -> np.ndarray:
        return self.df[self.y_col].to_numpy(dtype=float)

    @property
    def X(self) -> np.ndarray:
        if not self.x_cols:
            return np.empty((len(self.df), 0), dtype=float)
        return self.df[self.x_cols].to_numpy(dtype=float)

    @property
    def intervention_index(self) -> int:
        if isinstance(self.intervention_t, (int, np.integer)):
            try:
                t_values = self.t.tolist()
            except Exception:
                t_values = list(self.t)
            if self.intervention_t not in t_values and 0 <= int(self.intervention_t) < len(self.df):
                return int(self.intervention_t)
        try:
            return _time_index(self.t, self.intervention_t)
        except KeyError:
            assert isinstance(self.intervention_t, (int, np.integer))
            return int(self.intervention_t)

    @property
    def pre_mask(self) -> np.ndarray:
        idx = self.intervention_index
        m = np.zeros(len(self.df), dtype=bool)
        m[:idx] = True
        return m

    @property
    def post_mask(self) -> np.ndarray:
        return ~self.pre_mask

    def with_intervention_t(self, intervention_t: Any) -> "ImpactCase":
        return ImpactCase(
            df=self.df.copy(),
            time_col=self.time_col,
            y_col=self.y_col,
            x_cols=list(self.x_cols),
            intervention_t=intervention_t,
            y_cf_true=self.y_cf_true.copy() if self.y_cf_true is not None else None,
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True)
class PanelCase:
    """Long-format panel with one treated unit and one intervention date."""

    df: pd.DataFrame
    unit_col: str
    time_col: str
    y_col: str
    treated_unit: Any
    intervention_t: Any
    y_cf_true: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for c in [self.unit_col, self.time_col, self.y_col]:
            if c not in self.df.columns:
                raise ValueError(f"column '{c}' not in df")

        if self.treated_unit not in set(self.df[self.unit_col].unique().tolist()):
            raise ValueError(f"treated_unit={self.treated_unit!r} not present in df")

        object.__setattr__(
            self,
            "df",
            self.df.sort_values([self.unit_col, self.time_col]).reset_index(drop=True),
        )

        times = np.sort(self.df[self.time_col].unique())
        if not _contains_time_value(times, self.intervention_t):
            if not (isinstance(self.intervention_t, int) and 0 <= self.intervention_t < len(times)):
                raise ValueError(
                    f"intervention_t={self.intervention_t!r} not present in '{self.time_col}'. "
                    "Provide a time value or an integer position in the unique times."
                )

        if self.y_cf_true is not None and len(self.y_cf_true) != len(times):
            raise ValueError("y_cf_true must have length equal to number of unique times")

    @property
    def times(self) -> np.ndarray:
        return np.sort(self.df[self.time_col].unique())

    @property
    def units(self) -> List[Any]:
        return sorted(self.df[self.unit_col].unique().tolist())

    @property
    def intervention_index(self) -> int:
        try:
            return _time_index(self.times, self.intervention_t)
        except KeyError:
            assert isinstance(self.intervention_t, int)
            return int(self.intervention_t)

    @property
    def pre_mask(self) -> np.ndarray:
        idx = self.intervention_index
        m = np.zeros(len(self.times), dtype=bool)
        m[:idx] = True
        return m

    @property
    def post_mask(self) -> np.ndarray:
        return ~self.pre_mask

    def to_matrix(self) -> Tuple[np.ndarray, List[Any]]:
        pivot = self.df.pivot(index=self.time_col, columns=self.unit_col, values=self.y_col)
        pivot = pivot.reindex(index=self.times)
        units = list(pivot.columns)
        Y = pivot.to_numpy(dtype=float)
        return Y, units

    def is_balanced(self) -> bool:
        Y, _ = self.to_matrix()
        return bool(np.all(np.isfinite(Y)))

    def treated_series(self) -> np.ndarray:
        Y, units = self.to_matrix()
        j = units.index(self.treated_unit)
        return Y[:, j]

    def control_matrix(self) -> Tuple[np.ndarray, List[Any]]:
        Y, units = self.to_matrix()
        j = units.index(self.treated_unit)
        control_units = units[:j] + units[j + 1 :]
        X = np.delete(Y, j, axis=1)
        return X, control_units

    def with_treated_unit(self, treated_unit: Any) -> "PanelCase":
        y_cf_true = None
        if self.y_cf_true is not None and treated_unit == self.treated_unit:
            y_cf_true = self.y_cf_true.copy()
        return PanelCase(
            df=self.df.copy(),
            unit_col=self.unit_col,
            time_col=self.time_col,
            y_col=self.y_col,
            treated_unit=treated_unit,
            intervention_t=self.intervention_t,
            y_cf_true=y_cf_true,
            metadata=dict(self.metadata),
        )

    def with_intervention_t(self, intervention_t: Any) -> "PanelCase":
        return PanelCase(
            df=self.df.copy(),
            unit_col=self.unit_col,
            time_col=self.time_col,
            y_col=self.y_col,
            treated_unit=self.treated_unit,
            intervention_t=intervention_t,
            y_cf_true=self.y_cf_true.copy() if self.y_cf_true is not None else None,
            metadata=dict(self.metadata),
        )

    def subset_units(self, units: Sequence[Any], treated_unit: Optional[Any] = None) -> "PanelCase":
        units_set = set(units)
        if self.treated_unit not in units_set and treated_unit is None:
            raise ValueError("subset_units would drop the treated unit; pass treated_unit explicitly")
        df = self.df[self.df[self.unit_col].isin(units_set)].copy()
        return PanelCase(
            df=df,
            unit_col=self.unit_col,
            time_col=self.time_col,
            y_col=self.y_col,
            treated_unit=self.treated_unit if treated_unit is None else treated_unit,
            intervention_t=self.intervention_t,
            y_cf_true=self.y_cf_true.copy() if self.y_cf_true is not None and (treated_unit is None or treated_unit == self.treated_unit) else None,
            metadata=dict(self.metadata),
        )


@dataclass
class PredictionResult:
    """Counterfactual trajectory for the treated series over all time points."""

    y_cf_mean: np.ndarray
    y_cf_lower: Optional[np.ndarray] = None
    y_cf_upper: Optional[np.ndarray] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def effect(self, y_obs: np.ndarray) -> np.ndarray:
        return np.asarray(y_obs, dtype=float) - np.asarray(self.y_cf_mean, dtype=float)

    def cumulative_effect(self, y_obs: np.ndarray) -> np.ndarray:
        return np.cumsum(self.effect(y_obs))

    def to_frame(self, t: Sequence[Any], y_obs: np.ndarray) -> pd.DataFrame:
        y_obs = np.asarray(y_obs, dtype=float)
        y_cf = np.asarray(self.y_cf_mean, dtype=float)
        df = pd.DataFrame({
            "t": np.asarray(t),
            "y_obs": y_obs,
            "y_cf_mean": y_cf,
            "effect": y_obs - y_cf,
            "cumulative_effect": np.cumsum(y_obs - y_cf),
        })
        if self.y_cf_lower is not None:
            df["y_cf_lower"] = np.asarray(self.y_cf_lower, dtype=float)
        if self.y_cf_upper is not None:
            df["y_cf_upper"] = np.asarray(self.y_cf_upper, dtype=float)
        return df
