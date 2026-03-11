from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from tscfbench.agent.tokens import TokenBudget, canonical_json_dumps, estimate_json_tokens, estimate_text_tokens
from tscfbench.core import PanelCase, PredictionResult
from tscfbench.protocols import PanelBenchmarkOutput


def _slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "artifact"


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    kind: str
    path: str
    media_type: str
    bytes: int
    approx_tokens: int
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "path": self.path,
            "media_type": self.media_type,
            "bytes": self.bytes,
            "approx_tokens": self.approx_tokens,
            "summary": self.summary,
        }


class ArtifactStore:
    def __init__(self, root: Union[str, Path]):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_text(self, text: str, kind: str, name_hint: str, suffix: str = ".txt", media_type: str = "text/plain") -> ArtifactRef:
        text = text or ""
        data = text.encode("utf-8")
        digest = hashlib.sha256(data).hexdigest()[:16]
        name = f"{_slug(kind)}-{_slug(name_hint)}-{digest}{suffix}"
        path = self.root / name
        if not path.exists():
            path.write_bytes(data)
        est = estimate_text_tokens(text)
        return ArtifactRef(
            id=digest,
            kind=kind,
            path=str(path),
            media_type=media_type,
            bytes=len(data),
            approx_tokens=est.approx_tokens,
            summary=f"{kind} stored at {path.name}",
        )

    def put_json(self, obj: Any, kind: str, name_hint: str, pretty: bool = False) -> ArtifactRef:
        text = canonical_json_dumps(obj, pretty=pretty)
        return self.put_text(text, kind=kind, name_hint=name_hint, suffix=".json", media_type="application/json")

    def put_csv(self, df: pd.DataFrame, kind: str, name_hint: str) -> ArtifactRef:
        text = df.to_csv(index=False)
        return self.put_text(text, kind=kind, name_hint=name_hint, suffix=".csv", media_type="text/csv")


@dataclass
class ContextPack:
    schema_version: str
    pack_type: str
    dataset_id: str
    case_type: str
    summary: Dict[str, Any]
    preview: Dict[str, Any]
    hints: List[str]
    artifact_refs: List[ArtifactRef] = field(default_factory=list)
    token_budget: Dict[str, Any] = field(default_factory=dict)
    token_estimate: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "pack_type": self.pack_type,
            "dataset_id": self.dataset_id,
            "case_type": self.case_type,
            "summary": self.summary,
            "preview": self.preview,
            "hints": self.hints,
            "artifact_refs": [a.to_dict() for a in self.artifact_refs],
            "token_budget": self.token_budget,
            "token_estimate": self.token_estimate,
        }

    def to_json(self, path: Union[str, Path], pretty: bool = True) -> None:
        Path(path).write_text(canonical_json_dumps(self.to_dict(), pretty=pretty), encoding="utf-8")


@dataclass
class RunDigest:
    schema_version: str
    run_id: str
    dataset_id: str
    model_name: str
    metrics: Dict[str, Any]
    preview: Dict[str, Any]
    next_actions: List[str]
    artifact_refs: List[ArtifactRef] = field(default_factory=list)
    token_budget: Dict[str, Any] = field(default_factory=dict)
    token_estimate: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "dataset_id": self.dataset_id,
            "model_name": self.model_name,
            "metrics": self.metrics,
            "preview": self.preview,
            "next_actions": self.next_actions,
            "artifact_refs": [a.to_dict() for a in self.artifact_refs],
            "token_budget": self.token_budget,
            "token_estimate": self.token_estimate,
        }

    def to_json(self, path: Union[str, Path], pretty: bool = True) -> None:
        Path(path).write_text(canonical_json_dumps(self.to_dict(), pretty=pretty), encoding="utf-8")


def _float(x: Any) -> float:
    try:
        return float(x)
    except Exception:  # noqa: BLE001
        return float("nan")


def _head_tail_records(times: Sequence[Any], values: Sequence[float], n: int = 3) -> List[Dict[str, Any]]:
    times_arr = np.asarray(times)
    values_arr = np.asarray(values, dtype=float)
    if len(times_arr) <= 2 * n:
        idxs = list(range(len(times_arr)))
    else:
        idxs = list(range(n)) + list(range(len(times_arr) - n, len(times_arr)))
    return [{"t": times_arr[i].item() if hasattr(times_arr[i], "item") else times_arr[i], "y": _float(values_arr[i])} for i in idxs]


def _top_correlated_controls(case: PanelCase, top_k: int) -> pd.DataFrame:
    y = case.treated_series()
    X, control_units = case.control_matrix()
    pre = case.pre_mask
    rows: List[Dict[str, Any]] = []
    for j, unit in enumerate(control_units):
        x = X[:, j]
        valid = np.isfinite(y[pre]) & np.isfinite(x[pre])
        if np.sum(valid) < 2:
            corr = np.nan
        else:
            corr = float(np.corrcoef(y[pre][valid], x[pre][valid])[0, 1])
        rows.append({"unit": unit, "pre_corr": corr, "pre_mean": _float(np.nanmean(x[pre])), "post_mean": _float(np.nanmean(x[~pre]))})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("pre_corr", key=lambda s: np.abs(s.to_numpy(dtype=float)), ascending=False).head(top_k).reset_index(drop=True)


def _budgeted_sizes(budget: TokenBudget, requested_controls: int, requested_preview_points: int, requested_placebos: int) -> Dict[str, int]:
    usable = budget.usable_context_tokens
    controls = requested_controls
    preview = requested_preview_points
    placebos = requested_placebos
    if usable < 1500:
        controls = min(controls, 3)
        preview = min(preview, 4)
        placebos = min(placebos, 3)
    if usable < 900:
        controls = min(controls, 2)
        preview = min(preview, 2)
        placebos = min(placebos, 2)
    if usable < 600:
        controls = min(controls, 1)
        preview = min(preview, 1)
        placebos = min(placebos, 1)
    return {"controls": max(1, controls), "preview": max(1, preview), "placebos": max(1, placebos)}


def pack_panel_case(
    case: PanelCase,
    artifact_dir: Union[str, Path],
    budget: Optional[TokenBudget] = None,
    top_k_controls: int = 5,
    preview_points: int = 6,
    write_full_dataset: bool = True,
) -> ContextPack:
    budget = budget or TokenBudget()
    sizes = _budgeted_sizes(budget, top_k_controls, preview_points, requested_placebos=5)
    store = ArtifactStore(artifact_dir)

    dataset_id = str(case.metadata.get("dataset_id", "unnamed"))
    y = case.treated_series()
    pre = case.pre_mask
    post = case.post_mask
    donor_df = _top_correlated_controls(case, top_k=sizes["controls"])

    artifact_refs: List[ArtifactRef] = []
    if write_full_dataset:
        artifact_refs.append(store.put_csv(case.df, kind="dataset_long", name_hint=dataset_id))
    treated_df = pd.DataFrame({"t": case.times, "y": y})
    artifact_refs.append(store.put_csv(treated_df, kind="treated_series", name_hint=dataset_id))
    if not donor_df.empty:
        artifact_refs.append(store.put_csv(donor_df, kind="top_donors", name_hint=dataset_id))
    metadata_payload = {
        "dataset_id": dataset_id,
        "treated_unit": case.treated_unit,
        "intervention_t": case.intervention_t,
        "n_units": len(case.units),
        "n_periods": len(case.times),
        "balanced": case.is_balanced(),
    }
    artifact_refs.append(store.put_json(metadata_payload, kind="dataset_meta", name_hint=dataset_id))

    summary = {
        "treated_unit": case.treated_unit,
        "intervention_t": case.intervention_t,
        "n_units": len(case.units),
        "n_periods": len(case.times),
        "pre_periods": int(np.sum(pre)),
        "post_periods": int(np.sum(post)),
        "balanced": bool(case.is_balanced()),
        "outcome": case.y_col,
        "pre_mean": _float(np.nanmean(y[pre])),
        "post_mean": _float(np.nanmean(y[post])),
        "pre_std": _float(np.nanstd(y[pre])),
        "post_std": _float(np.nanstd(y[post])),
        "has_truth_counterfactual": bool(case.y_cf_true is not None),
    }
    preview = {
        "treated_series_preview": _head_tail_records(case.times, y, n=sizes["preview"]),
        "top_donor_preview": donor_df.to_dict(orient="records"),
    }
    if case.y_cf_true is not None:
        preview["true_counterfactual_preview"] = _head_tail_records(case.times, case.y_cf_true, n=sizes["preview"])

    hints = [
        "Use artifact handles before requesting the full long-format panel.",
        "Prefer editing experiment specs instead of rewriting large prompts.",
        "Treat CSV/JSON artifacts as load-on-demand context, not chat payload.",
        "Use concise JSON summaries for intermediate state handoffs.",
    ]
    pack = ContextPack(
        schema_version="0.5.0",
        pack_type="panel_context_pack",
        dataset_id=dataset_id,
        case_type="panel",
        summary=summary,
        preview=preview,
        hints=hints,
        artifact_refs=artifact_refs,
        token_budget=budget.to_dict(),
    )
    pack.token_estimate = estimate_json_tokens(pack.to_dict()).to_dict()
    return pack


def _prediction_frame(case: PanelCase, pred: PredictionResult) -> pd.DataFrame:
    return pred.to_frame(case.times, case.treated_series())


def _core_metric_subset(metrics: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "pre_rmspe",
        "post_rmspe",
        "post_pre_rmspe_ratio",
        "cum_effect",
        "avg_effect",
        "avg_abs_effect",
        "space_placebo_pvalue",
        "time_placebo_pvalue",
        "space_placebo_eligible_controls",
        "time_placebo_count",
        "truth_rmse",
        "truth_mae",
        "truth_r2",
        "truth_cum_effect",
    ]
    return {k: metrics[k] for k in keys if k in metrics}


def pack_panel_run(
    case: PanelCase,
    report: PanelBenchmarkOutput,
    artifact_dir: Union[str, Path],
    budget: Optional[TokenBudget] = None,
    top_k_placebos: int = 5,
    run_id: str = "run",
) -> RunDigest:
    budget = budget or TokenBudget()
    sizes = _budgeted_sizes(budget, requested_controls=5, requested_preview_points=4, requested_placebos=top_k_placebos)
    store = ArtifactStore(artifact_dir)

    dataset_id = str(case.metadata.get("dataset_id", "unnamed"))
    artifact_refs: List[ArtifactRef] = []
    pred_df = _prediction_frame(case, report.prediction)
    artifact_refs.append(store.put_csv(pred_df, kind="prediction_frame", name_hint=run_id))
    artifact_refs.append(store.put_json(report.metrics, kind="metrics", name_hint=run_id))
    if report.space_placebos is not None and not report.space_placebos.empty:
        artifact_refs.append(store.put_csv(report.space_placebos, kind="space_placebos", name_hint=run_id))
    if report.time_placebos is not None and not report.time_placebos.empty:
        artifact_refs.append(store.put_csv(report.time_placebos, kind="time_placebos", name_hint=run_id))

    preview = {
        "space_placebos_head": report.space_placebos.head(sizes["placebos"]).to_dict(orient="records") if report.space_placebos is not None and not report.space_placebos.empty else [],
        "time_placebos_head": report.time_placebos.head(sizes["placebos"]).to_dict(orient="records") if report.time_placebos is not None and not report.time_placebos.empty else [],
        "prediction_preview": pred_df.head(max(2, sizes["preview"]))[["t", "y_obs", "y_cf_mean", "effect"]].to_dict(orient="records"),
    }
    next_actions = [
        "If fit is weak, modify the JSON experiment spec instead of pasting a new natural-language prompt.",
        "If a placebo table matters, load the CSV artifact by handle rather than inlining the whole table.",
        "If you add a model adapter, update AGENTS.md and the repo map so future agents stay token efficient.",
    ]
    digest = RunDigest(
        schema_version="0.5.0",
        run_id=run_id,
        dataset_id=dataset_id,
        model_name=str(report.metadata.get("model_name", "unknown")),
        metrics=_core_metric_subset(report.metrics),
        preview=preview,
        next_actions=next_actions,
        artifact_refs=artifact_refs,
        token_budget=budget.to_dict(),
    )
    digest.token_estimate = estimate_json_tokens(digest.to_dict()).to_dict()
    return digest
