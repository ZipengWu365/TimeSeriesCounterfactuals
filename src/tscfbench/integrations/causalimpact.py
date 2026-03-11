from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import pandas as pd

from tscfbench.core import ImpactCase, PredictionResult
from tscfbench.integrations.adapters import (
    OptionalDependencyError,
    _extract_prediction_columns,
    _find_prediction_frame,
    _filter_kwargs,
    _require_module,
)
from tscfbench.models.base import CounterfactualModel


@dataclass
class TFPCausalImpactAdapter(CounterfactualModel):
    """Adapter for modern tfp-causalimpact / causalimpact-style Python APIs.

    It supports both common call styles seen in the ecosystem:
      * `causalimpact.CausalImpact(data, pre_period, post_period, ...)`
      * `causalimpact.fit_causalimpact(data, pre_period=..., post_period=..., ...)`

    The parser is intentionally tolerant because python ports expose slightly
    different result objects and column names.
    """

    inference_options: Optional[Dict[str, Any]] = None
    constructor_kwargs: Dict[str, Any] = field(default_factory=dict)
    name: str = "tfp_causalimpact_adapter"

    def fit_predict(self, case: Any) -> PredictionResult:
        if not isinstance(case, ImpactCase):
            raise TypeError("TFPCausalImpactAdapter expects an ImpactCase")
        if case.intervention_index <= 0:
            raise ValueError("ImpactCase needs at least one pre-treatment observation")

        mod = _require_module(["causalimpact"], install_hint="pip install tfp-causalimpact")
        data = case.df[[case.y_col] + list(case.x_cols)].copy()
        pre_period = [case.t[0], case.t[case.intervention_index - 1]]
        post_period = [case.t[case.intervention_index], case.t[-1]]

        result_obj: Any
        if hasattr(mod, "fit_causalimpact"):
            kwargs = dict(self.constructor_kwargs)
            if self.inference_options is not None and hasattr(mod, "InferenceOptions"):
                InferenceOptions = getattr(mod, "InferenceOptions")
                kwargs.setdefault("inference_options", InferenceOptions(**_filter_kwargs(InferenceOptions, self.inference_options)))
            result_obj = mod.fit_causalimpact(data, pre_period=pre_period, post_period=post_period, **kwargs)
        elif hasattr(mod, "CausalImpact"):
            CausalImpact = getattr(mod, "CausalImpact")
            result_obj = CausalImpact(data, pre_period, post_period, **_filter_kwargs(CausalImpact, self.constructor_kwargs))
        else:
            raise OptionalDependencyError("Installed causalimpact module does not expose fit_causalimpact or CausalImpact")

        pred_df = _find_prediction_frame(result_obj, min_rows=len(case.df))
        if pred_df is None:
            if isinstance(result_obj, pd.DataFrame):
                pred_df = result_obj
            else:
                raise ValueError("Could not locate an inferences/prediction dataframe on the causalimpact result")

        mean, lower, upper = _extract_prediction_columns(pred_df, horizon=len(case.df))
        return PredictionResult(
            y_cf_mean=mean,
            y_cf_lower=lower,
            y_cf_upper=upper,
            meta={"backend": "causalimpact", "adapter": self.name},
        )


__all__ = ["TFPCausalImpactAdapter"]
