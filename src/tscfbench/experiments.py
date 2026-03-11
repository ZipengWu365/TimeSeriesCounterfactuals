from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Union

from tscfbench.core import ImpactCase, PanelCase
from tscfbench.datasets import load_named_dataset
from tscfbench.datasets.synthetic import make_arma_impact, make_panel_latent_factor
from tscfbench.model_zoo import materialize_model
from tscfbench.protocols import PanelBenchmarkOutput, PanelProtocolConfig, benchmark_panel


@dataclass(frozen=True)
class PanelExperimentSpec:
    dataset: str = "synthetic_latent_factor"
    model: str = "simple_scm"
    seed: int = 7
    intervention_t: int = 70
    n_units: int = 12
    n_periods: int = 120
    placebo_pre_rmspe_factor: float = 5.0
    min_pre_periods: int = 12
    max_time_placebos: int = 8
    data_source: str = "auto"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)

    def to_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "PanelExperimentSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**payload)


@dataclass(frozen=True)
class ImpactExperimentSpec:
    dataset: str = "synthetic_arma_impact"
    model: str = "ols_impact"
    seed: int = 7
    intervention_t: int = 140
    n_periods: int = 200
    n_controls: int = 2
    effect: float = 5.0
    model_kwargs: Dict[str, Any] = field(default_factory=dict)

    def to_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "ImpactExperimentSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**payload)



def materialize_panel_case(spec: PanelExperimentSpec) -> PanelCase:
    if spec.dataset == "synthetic_latent_factor":
        return make_panel_latent_factor(T=spec.n_periods, N=spec.n_units, intervention_t=spec.intervention_t, seed=spec.seed)
    return load_named_dataset(spec.dataset, source=spec.data_source)



def materialize_impact_case(spec: ImpactExperimentSpec) -> ImpactCase:
    if spec.dataset == "synthetic_arma_impact":
        return make_arma_impact(T=spec.n_periods, intervention_t=spec.intervention_t, n_controls=spec.n_controls, effect=spec.effect, seed=spec.seed)
    raise ValueError(f"Unknown impact dataset: {spec.dataset}")



def materialize_panel_model(spec: PanelExperimentSpec):
    return materialize_model(spec.model, spec.model_kwargs)



def materialize_impact_model(spec: ImpactExperimentSpec):
    return materialize_model(spec.model, spec.model_kwargs)



def run_panel_experiment(spec: PanelExperimentSpec) -> PanelBenchmarkOutput:
    case = materialize_panel_case(spec)
    model = materialize_panel_model(spec)
    config = PanelProtocolConfig(
        run_space_placebo=True,
        run_time_placebo=True,
        placebo_pre_rmspe_factor=spec.placebo_pre_rmspe_factor,
        min_pre_periods=spec.min_pre_periods,
        max_time_placebos=spec.max_time_placebos,
    )
    return benchmark_panel(case, model, config=config)


__all__ = [
    "ImpactExperimentSpec",
    "PanelExperimentSpec",
    "materialize_impact_case",
    "materialize_impact_model",
    "materialize_panel_case",
    "materialize_panel_model",
    "run_panel_experiment",
]
