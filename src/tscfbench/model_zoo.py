from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from tscfbench.integrations.adapters import (
    CImpactAdapter,
    CausalPyAdapter,
    DartsForecastAdapter,
    PysynconPanelAdapter,
    SCPIAdapter,
    StatsForecastCounterfactualAdapter,
    SyntheticControlMethodsAdapter,
)
from tscfbench.integrations.causalimpact import TFPCausalImpactAdapter
from tscfbench.models.did import DifferenceInDifferences
from tscfbench.models.ols import OLSImpact
from tscfbench.models.synthetic_control import SimpleSyntheticControl


ModelFactory = Callable[..., Any]


_MODEL_FACTORIES: Dict[str, ModelFactory] = {
    "simple_scm": SimpleSyntheticControl,
    "simple_scm_builtin": SimpleSyntheticControl,
    "did": DifferenceInDifferences,
    "did_builtin": DifferenceInDifferences,
    "ols_impact": OLSImpact,
    "ols_impact_builtin": OLSImpact,
    "pysyncon": PysynconPanelAdapter,
    "scpi": SCPIAdapter,
    "synthetic_control_methods": SyntheticControlMethodsAdapter,
    "tfp_causalimpact": TFPCausalImpactAdapter,
    "cimpact": CImpactAdapter,
    "darts_forecast_cf": DartsForecastAdapter,
    "statsforecast_cf": StatsForecastCounterfactualAdapter,
    "causalpy": CausalPyAdapter,
}


_TASK_FAMILY: Dict[str, str] = {
    "simple_scm": "panel",
    "simple_scm_builtin": "panel",
    "did": "panel",
    "did_builtin": "panel",
    "ols_impact": "impact",
    "ols_impact_builtin": "impact",
    "pysyncon": "panel",
    "scpi": "panel",
    "synthetic_control_methods": "panel",
    "tfp_causalimpact": "impact",
    "cimpact": "impact",
    "darts_forecast_cf": "forecast_cf",
    "statsforecast_cf": "forecast_cf",
    "causalpy": "quasi_experiment",
}


def list_model_ids(task_family: Optional[str] = None) -> List[str]:
    if task_family is None:
        return sorted(_MODEL_FACTORIES)
    return sorted([k for k, fam in _TASK_FAMILY.items() if fam == task_family])


def get_model_task_family(model_id: str) -> str:
    if model_id not in _TASK_FAMILY:
        raise KeyError(f"Unknown model id: {model_id}")
    return _TASK_FAMILY[model_id]


def materialize_model(model_id: str, model_kwargs: Optional[Dict[str, Any]] = None) -> Any:
    if model_id not in _MODEL_FACTORIES:
        raise KeyError(f"Unknown model id: {model_id}")
    kwargs = dict(model_kwargs or {})
    return _MODEL_FACTORIES[model_id](**kwargs)


__all__ = ["get_model_task_family", "list_model_ids", "materialize_model"]
