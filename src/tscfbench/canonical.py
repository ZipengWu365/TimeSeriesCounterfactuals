from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd

from tscfbench.markdown_utils import dataframe_to_markdown
from tscfbench.datasets import get_dataset_card
from tscfbench.sweeps import SweepMatrixSpec, SweepRun, SweepCellSpec, render_sweep_markdown, run_sweep


@dataclass(frozen=True)
class CanonicalStudy:
    id: str
    title: str
    dataset_id: str
    treated_unit: str
    intervention_t: int
    outcome: str
    default_models: List[str]
    recommended_external_models: List[str] = field(default_factory=list)
    min_pre_periods: int = 10
    max_time_placebos: int = 8
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_CANONICAL_STUDIES: List[CanonicalStudy] = [
    CanonicalStudy(
        id="germany",
        title="German reunification",
        dataset_id="german_reunification",
        treated_unit="West Germany",
        intervention_t=1990,
        outcome="gdp",
        default_models=["simple_scm", "did"],
        recommended_external_models=["pysyncon", "scpi", "synthetic_control_methods"],
        min_pre_periods=12,
        max_time_placebos=10,
        note="Comparative-politics benchmark for a single treated unit after 1990.",
    ),
    CanonicalStudy(
        id="prop99",
        title="California Proposition 99",
        dataset_id="california_prop99",
        treated_unit="California",
        intervention_t=1989,
        outcome="cigsale",
        default_models=["simple_scm", "did"],
        recommended_external_models=["pysyncon", "scpi", "synthetic_control_methods"],
        min_pre_periods=10,
        max_time_placebos=8,
        note="Tobacco-control benchmark with a long pre-treatment panel.",
    ),
    CanonicalStudy(
        id="basque",
        title="Basque Country terrorism",
        dataset_id="basque_country",
        treated_unit="Basque Country (Pais Vasco)",
        intervention_t=1970,
        outcome="gdpcap",
        default_models=["simple_scm", "did"],
        recommended_external_models=["pysyncon", "scpi", "synthetic_control_methods"],
        min_pre_periods=12,
        max_time_placebos=10,
        note="Foundational SCM case study on the economic effects of conflict.",
    ),
]


@dataclass(frozen=True)
class CanonicalBenchmarkSpec:
    schema_version: str = "1.8.0"
    name: str = "canonical_panel_benchmark"
    study_ids: List[str] = field(default_factory=lambda: [s.id for s in _CANONICAL_STUDIES])
    models: Optional[List[str]] = None
    include_external: bool = False
    data_source: str = "auto"
    seed: int = 7
    stop_on_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "CanonicalBenchmarkSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**payload)



def list_canonical_studies() -> List[CanonicalStudy]:
    return list(_CANONICAL_STUDIES)



def get_canonical_study(study_id: str) -> CanonicalStudy:
    for study in _CANONICAL_STUDIES:
        if study.id == study_id:
            return study
    raise KeyError(f"Unknown canonical study id: {study_id}")



def _models_for(study: CanonicalStudy, models: Optional[Sequence[str]], include_external: bool) -> List[str]:
    if models:
        return list(models)
    out = list(study.default_models)
    if include_external:
        out.extend(study.recommended_external_models)
    return out



def make_canonical_sweep_spec(
    *,
    study_ids: Optional[Sequence[str]] = None,
    models: Optional[Sequence[str]] = None,
    include_external: bool = False,
    data_source: str = "auto",
    seed: int = 7,
    stop_on_error: bool = False,
    name: str = "canonical_panel_benchmark",
) -> SweepMatrixSpec:
    ids = list(study_ids) if study_ids is not None else [s.id for s in _CANONICAL_STUDIES]
    cells: List[SweepCellSpec] = []
    for study_id in ids:
        study = get_canonical_study(study_id)
        for model in _models_for(study, models=models, include_external=include_external):
            cells.append(
                SweepCellSpec(
                    task_family="panel",
                    dataset=study.dataset_id,
                    model=model,
                    seed=seed,
                    intervention_t=study.intervention_t,
                    data_source=data_source,
                    min_pre_periods=study.min_pre_periods,
                    max_time_placebos=study.max_time_placebos,
                    notes=study.note,
                )
            )
    return SweepMatrixSpec(schema_version="1.8.0", name=name, cells=cells, stop_on_error=stop_on_error)



def run_canonical_benchmark(spec: CanonicalBenchmarkSpec | SweepMatrixSpec) -> SweepRun:
    if isinstance(spec, CanonicalBenchmarkSpec):
        sweep = make_canonical_sweep_spec(
            study_ids=spec.study_ids,
            models=spec.models,
            include_external=spec.include_external,
            data_source=spec.data_source,
            seed=spec.seed,
            stop_on_error=spec.stop_on_error,
            name=spec.name,
        )
    else:
        sweep = spec
    return run_sweep(sweep)



def render_canonical_markdown(run: SweepRun) -> str:
    lines: List[str] = []
    lines.append(f"# Canonical benchmark report: {run.spec.name}")
    lines.append("")
    summary = run.summary()
    lines.append(f"Cells: {summary['cells']}; ok: {summary['ok']}; skipped: {summary.get('skipped', 0)}; errors: {summary['errors']}")
    if summary.get("data_sources"):
        lines.append(f"Resolved data sources: {', '.join(summary['data_sources'])}")
    lines.append("")
    df = run.to_frame()
    if not df.empty:
        for study in list_canonical_studies():
            sub = df[df["dataset"] == study.dataset_id].copy()
            if sub.empty:
                continue
            lines.append(f"## {study.title}")
            lines.append("")
            card = get_dataset_card(study.dataset_id)
            lines.append(f"- treated unit: `{card.treated_unit}`")
            lines.append(f"- intervention: `{card.intervention_t}`")
            lines.append(f"- outcome: `{study.outcome}`")
            lines.append(f"- note: {study.note}")
            lines.append("")
            show_cols = [c for c in ["model", "data_source", "status", "metric::pre_rmspe", "metric::post_rmspe", "metric::post_pre_rmspe_ratio", "metric::space_placebo_pvalue", "metric::time_placebo_pvalue", "error"] if c in sub.columns]
            lines.append(dataframe_to_markdown(sub[show_cols], index=False))
            lines.append("")
    lines.append("## Sweep appendix")
    lines.append("")
    lines.append(render_sweep_markdown(run))
    lines.append("")
    return "\n".join(lines)



def canonical_install_notes() -> List[Dict[str, Any]]:
    return [
        {"study": "germany", "default_stack": ["simple_scm", "did"], "recommended_stack": ["pysyncon", "scpi"], "note": "Start with built-in baselines, then add inference-oriented external adapters."},
        {"study": "prop99", "default_stack": ["simple_scm", "did"], "recommended_stack": ["pysyncon", "synthetic_control_methods"], "note": "Prop99 is a good first tutorial because the intervention timing is easy to explain."},
        {"study": "basque", "default_stack": ["simple_scm", "did"], "recommended_stack": ["pysyncon", "scpi"], "note": "Basque is ideal for a methods tutorial because it is historically central to SCM."},
    ]


__all__ = [
    "CanonicalBenchmarkSpec",
    "CanonicalStudy",
    "canonical_install_notes",
    "get_canonical_study",
    "list_canonical_studies",
    "make_canonical_sweep_spec",
    "render_canonical_markdown",
    "run_canonical_benchmark",
]
