from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np
import pandas as pd

from tscfbench.bench import benchmark
from tscfbench.core import ImpactCase, PanelCase
from tscfbench.model_zoo import materialize_model
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel
from tscfbench.report import render_panel_markdown
from tscfbench.visuals import write_impact_visual_bundle, write_panel_visual_bundle


def _jsonable_metric(value: Any) -> Any:
    if value is None:
        return None
    try:
        scalar = value.item() if hasattr(value, "item") else value
    except Exception:  # noqa: BLE001
        scalar = value
    if isinstance(scalar, float) and not np.isfinite(scalar):
        return None
    return scalar


def _compact_summary(mapping: Dict[str, Any]) -> Dict[str, Any]:
    return {k: _jsonable_metric(v) for k, v in mapping.items() if _jsonable_metric(v) is not None}


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _maybe_parse_time(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    out = df.copy()
    try:
        parsed = pd.to_datetime(out[time_col], errors="raise")
        out[time_col] = parsed
    except Exception:  # noqa: BLE001
        pass
    return out


def _coerce_intervention(df: pd.DataFrame, time_col: str, intervention_t: Any) -> Any:
    values = df[time_col]
    if pd.api.types.is_datetime64_any_dtype(values):
        try:
            target = pd.Timestamp(intervention_t)
            parsed = pd.to_datetime(values)
            mask = parsed == target
            if bool(mask.any()):
                first = int(np.flatnonzero(np.asarray(mask))[0])
                return values.iloc[first]
            return target
        except Exception:  # noqa: BLE001
            return intervention_t
    value_list = values.tolist()
    if intervention_t in set(value_list):
        return intervention_t
    try:
        return int(intervention_t)
    except Exception:  # noqa: BLE001
        return intervention_t


def _impact_report(case: ImpactCase, model_name: str, metrics: Dict[str, Any], scenario: str = "") -> str:
    lines: List[str] = [
        f"# Impact report: {scenario or case.metadata.get('dataset_id', 'custom_impact')}",
        "",
        f"- intervention: `{case.intervention_t}`",
        f"- outcome: `{case.y_col}`",
        f"- controls: `{', '.join(case.x_cols) if case.x_cols else '(none)'}`",
        f"- model: `{model_name}`",
        "",
        "## Metrics",
        "",
    ]
    for key in ["rmse", "mae", "r2", "cum_mae", "cum_rmse", "cum_final_error", "coverage", "avg_effect", "cum_effect"]:
        if key in metrics:
            try:
                value = float(metrics[key])
                lines.append(f"- {key}: {value:.4f}")
            except Exception:  # noqa: BLE001
                lines.append(f"- {key}: {metrics[key]}")
    if scenario:
        lines.extend(["", "## Scenario", "", scenario, ""])
    return "\n".join(lines)


def _run_panel_data_impl(
    df: pd.DataFrame,
    *,
    dataset_id: str,
    source: str,
    unit_col: str,
    time_col: str,
    y_col: str,
    treated_unit: Any,
    intervention_t: Any,
    model: str,
    output_dir: str | Path,
    placebo_pre_rmspe_factor: float,
    min_pre_periods: int,
    max_time_placebos: int,
    title: str | None,
    plot: bool,
    takeaway: str | None,
) -> Dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _maybe_parse_time(df.copy(), time_col)
    intervention = _coerce_intervention(df, time_col, intervention_t)
    case = PanelCase(
        df=df,
        unit_col=unit_col,
        time_col=time_col,
        y_col=y_col,
        treated_unit=treated_unit,
        intervention_t=intervention,
        metadata={"dataset_id": dataset_id, "source": source},
    )
    fitted = materialize_model(model)
    report = benchmark_panel(
        case,
        fitted,
        config=PanelProtocolConfig(
            run_space_placebo=True,
            run_time_placebo=True,
            placebo_pre_rmspe_factor=placebo_pre_rmspe_factor,
            min_pre_periods=min_pre_periods,
            max_time_placebos=max_time_placebos,
        ),
    )
    metrics_json = out_dir / "panel_metrics.json"
    report_md = out_dir / "panel_report.md"
    prediction_csv = out_dir / "panel_prediction_frame.csv"
    report_md.write_text(render_panel_markdown(case, report), encoding="utf-8")
    metrics_json.write_text(
        json.dumps({"metrics": report.metrics, "metadata": report.metadata}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    pred_df = report.prediction.to_frame(case.times, case.treated_series(), intervention_index=case.intervention_index)
    pred_df.to_csv(prediction_csv, index=False)
    artifacts = {
        "metrics_json": str(metrics_json),
        "report_md": str(report_md),
        "prediction_csv": str(prediction_csv),
    }
    if plot:
        visuals = write_panel_visual_bundle(
            case,
            report,
            output_dir=out_dir,
            stem="panel",
            title=title or f"{dataset_id}: treated vs counterfactual",
            ylabel=y_col,
            takeaway=takeaway,
        )
        artifacts.update(visuals)
    summary = _compact_summary(
        {
            "treated_unit": str(treated_unit),
            "intervention_t": str(intervention),
            "model": model,
            "post_pre_rmspe_ratio": report.metrics.get("post_pre_rmspe_ratio"),
            "cum_effect": report.metrics.get("cum_effect"),
            "avg_effect": report.metrics.get("avg_effect"),
            "space_placebo_pvalue": report.metrics.get("space_placebo_pvalue"),
            "time_placebo_pvalue": report.metrics.get("time_placebo_pvalue"),
        }
    )
    return {
        "output_dir": str(out_dir),
        "summary": summary,
        "generated_files": artifacts,
        "next_command": "python -m tscfbench doctor",
        "data_source": source,
    }


def run_panel_data(
    df: pd.DataFrame,
    *,
    unit_col: str,
    time_col: str,
    y_col: str,
    treated_unit: Any,
    intervention_t: Any,
    model: str = "simple_scm",
    output_dir: str | Path = "tscfbench_panel_run",
    placebo_pre_rmspe_factor: float = 5.0,
    min_pre_periods: int = 12,
    max_time_placebos: int = 8,
    title: str | None = None,
    plot: bool = True,
    takeaway: str | None = None,
    data_name: str = "custom_panel",
) -> Dict[str, Any]:
    payload = _run_panel_data_impl(
        df,
        dataset_id=data_name,
        source="dataframe",
        unit_col=unit_col,
        time_col=time_col,
        y_col=y_col,
        treated_unit=treated_unit,
        intervention_t=intervention_t,
        model=model,
        output_dir=output_dir,
        placebo_pre_rmspe_factor=placebo_pre_rmspe_factor,
        min_pre_periods=min_pre_periods,
        max_time_placebos=max_time_placebos,
        title=title,
        plot=plot,
        takeaway=takeaway,
    )
    return {
        "kind": "panel_data_run",
        "data_name": data_name,
        **payload,
    }


def run_csv_panel(
    csv_path: str | Path,
    *,
    unit_col: str,
    time_col: str,
    y_col: str,
    treated_unit: Any,
    intervention_t: Any,
    model: str = "simple_scm",
    output_dir: str | Path = "tscfbench_csv_panel",
    placebo_pre_rmspe_factor: float = 5.0,
    min_pre_periods: int = 12,
    max_time_placebos: int = 8,
    title: str | None = None,
    plot: bool = True,
    takeaway: str | None = None,
) -> Dict[str, Any]:
    path = Path(csv_path)
    payload = _run_panel_data_impl(
        _read_csv(path),
        dataset_id=path.stem,
        source=str(path),
        unit_col=unit_col,
        time_col=time_col,
        y_col=y_col,
        treated_unit=treated_unit,
        intervention_t=intervention_t,
        model=model,
        output_dir=output_dir,
        placebo_pre_rmspe_factor=placebo_pre_rmspe_factor,
        min_pre_periods=min_pre_periods,
        max_time_placebos=max_time_placebos,
        title=title,
        plot=plot,
        takeaway=takeaway,
    )
    return {
        "kind": "csv_panel_run",
        "csv_path": str(path),
        **payload,
    }


def _run_impact_data_impl(
    df: pd.DataFrame,
    *,
    dataset_id: str,
    source: str,
    time_col: str,
    y_col: str,
    x_cols: Sequence[str],
    intervention_t: Any,
    model: str,
    output_dir: str | Path,
    title: str | None,
    plot: bool,
    takeaway: str | None,
) -> Dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = _maybe_parse_time(df.copy(), time_col)
    intervention = _coerce_intervention(df, time_col, intervention_t)
    case = ImpactCase(
        df=df,
        time_col=time_col,
        y_col=y_col,
        x_cols=list(x_cols),
        intervention_t=intervention,
        metadata={"dataset_id": dataset_id, "source": source},
    )
    fitted = materialize_model(model)
    out = benchmark(case, fitted)
    metrics_json = out_dir / "impact_metrics.json"
    report_md = out_dir / "impact_report.md"
    prediction_csv = out_dir / "impact_prediction_frame.csv"
    report_md.write_text(
        _impact_report(case, getattr(fitted, "name", model), out.metrics, scenario=title or dataset_id),
        encoding="utf-8",
    )
    metrics_json.write_text(
        json.dumps({"metrics": out.metrics, "metadata": out.prediction.meta}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    pred_df = out.prediction.to_frame(case.t, case.y_obs, intervention_index=case.intervention_index)
    pred_df.to_csv(prediction_csv, index=False)
    artifacts = {
        "metrics_json": str(metrics_json),
        "report_md": str(report_md),
        "prediction_csv": str(prediction_csv),
    }
    if plot:
        visuals = write_impact_visual_bundle(
            case,
            out,
            output_dir=out_dir,
            stem="impact",
            title=title or f"{dataset_id}: observed vs counterfactual",
            ylabel=y_col,
            takeaway=takeaway,
        )
        artifacts.update(visuals)
    summary = _compact_summary(
        {
            "intervention_t": str(intervention),
            "model": model,
            "controls": len(list(x_cols)),
            "post_period_points": int(case.post_mask.sum()),
            "avg_effect": out.metrics.get("avg_effect"),
            "avg_abs_effect": out.metrics.get("avg_abs_effect"),
            "cum_effect": out.metrics.get("cum_effect"),
            "max_abs_effect": out.metrics.get("max_abs_effect"),
            "rmse": out.metrics.get("rmse"),
            "cum_mae": out.metrics.get("cum_mae"),
            "coverage": out.metrics.get("coverage"),
        }
    )
    return {
        "output_dir": str(out_dir),
        "summary": summary,
        "generated_files": artifacts,
        "next_command": "python -m tscfbench doctor",
        "data_source": source,
    }


def run_impact_data(
    df: pd.DataFrame,
    *,
    time_col: str,
    y_col: str,
    x_cols: Sequence[str],
    intervention_t: Any,
    model: str = "ols_impact",
    output_dir: str | Path = "tscfbench_impact_run",
    title: str | None = None,
    plot: bool = True,
    takeaway: str | None = None,
    data_name: str = "custom_impact",
) -> Dict[str, Any]:
    payload = _run_impact_data_impl(
        df,
        dataset_id=data_name,
        source="dataframe",
        time_col=time_col,
        y_col=y_col,
        x_cols=x_cols,
        intervention_t=intervention_t,
        model=model,
        output_dir=output_dir,
        title=title,
        plot=plot,
        takeaway=takeaway,
    )
    return {
        "kind": "impact_data_run",
        "data_name": data_name,
        **payload,
    }


def run_csv_impact(
    csv_path: str | Path,
    *,
    time_col: str,
    y_col: str,
    x_cols: Sequence[str],
    intervention_t: Any,
    model: str = "ols_impact",
    output_dir: str | Path = "tscfbench_csv_impact",
    title: str | None = None,
    plot: bool = True,
    takeaway: str | None = None,
) -> Dict[str, Any]:
    path = Path(csv_path)
    payload = _run_impact_data_impl(
        _read_csv(path),
        dataset_id=path.stem,
        source=str(path),
        time_col=time_col,
        y_col=y_col,
        x_cols=x_cols,
        intervention_t=intervention_t,
        model=model,
        output_dir=output_dir,
        title=title,
        plot=plot,
        takeaway=takeaway,
    )
    return {
        "kind": "csv_impact_run",
        "csv_path": str(path),
        **payload,
    }


__all__ = [
    "run_panel_data",
    "run_impact_data",
    "run_csv_panel",
    "run_csv_impact",
]
