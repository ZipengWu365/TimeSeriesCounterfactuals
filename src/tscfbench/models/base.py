from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class CounterfactualModel(ABC):
    """Common fit_predict interface for counterfactual estimators."""

    name: str = "base"

    @abstractmethod
    def fit_predict(self, case: Any):
        """Fit on the pre period and return counterfactual predictions for all t."""

    def _ensure_1d(self, x: np.ndarray) -> np.ndarray:
        return np.asarray(x, dtype=float).reshape(-1)
