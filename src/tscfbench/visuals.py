from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas as pd

from tscfbench.bench import BenchmarkOutput
from tscfbench.core import ImpactCase, PanelCase
from tscfbench.protocols import PanelBenchmarkOutput


def _ensure_dir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def _import_matplotlib():
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        return plt
    except Exception:
        return None


def _series_frame_from_panel(case: PanelCase, report: PanelBenchmarkOutput) -> pd.DataFrame:
    return report.prediction.to_frame(case.times, case.treated_series(), intervention_index=case.intervention_index)


def _series_frame_from_impact(case: ImpactCase, out: BenchmarkOutput) -> pd.DataFrame:
    return out.prediction.to_frame(case.t, case.y_obs, intervention_index=case.intervention_index)


def _intervention_value(case: PanelCase | ImpactCase) -> Any:
    if isinstance(case, PanelCase):
        return case.intervention_t
    return case.intervention_t if case.intervention_t in set(case.t.tolist()) else case.t[case.intervention_index]


def _share_card_text(*, title: str, summary: str, takeaway: str, badge: str) -> Dict[str, str]:
    return {"title": title, "summary": summary, "takeaway": takeaway, "badge": badge}


def _fmt_tick(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 12 else text[:12] + "..."


def _normalize(values: np.ndarray, low: float, high: float) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    span = float(high - low)
    if not np.isfinite(span) or abs(span) < 1e-12:
        return np.full_like(arr, 0.5, dtype=float)
    return (arr - low) / span


def _masked_post_array(values: np.ndarray, intervention_index: int) -> np.ndarray:
    out = np.full_like(np.asarray(values, dtype=float), np.nan, dtype=float)
    out[int(intervention_index) :] = np.asarray(values, dtype=float)[int(intervention_index) :]
    return out


def _prepare_post_intervention_visuals(
    *,
    t: Iterable[Any],
    y_obs: np.ndarray,
    y_cf: np.ndarray,
    intervention_index: int,
    y_cf_lower: Optional[np.ndarray] = None,
    y_cf_upper: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    t_list = list(t)
    if not t_list:
        raise ValueError("Cannot render visuals without time points")

    idx = int(min(max(intervention_index, 0), len(t_list) - 1))
    y_obs_arr = np.asarray(y_obs, dtype=float)
    y_cf_arr = np.asarray(y_cf, dtype=float)
    post_slice = slice(idx, len(t_list))

    payload: Dict[str, Any] = {
        "t": t_list,
        "post_t": t_list[idx:],
        "intervention_index": idx,
        "y_obs": y_obs_arr,
        "y_cf_post": y_cf_arr[post_slice],
        "y_cf_masked": _masked_post_array(y_cf_arr, idx),
    }

    point_effect_post = y_obs_arr[post_slice] - y_cf_arr[post_slice]
    payload["point_effect_post"] = point_effect_post
    payload["point_effect_masked"] = _masked_post_array(y_obs_arr - y_cf_arr, idx)

    cumulative_post = np.cumsum(point_effect_post)
    cumulative_masked = np.full_like(y_obs_arr, np.nan, dtype=float)
    cumulative_masked[idx:] = cumulative_post
    payload["cumulative_effect_post"] = cumulative_post
    payload["cumulative_effect_masked"] = cumulative_masked

    if y_cf_lower is not None and y_cf_upper is not None:
        lower = np.asarray(y_cf_lower, dtype=float)
        upper = np.asarray(y_cf_upper, dtype=float)
        payload["y_cf_lower_post"] = lower[post_slice]
        payload["y_cf_upper_post"] = upper[post_slice]
        payload["y_cf_lower_masked"] = _masked_post_array(lower, idx)
        payload["y_cf_upper_masked"] = _masked_post_array(upper, idx)

        point_lower_post = y_obs_arr[post_slice] - upper[post_slice]
        point_upper_post = y_obs_arr[post_slice] - lower[post_slice]
        payload["point_effect_lower_post"] = point_lower_post
        payload["point_effect_upper_post"] = point_upper_post
        payload["point_effect_lower_masked"] = _masked_post_array(y_obs_arr - upper, idx)
        payload["point_effect_upper_masked"] = _masked_post_array(y_obs_arr - lower, idx)

        cumulative_lower_post = np.cumsum(point_lower_post)
        cumulative_upper_post = np.cumsum(point_upper_post)
        cumulative_lower_masked = np.full_like(y_obs_arr, np.nan, dtype=float)
        cumulative_upper_masked = np.full_like(y_obs_arr, np.nan, dtype=float)
        cumulative_lower_masked[idx:] = cumulative_lower_post
        cumulative_upper_masked[idx:] = cumulative_upper_post
        payload["cumulative_effect_lower_post"] = cumulative_lower_post
        payload["cumulative_effect_upper_post"] = cumulative_upper_post
        payload["cumulative_effect_lower_masked"] = cumulative_lower_masked
        payload["cumulative_effect_upper_masked"] = cumulative_upper_masked

    return payload


def _svg_x_positions(length: int, *, x0: float, width: float) -> np.ndarray:
    if length <= 1:
        return np.asarray([x0 + width / 2.0], dtype=float)
    return np.linspace(x0, x0 + width, num=length)


def _svg_polyline(
    xs: np.ndarray,
    values: np.ndarray,
    *,
    y0: float,
    height: float,
    low: float,
    high: float,
) -> str:
    arr = np.asarray(values, dtype=float)
    mask = np.isfinite(arr)
    if mask.sum() == 0:
        return ""
    ys = y0 + height - _normalize(arr[mask], low, high) * height
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs[mask], ys))


def _svg_band(
    xs: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    *,
    y0: float,
    height: float,
    low: float,
    high: float,
) -> str:
    lo = np.asarray(lower, dtype=float)
    up = np.asarray(upper, dtype=float)
    mask = np.isfinite(lo) & np.isfinite(up)
    if mask.sum() < 2:
        return ""
    xs_masked = xs[mask]
    y_upper = y0 + height - _normalize(up[mask], low, high) * height
    y_lower = y0 + height - _normalize(lo[mask], low, high) * height
    points = list(zip(xs_masked, y_upper)) + list(zip(xs_masked[::-1], y_lower[::-1]))
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def _value_bounds(*arrays: np.ndarray) -> tuple[float, float]:
    finite_parts = []
    for arr in arrays:
        values = np.asarray(arr, dtype=float)
        values = values[np.isfinite(values)]
        if values.size:
            finite_parts.append(values)
    if not finite_parts:
        return (-1.0, 1.0)
    vals = np.concatenate(finite_parts)
    low = float(np.nanmin(vals))
    high = float(np.nanmax(vals))
    pad = max(1e-6, 0.08 * (high - low if high != low else abs(high) + 1.0))
    return low - pad, high + pad


def _write_simple_line_chart_svg(
    *,
    t: list[Any],
    payload: Dict[str, Any],
    title: str,
    ylabel: str,
    output_path: Path,
) -> str:
    width, height = 960, 420
    left, top, plot_w, plot_h = 70, 70, 820, 260
    xs = _svg_x_positions(len(t), x0=left, width=plot_w)
    low, high = _value_bounds(
        payload["y_obs"],
        payload["y_cf_masked"],
        payload.get("y_cf_lower_masked", np.asarray([])),
        payload.get("y_cf_upper_masked", np.asarray([])),
    )
    obs_points = _svg_polyline(xs, payload["y_obs"], y0=top, height=plot_h, low=low, high=high)
    cf_points = _svg_polyline(xs, payload["y_cf_masked"], y0=top, height=plot_h, low=low, high=high)
    band_points = ""
    if "y_cf_lower_masked" in payload and "y_cf_upper_masked" in payload:
        band_points = _svg_band(
            xs,
            payload["y_cf_lower_masked"],
            payload["y_cf_upper_masked"],
            y0=top,
            height=plot_h,
            low=low,
            high=high,
        )
    intervention_x = xs[payload["intervention_index"]]
    ticks = [0, len(t) // 2 if len(t) > 2 else 0, len(t) - 1]
    tick_labels = [escape(_fmt_tick(t[i])) for i in ticks]
    band_svg = (
        f'<polygon fill="#fdba74" fill-opacity="0.40" stroke="none" points="{band_points}"/>'
        if band_points
        else ""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)}</text>
  <text x="{left}" y="52" font-size="13" fill="#555">{escape(ylabel)}</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>
  <line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#777"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#777"/>
  {band_svg}
  <polyline fill="none" stroke="#111827" stroke-width="2.6" points="{obs_points}"/>
  <polyline fill="none" stroke="#f97316" stroke-width="2.6" stroke-dasharray="8 6" points="{cf_points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top + plot_h}" stroke="#6b7280" stroke-dasharray="6 6"/>
  <text x="{intervention_x + 6:.2f}" y="{top + 16}" font-size="12" fill="#111">Intervention</text>
  <text x="{left}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[0]}</text>
  <text x="{left + plot_w / 2 - 18:.2f}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[1]}</text>
  <text x="{left + plot_w - 42:.2f}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[2]}</text>
  <rect x="{left}" y="{height - 58}" width="12" height="12" fill="#111827"/>
  <text x="{left + 18}" y="{height - 48}" font-size="13">Observed</text>
  <rect x="{left + 120}" y="{height - 58}" width="12" height="12" fill="#f97316"/>
  <text x="{left + 138}" y="{height - 48}" font-size="13">Counterfactual (post)</text>
  <rect x="{left + 320}" y="{height - 58}" width="12" height="12" fill="#fdba74"/>
  <text x="{left + 338}" y="{height - 48}" font-size="13">95% interval</text>
</svg>"""
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)


def _write_simple_effect_svg(
    *,
    t: list[Any],
    series: np.ndarray,
    lower: Optional[np.ndarray],
    upper: Optional[np.ndarray],
    intervention_index: int,
    title: str,
    series_label: str,
    output_path: Path,
) -> str:
    width, height = 960, 420
    left, top, plot_w, plot_h = 70, 70, 820, 260
    xs = _svg_x_positions(len(t), x0=left, width=plot_w)
    low, high = _value_bounds(series, np.asarray([0.0]), lower if lower is not None else np.asarray([]), upper if upper is not None else np.asarray([]))
    points = _svg_polyline(xs, series, y0=top, height=plot_h, low=low, high=high)
    band_points = ""
    if lower is not None and upper is not None:
        band_points = _svg_band(xs, lower, upper, y0=top, height=plot_h, low=low, high=high)
    intervention_x = xs[intervention_index]
    zero_y = top + plot_h - _normalize(np.asarray([0.0]), low, high)[0] * plot_h
    ticks = [0, len(t) // 2 if len(t) > 2 else 0, len(t) - 1]
    tick_labels = [escape(_fmt_tick(t[i])) for i in ticks]
    band_svg = (
        f'<polygon fill="#fdba74" fill-opacity="0.40" stroke="none" points="{band_points}"/>'
        if band_points
        else ""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)}</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>
  <line x1="{left}" y1="{zero_y:.2f}" x2="{left + plot_w}" y2="{zero_y:.2f}" stroke="#9ca3af"/>
  {band_svg}
  <polyline fill="none" stroke="#f97316" stroke-width="2.8" stroke-dasharray="8 6" points="{points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top + plot_h}" stroke="#6b7280" stroke-dasharray="6 6"/>
  <text x="{intervention_x + 6:.2f}" y="{top + 16}" font-size="12" fill="#111">Intervention</text>
  <text x="{left}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[0]}</text>
  <text x="{left + plot_w / 2 - 18:.2f}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[1]}</text>
  <text x="{left + plot_w - 42:.2f}" y="{top + plot_h + 28}" font-size="12" fill="#444">{tick_labels[2]}</text>
  <text x="{left}" y="{height - 48}" font-size="13">{escape(series_label)}</text>
</svg>"""
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)


def _write_simple_bar_svg(*, weights: pd.Series, title: str, output_path: Path) -> str:
    width, height = 860, 420
    left, top, plot_w, plot_h = 80, 70, 720, 250
    series = weights.sort_values(ascending=False)
    vals = series.to_numpy(dtype=float)
    max_v = max(float(np.nanmax(vals)) if len(vals) else 1.0, 1e-9)
    n = max(1, len(vals))
    bar_w = plot_w / n * 0.72
    gap = plot_w / n * 0.28
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)} - donor contributions</text>',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>',
    ]
    for i, (label, val) in enumerate(series.items()):
        x = left + i * (bar_w + gap)
        h = plot_h * (float(val) / max_v)
        y = top + plot_h - h
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="#2563eb"/>')
        parts.append(f'<text x="{x:.2f}" y="{top + plot_h + 22}" font-size="10" fill="#444" transform="rotate(20 {x:.2f},{top + plot_h + 22})">{escape(_fmt_tick(label))}</text>')
    parts.append("</svg>")
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return str(output_path)


def _write_simple_share_card_svg(
    *,
    t: list[Any],
    payload: Dict[str, Any],
    summary_text: Dict[str, str],
    output_path: Path,
) -> str:
    width, height = 1180, 480
    left, top, plot_w, plot_h = 60, 90, 420, 250
    xs = _svg_x_positions(len(t), x0=left, width=plot_w)
    low, high = _value_bounds(
        payload["y_obs"],
        payload["y_cf_masked"],
        payload.get("y_cf_lower_masked", np.asarray([])),
        payload.get("y_cf_upper_masked", np.asarray([])),
    )
    obs_points = _svg_polyline(xs, payload["y_obs"], y0=top, height=plot_h, low=low, high=high)
    cf_points = _svg_polyline(xs, payload["y_cf_masked"], y0=top, height=plot_h, low=low, high=high)
    band_points = ""
    if "y_cf_lower_masked" in payload and "y_cf_upper_masked" in payload:
        band_points = _svg_band(
            xs,
            payload["y_cf_lower_masked"],
            payload["y_cf_upper_masked"],
            y0=top,
            height=plot_h,
            low=low,
            high=high,
        )
    intervention_x = xs[payload["intervention_index"]]
    band_svg = (
        f'<polygon fill="#fdba74" fill-opacity="0.40" stroke="none" points="{band_points}"/>'
        if band_points
        else ""
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd" rx="10"/>
  {band_svg}
  <polyline fill="none" stroke="#111827" stroke-width="3" points="{obs_points}"/>
  <polyline fill="none" stroke="#f97316" stroke-width="3" stroke-dasharray="8 6" points="{cf_points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top + plot_h}" stroke="#6b7280" stroke-dasharray="6 6"/>
  <text x="{left}" y="48" font-size="24" font-weight="700">{escape(summary_text["title"])}</text>
  <text x="560" y="90" font-size="14" fill="#555">{escape(summary_text["badge"])}</text>
  <text x="560" y="150" font-size="18" font-weight="700">{escape(summary_text["summary"])}</text>
  <foreignObject x="560" y="210" width="540" height="170"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:22px;font-weight:700;color:#111;line-height:1.3;">{escape(summary_text["takeaway"])}</div></foreignObject>
  <text x="560" y="420" font-size="12" fill="#666">Generated by tscfbench</text>
</svg>"""
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)


def _render_counterfactual_figure(
    *,
    plt,
    payload: Dict[str, Any],
    intervention_t: Any,
    title: str,
    ylabel: str,
    output_png: Path,
    output_svg: Path,
) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11.0, 9.2), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.7, 1.7]})

    axes[0].plot(payload["t"], payload["y_obs"], color="#111827", linewidth=2.2, label="Observed")
    axes[0].plot(payload["post_t"], payload["y_cf_post"], color="#f97316", linewidth=2.2, linestyle="--", label="Counterfactual (post)")
    if "y_cf_lower_post" in payload and "y_cf_upper_post" in payload:
        axes[0].fill_between(payload["post_t"], payload["y_cf_lower_post"], payload["y_cf_upper_post"], color="#fdba74", alpha=0.45, label="95% interval")
    axes[0].set_title(title)
    axes[0].set_ylabel(ylabel)
    axes[0].legend(loc="best")

    axes[1].plot(payload["post_t"], payload["point_effect_post"], color="#f97316", linewidth=2.2, linestyle="--", label="Point effect")
    if "point_effect_lower_post" in payload and "point_effect_upper_post" in payload:
        axes[1].fill_between(payload["post_t"], payload["point_effect_lower_post"], payload["point_effect_upper_post"], color="#fdba74", alpha=0.45)
    axes[1].axhline(0.0, color="#6b7280", linewidth=1.0)
    axes[1].set_ylabel("Point effect")
    axes[1].legend(loc="best")

    axes[2].plot(payload["post_t"], payload["cumulative_effect_post"], color="#f97316", linewidth=2.2, linestyle="--", label="Cumulative effect")
    if "cumulative_effect_lower_post" in payload and "cumulative_effect_upper_post" in payload:
        axes[2].fill_between(payload["post_t"], payload["cumulative_effect_lower_post"], payload["cumulative_effect_upper_post"], color="#fdba74", alpha=0.45)
    axes[2].axhline(0.0, color="#6b7280", linewidth=1.0)
    axes[2].set_ylabel("Cumulative effect")
    axes[2].legend(loc="best")

    for ax in axes:
        ax.axvline(intervention_t, color="#6b7280", linestyle="--", linewidth=1.6)
        ax.grid(alpha=0.22)

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_png, dpi=160)
    fig.savefig(output_svg, format="svg")
    plt.close(fig)


def _render_single_effect_figure(
    *,
    plt,
    t: list[Any],
    post_t: list[Any],
    series_post: np.ndarray,
    lower_post: Optional[np.ndarray],
    upper_post: Optional[np.ndarray],
    intervention_t: Any,
    title: str,
    ylabel: str,
    label: str,
    output_png: Path,
    output_svg: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.0))
    ax.plot(post_t, series_post, color="#f97316", linewidth=2.2, linestyle="--", label=label)
    if lower_post is not None and upper_post is not None:
        ax.fill_between(post_t, lower_post, upper_post, color="#fdba74", alpha=0.45, label="95% interval")
    ax.axhline(0.0, color="#6b7280", linewidth=1.0)
    ax.axvline(intervention_t, color="#6b7280", linestyle="--", linewidth=1.6)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlim(t[0], t[-1])
    ax.grid(alpha=0.22)
    ax.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_png, dpi=160)
    fig.savefig(output_svg, format="svg")
    plt.close(fig)


def write_prediction_visuals(
    *,
    t: Iterable[Any],
    y_obs: np.ndarray,
    y_cf: np.ndarray,
    intervention_t: Any,
    output_dir: str | Path,
    stem: str,
    title: str,
    ylabel: str,
    summary_text: Dict[str, str],
    cumulative: Optional[np.ndarray] = None,
    y_cf_lower: Optional[np.ndarray] = None,
    y_cf_upper: Optional[np.ndarray] = None,
    weights: Optional[pd.Series] = None,
) -> Dict[str, str]:
    """Write shareable chart assets.

    Observed series stays full-length. Counterfactual paths and uncertainty bands appear only from the intervention onward.
    """

    del cumulative  # Visual cumulative effect is recomputed from the intervention forward.
    plt = _import_matplotlib()
    out = _ensure_dir(output_dir)
    files: Dict[str, str] = {}
    t_list = list(t)
    intervention_index = min(max(t_list.index(intervention_t) if intervention_t in t_list else len(t_list) // 2, 0), max(len(t_list) - 1, 0))
    payload = _prepare_post_intervention_visuals(
        t=t_list,
        y_obs=np.asarray(y_obs, dtype=float),
        y_cf=np.asarray(y_cf, dtype=float),
        intervention_index=intervention_index,
        y_cf_lower=np.asarray(y_cf_lower, dtype=float) if y_cf_lower is not None else None,
        y_cf_upper=np.asarray(y_cf_upper, dtype=float) if y_cf_upper is not None else None,
    )

    line_svg = out / f"{stem}_treated_vs_counterfactual.svg"
    point_svg = out / f"{stem}_point_effect.svg"
    cum_svg = out / f"{stem}_cumulative_impact.svg"
    share_svg = out / f"{stem}_share_card.svg"
    _write_simple_line_chart_svg(t=t_list, payload=payload, title=title, ylabel=ylabel, output_path=line_svg)
    _write_simple_effect_svg(
        t=t_list,
        series=payload["point_effect_masked"],
        lower=payload.get("point_effect_lower_masked"),
        upper=payload.get("point_effect_upper_masked"),
        intervention_index=intervention_index,
        title=f"{title} - point effect",
        series_label="Point effect",
        output_path=point_svg,
    )
    _write_simple_effect_svg(
        t=t_list,
        series=payload["cumulative_effect_masked"],
        lower=payload.get("cumulative_effect_lower_masked"),
        upper=payload.get("cumulative_effect_upper_masked"),
        intervention_index=intervention_index,
        title=f"{title} - cumulative impact",
        series_label="Cumulative effect",
        output_path=cum_svg,
    )
    _write_simple_share_card_svg(t=t_list, payload=payload, summary_text=summary_text, output_path=share_svg)
    files["treated_vs_counterfactual_svg"] = str(line_svg)
    files["point_effect_svg"] = str(point_svg)
    files["cumulative_impact_svg"] = str(cum_svg)
    files["share_card_svg"] = str(share_svg)
    if weights is not None and not weights.empty:
        w_svg = out / f"{stem}_donor_contributions.svg"
        _write_simple_bar_svg(weights=weights, title=title, output_path=w_svg)
        files["donor_contributions_svg"] = str(w_svg)

    if plt is None:
        note = out / f"{stem}_plots_note.txt"
        note.write_text(
            "Matplotlib was not available, so tscfbench wrote SVG charts instead of PNGs. Install the starter path (`python -m pip install -e \".[starter]\"`) or add `matplotlib` to enable PNG assets.",
            encoding="utf-8",
        )
        files["note"] = str(note)
        return files

    line_png = out / f"{stem}_treated_vs_counterfactual.png"
    point_png = out / f"{stem}_point_effect.png"
    cum_png = out / f"{stem}_cumulative_impact.png"
    _render_counterfactual_figure(
        plt=plt,
        payload=payload,
        intervention_t=intervention_t,
        title=title,
        ylabel=ylabel,
        output_png=line_png,
        output_svg=line_svg,
    )
    files["treated_vs_counterfactual_png"] = str(line_png)

    _render_single_effect_figure(
        plt=plt,
        t=t_list,
        post_t=payload["post_t"],
        series_post=payload["point_effect_post"],
        lower_post=payload.get("point_effect_lower_post"),
        upper_post=payload.get("point_effect_upper_post"),
        intervention_t=intervention_t,
        title=f"{title} - point effect",
        ylabel="Point effect",
        label="Point effect",
        output_png=point_png,
        output_svg=point_svg,
    )
    files["point_effect_png"] = str(point_png)

    _render_single_effect_figure(
        plt=plt,
        t=t_list,
        post_t=payload["post_t"],
        series_post=payload["cumulative_effect_post"],
        lower_post=payload.get("cumulative_effect_lower_post"),
        upper_post=payload.get("cumulative_effect_upper_post"),
        intervention_t=intervention_t,
        title=f"{title} - cumulative impact",
        ylabel="Cumulative effect",
        label="Cumulative effect",
        output_png=cum_png,
        output_svg=cum_svg,
    )
    files["cumulative_impact_png"] = str(cum_png)

    if weights is not None and not weights.empty:
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        weights.sort_values(ascending=False).plot(kind="bar", ax=ax)
        ax.set_title(f"{title} - donor contributions")
        ax.set_ylabel("Weight")
        ax.grid(axis="y", alpha=0.2)
        w_png = out / f"{stem}_donor_contributions.png"
        fig.tight_layout()
        fig.savefig(w_png, dpi=160)
        plt.close(fig)
        files["donor_contributions_png"] = str(w_png)

    fig = plt.figure(figsize=(11.2, 4.6))
    ax = fig.add_axes([0.05, 0.15, 0.42, 0.70])
    ax.plot(t_list, payload["y_obs"], linewidth=2.1, color="#111827", label="Observed")
    ax.plot(payload["post_t"], payload["y_cf_post"], linewidth=2.1, color="#f97316", linestyle="--", label="Counterfactual (post)")
    if "y_cf_lower_post" in payload and "y_cf_upper_post" in payload:
        ax.fill_between(payload["post_t"], payload["y_cf_lower_post"], payload["y_cf_upper_post"], color="#fdba74", alpha=0.45)
    ax.axvline(intervention_t, linestyle="--", linewidth=1.3, color="#6b7280")
    ax.set_title(summary_text["title"])
    ax.grid(alpha=0.18)
    ax.legend(loc="best")
    fig.text(0.54, 0.80, summary_text["badge"], fontsize=12, weight="bold")
    fig.text(0.54, 0.62, summary_text["summary"], fontsize=12)
    fig.text(0.54, 0.36, summary_text["takeaway"], fontsize=15, weight="bold", wrap=True)
    fig.text(0.54, 0.18, "Generated by tscfbench", fontsize=10)
    share_png = out / f"{stem}_share_card.png"
    fig.savefig(share_png, dpi=170)
    plt.close(fig)
    files["share_card_png"] = str(share_png)
    return files


def write_panel_visual_bundle(
    case: PanelCase,
    report: PanelBenchmarkOutput,
    *,
    output_dir: str | Path,
    stem: str,
    title: str,
    ylabel: str,
    takeaway: Optional[str] = None,
) -> Dict[str, str]:
    frame = _series_frame_from_panel(case, report)
    weights = None
    meta = report.prediction.meta or {}
    if meta.get("weights") is not None and meta.get("control_units") is not None:
        weights = pd.Series(np.asarray(meta["weights"], dtype=float), index=list(meta["control_units"]))
    m = report.metrics
    summary = f"post/pre RMSPE ratio: {m.get('post_pre_rmspe_ratio', float('nan')):.2f}; cumulative effect: {m.get('cum_effect', float('nan')):.2f}"
    card = _share_card_text(
        title=title,
        summary=summary,
        takeaway=takeaway or "A one-command counterfactual study can produce both a report and a shareable figure.",
        badge="Panel counterfactual demo",
    )
    return write_prediction_visuals(
        t=frame["t"],
        y_obs=frame["y_obs"].to_numpy(dtype=float),
        y_cf=frame["y_cf_mean"].to_numpy(dtype=float),
        y_cf_lower=frame["y_cf_lower"].to_numpy(dtype=float) if "y_cf_lower" in frame.columns else None,
        y_cf_upper=frame["y_cf_upper"].to_numpy(dtype=float) if "y_cf_upper" in frame.columns else None,
        intervention_t=_intervention_value(case),
        output_dir=output_dir,
        stem=stem,
        title=title,
        ylabel=ylabel,
        summary_text=card,
        cumulative=frame["cumulative_effect"].to_numpy(dtype=float),
        weights=weights,
    )


def write_impact_visual_bundle(
    case: ImpactCase,
    out: BenchmarkOutput,
    *,
    output_dir: str | Path,
    stem: str,
    title: str,
    ylabel: str,
    takeaway: Optional[str] = None,
) -> Dict[str, str]:
    frame = _series_frame_from_impact(case, out)
    m = out.metrics
    rmse = float(m.get("rmse", float("nan")))
    cum_series = frame["cumulative_effect"].dropna()
    cum_effect = float(cum_series.iloc[-1]) if len(cum_series) else float("nan")
    intervention = _intervention_value(case)
    intervention_index = list(frame["t"]).index(intervention) if intervention in set(frame["t"].tolist()) else int(getattr(case, "intervention_index", max(len(frame) // 2, 0)))
    post_points = max(int(len(frame) - intervention_index), 0)
    controls = len(case.x_cols)
    if np.isfinite(rmse):
        summary = f"RMSE: {rmse:.3f}; cumulative effect: {cum_effect:.2f}"
    else:
        summary = f"post-period points: {post_points}; cumulative effect: {cum_effect:.2f}; controls: {controls}"
    card = _share_card_text(
        title=title,
        summary=summary,
        takeaway=takeaway or "Counterfactual impact analysis is easier to explain when the default output includes a chart, not only JSON.",
        badge="Event impact demo",
    )
    return write_prediction_visuals(
        t=frame["t"],
        y_obs=frame["y_obs"].to_numpy(dtype=float),
        y_cf=frame["y_cf_mean"].to_numpy(dtype=float),
        y_cf_lower=frame["y_cf_lower"].to_numpy(dtype=float) if "y_cf_lower" in frame.columns else None,
        y_cf_upper=frame["y_cf_upper"].to_numpy(dtype=float) if "y_cf_upper" in frame.columns else None,
        intervention_t=intervention,
        output_dir=output_dir,
        stem=stem,
        title=title,
        ylabel=ylabel,
        summary_text=card,
        cumulative=frame["cumulative_effect"].to_numpy(dtype=float),
        weights=None,
    )


__all__ = [
    "write_panel_visual_bundle",
    "write_impact_visual_bundle",
]
