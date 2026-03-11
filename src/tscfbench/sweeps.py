from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from tscfbench.markdown_utils import dataframe_to_markdown

from tscfbench.bench import benchmark
from tscfbench.experiments import (
    ImpactExperimentSpec,
    PanelExperimentSpec,
    materialize_impact_case,
    materialize_impact_model,
    materialize_panel_case,
    materialize_panel_model,
)
from tscfbench.integrations.adapters import OptionalDependencyError
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel


@dataclass(frozen=True)
class SweepCellSpec:
    task_family: str
    dataset: str
    model: str
    seed: int = 7
    intervention_t: Optional[int] = None
    n_units: Optional[int] = None
    n_periods: Optional[int] = None
    n_controls: Optional[int] = None
    effect: Optional[float] = None
    placebo_pre_rmspe_factor: float = 5.0
    min_pre_periods: int = 12
    max_time_placebos: int = 8
    data_source: str = "auto"
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SweepMatrixSpec:
    schema_version: str = "1.8.0"
    name: str = "tscfbench_sweep"
    cells: List[SweepCellSpec] = field(default_factory=list)
    stop_on_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "stop_on_error": self.stop_on_error,
            "cells": [c.to_dict() for c in self.cells],
        }

    def to_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "SweepMatrixSpec":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        payload["cells"] = [SweepCellSpec(**c) for c in payload.get("cells", [])]
        return cls(**payload)


@dataclass(frozen=True)
class SweepCellResult:
    cell: SweepCellSpec
    status: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> Dict[str, Any]:
        payload = self.cell.to_dict()
        payload.update({f"metric::{k}": v for k, v in self.metrics.items()})
        payload.update({"status": self.status, "error": self.error, "meta": self.meta})
        return payload


@dataclass
class SweepRun:
    spec: SweepMatrixSpec
    results: List[SweepCellResult]

    def to_frame(self) -> pd.DataFrame:
        rows = [r.to_record() for r in self.results]
        return pd.DataFrame(rows)

    def summary(self) -> Dict[str, Any]:
        df = self.to_frame()
        if df.empty:
            return {"cells": 0, "ok": 0, "skipped": 0, "errors": 0, "status_counts": {}}
        status_counts = df["status"].value_counts(dropna=False).to_dict()
        return {
            "cells": int(len(df)),
            "ok": int(status_counts.get("ok", 0)),
            "skipped": int(status_counts.get("skipped_optional_dependency", 0)),
            "errors": int(sum(v for k, v in status_counts.items() if k not in {"ok", "skipped_optional_dependency"})),
            "status_counts": {str(k): int(v) for k, v in status_counts.items()},
            "models": sorted(df["model"].dropna().astype(str).unique().tolist()),
            "datasets": sorted(df["dataset"].dropna().astype(str).unique().tolist()),
            "data_sources": sorted(df.get("data_source", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
        }

    def best_by_metric(self, metric: str, *, lower_is_better: bool = True) -> pd.DataFrame:
        df = self.to_frame()
        col = f"metric::{metric}"
        if col not in df.columns:
            return pd.DataFrame()
        ok = df[df["status"] == "ok"].copy()
        ok = ok[np.isfinite(pd.to_numeric(ok[col], errors="coerce"))]
        if ok.empty:
            return pd.DataFrame()
        ok[col] = pd.to_numeric(ok[col], errors="coerce")
        ok = ok.sort_values(col, ascending=lower_is_better)
        return ok.groupby(["task_family", "dataset"], as_index=False).head(1).reset_index(drop=True)



def make_default_sweep_spec(*, task_family: str = "panel", include_external: bool = False, seed: int = 7, data_source: str = "auto") -> SweepMatrixSpec:
    task_family = task_family.lower().strip()
    cells: List[SweepCellSpec] = []
    if task_family == "panel":
        models = ["simple_scm", "did"]
        if include_external:
            models += ["pysyncon", "scpi", "synthetic_control_methods"]
        for model in models:
            cells.append(SweepCellSpec(task_family="panel", dataset="synthetic_latent_factor", model=model, seed=seed, intervention_t=70, n_units=12, n_periods=120, data_source=data_source, model_kwargs={}))
    elif task_family == "impact":
        models = ["ols_impact"]
        if include_external:
            models += ["tfp_causalimpact", "cimpact", "statsforecast_cf", "darts_forecast_cf"]
        for model in models:
            kwargs: Dict[str, Any] = {}
            if model == "statsforecast_cf":
                kwargs = {"model_name": "AutoARIMA", "model_kwargs": {"season_length": 1}, "use_controls": True}
            elif model == "darts_forecast_cf":
                kwargs = {"model_name": "ExponentialSmoothing", "use_controls": False}
            cells.append(SweepCellSpec(task_family="impact", dataset="synthetic_arma_impact", model=model, seed=seed, intervention_t=140, n_periods=200, n_controls=2, effect=5.0, data_source=data_source, model_kwargs=kwargs))
    else:
        raise ValueError(f"Unsupported task_family: {task_family}")
    return SweepMatrixSpec(name=f"default_{task_family}_sweep", cells=cells)



def _run_panel_cell(cell: SweepCellSpec) -> SweepCellResult:
    spec = PanelExperimentSpec(
        dataset=cell.dataset,
        model=cell.model,
        seed=cell.seed,
        intervention_t=int(cell.intervention_t if cell.intervention_t is not None else 70),
        n_units=int(cell.n_units if cell.n_units is not None else 12),
        n_periods=int(cell.n_periods if cell.n_periods is not None else 120),
        placebo_pre_rmspe_factor=float(cell.placebo_pre_rmspe_factor),
        min_pre_periods=int(cell.min_pre_periods),
        max_time_placebos=int(cell.max_time_placebos),
        data_source=cell.data_source,
        model_kwargs=dict(cell.model_kwargs),
    )
    case = materialize_panel_case(spec)
    model = materialize_panel_model(spec)
    report = benchmark_panel(
        case,
        model,
        config=PanelProtocolConfig(
            run_space_placebo=True,
            run_time_placebo=True,
            placebo_pre_rmspe_factor=spec.placebo_pre_rmspe_factor,
            min_pre_periods=spec.min_pre_periods,
            max_time_placebos=spec.max_time_placebos,
        ),
    )
    return SweepCellResult(cell=cell, status="ok", metrics=report.metrics, meta={"model_name": report.metadata.get("model_name"), "loaded_data_source": case.metadata.get("data_source")})



def _run_impact_cell(cell: SweepCellSpec) -> SweepCellResult:
    spec = ImpactExperimentSpec(
        dataset=cell.dataset,
        model=cell.model,
        seed=cell.seed,
        intervention_t=int(cell.intervention_t if cell.intervention_t is not None else 140),
        n_periods=int(cell.n_periods if cell.n_periods is not None else 200),
        n_controls=int(cell.n_controls if cell.n_controls is not None else 2),
        effect=float(cell.effect if cell.effect is not None else 5.0),
        model_kwargs=dict(cell.model_kwargs),
    )
    case = materialize_impact_case(spec)
    model = materialize_impact_model(spec)
    out = benchmark(case, model)
    return SweepCellResult(cell=cell, status="ok", metrics=out.metrics, meta={"model_name": getattr(model, "name", model.__class__.__name__)})



def _classify_exception(exc: Exception) -> str:
    msg = str(exc).lower()
    if isinstance(exc, OptionalDependencyError):
        return "skipped_optional_dependency"
    if isinstance(exc, (ImportError, ModuleNotFoundError)):
        if "optional dependency" in msg or "install with:" in msg or "no module named" in msg or "could not import" in msg:
            return "skipped_optional_dependency"
    return "error"



def run_sweep(spec: SweepMatrixSpec) -> SweepRun:
    results: List[SweepCellResult] = []
    for cell in spec.cells:
        try:
            task = str(cell.task_family).lower().strip()
            if task == "panel":
                result = _run_panel_cell(cell)
            elif task in {"impact", "forecast_cf"}:
                result = _run_impact_cell(cell)
            else:
                raise ValueError(f"Unsupported task family in sweep cell: {cell.task_family}")
            results.append(result)
        except Exception as exc:  # noqa: BLE001
            status = _classify_exception(exc)
            results.append(
                SweepCellResult(
                    cell=cell,
                    status=status,
                    error=str(exc),
                    metrics={},
                    meta={
                        "exception_type": exc.__class__.__name__,
                        "optional_dependency": status == "skipped_optional_dependency",
                    },
                )
            )
            if spec.stop_on_error and status != "skipped_optional_dependency":
                raise
    return SweepRun(spec=spec, results=results)



def render_sweep_markdown(run: SweepRun) -> str:
    lines: List[str] = []
    lines.append(f"# Sweep report: {run.spec.name}")
    summary = run.summary()
    lines.append("")
    lines.append(f"Cells: {summary['cells']}; ok: {summary['ok']}; skipped: {summary['skipped']}; errors: {summary['errors']}")
    if summary.get("data_sources"):
        lines.append(f"Data sources: {', '.join(summary['data_sources'])}")
    lines.append("")
    best_panel = run.best_by_metric("post_pre_rmspe_ratio", lower_is_better=False)
    if not best_panel.empty:
        lines.append("## Best panel cells by post/pre RMSPE ratio")
        lines.append("")
        show = [c for c in ["task_family", "dataset", "model", "data_source", "metric::post_pre_rmspe_ratio", "metric::space_placebo_pvalue"] if c in best_panel.columns]
        lines.append(dataframe_to_markdown(best_panel[show], index=False))
        lines.append("")
    best_impact = run.best_by_metric("rmse", lower_is_better=True)
    if not best_impact.empty:
        lines.append("## Best impact cells by RMSE")
        lines.append("")
        cols = [c for c in ["task_family", "dataset", "model", "metric::rmse", "metric::cum_mae"] if c in best_impact.columns]
        lines.append(dataframe_to_markdown(best_impact[cols], index=False))
        lines.append("")
    df = run.to_frame()
    if not df.empty:
        lines.append("## Full result grid")
        lines.append("")
        show_cols = [c for c in ["task_family", "dataset", "model", "data_source", "status", "error", "metric::post_pre_rmspe_ratio", "metric::rmse"] if c in df.columns]
        lines.append(dataframe_to_markdown(df[show_cols], index=False))
        lines.append("")
    if summary.get("skipped"):
        lines.append("## Optional backend notes")
        lines.append("")
        lines.append("Some cells were skipped because optional backends were not installed. This is not a model failure; it means the benchmark spec asked for backends outside the built-in core stack.")
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "SweepCellResult",
    "SweepCellSpec",
    "SweepMatrixSpec",
    "SweepRun",
    "make_default_sweep_spec",
    "render_sweep_markdown",
    "run_sweep",
]
