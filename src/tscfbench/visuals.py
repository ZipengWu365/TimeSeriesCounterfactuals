from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import numpy as np
import pandas as pd

from tscfbench.core import ImpactCase, PanelCase
from tscfbench.protocols import PanelBenchmarkOutput
from tscfbench.bench import BenchmarkOutput


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
    return report.prediction.to_frame(case.times, case.treated_series())


def _series_frame_from_impact(case: ImpactCase, out: BenchmarkOutput) -> pd.DataFrame:
    return out.prediction.to_frame(case.t, case.y_obs)


def _intervention_value(case: PanelCase | ImpactCase) -> Any:
    if isinstance(case, PanelCase):
        return case.intervention_t
    return case.intervention_t if case.intervention_t in set(case.t.tolist()) else case.t[case.intervention_index]


def _share_card_text(*, title: str, summary: str, takeaway: str, badge: str) -> Dict[str, str]:
    return {"title": title, "summary": summary, "takeaway": takeaway, "badge": badge}


def _fmt_tick(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 12 else text[:12] + "…"


def _normalize(values: np.ndarray, low: float, high: float) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    span = float(high - low)
    if not np.isfinite(span) or abs(span) < 1e-12:
        return np.full_like(arr, 0.5, dtype=float)
    return (arr - low) / span


def _svg_polyline(values: np.ndarray, *, x0: float, y0: float, width: float, height: float, low: float, high: float) -> str:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return ""
    xs = np.linspace(x0, x0 + width, num=arr.size)
    ys = y0 + height - _normalize(arr, low, high) * height
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys))


def _write_simple_line_chart_svg(*, t: list[Any], y_obs: np.ndarray, y_cf: np.ndarray, intervention_index: int, title: str, ylabel: str, output_path: Path) -> str:
    width, height = 960, 420
    left, top, plot_w, plot_h = 70, 70, 820, 260
    vals = np.concatenate([np.asarray(y_obs, dtype=float), np.asarray(y_cf, dtype=float)])
    low = float(np.nanmin(vals))
    high = float(np.nanmax(vals))
    pad = max(1e-6, 0.08 * (high - low if high != low else abs(high) + 1.0))
    low -= pad
    high += pad
    obs_points = _svg_polyline(np.asarray(y_obs, dtype=float), x0=left, y0=top, width=plot_w, height=plot_h, low=low, high=high)
    cf_points = _svg_polyline(np.asarray(y_cf, dtype=float), x0=left, y0=top, width=plot_w, height=plot_h, low=low, high=high)
    n = max(1, len(t) - 1)
    intervention_x = left + plot_w * (intervention_index / n)
    ticks = [0, len(t)//2 if len(t) > 2 else 0, len(t)-1]
    tick_labels = [escape(_fmt_tick(t[i])) for i in ticks]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)}</text>
  <text x="{left}" y="52" font-size="13" fill="#555">{escape(ylabel)}</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>
  <line x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}" stroke="#777"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#777"/>
  <polyline fill="none" stroke="#0f766e" stroke-width="2.6" points="{obs_points}"/>
  <polyline fill="none" stroke="#7c3aed" stroke-width="2.6" points="{cf_points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top+plot_h}" stroke="#111" stroke-dasharray="6 6"/>
  <text x="{intervention_x+6:.2f}" y="{top+16}" font-size="12" fill="#111">Intervention</text>
  <text x="{left}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[0]}</text>
  <text x="{left+plot_w/2-18:.2f}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[1]}</text>
  <text x="{left+plot_w-42:.2f}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[2]}</text>
  <rect x="{left}" y="{height-58}" width="12" height="12" fill="#0f766e"/>
  <text x="{left+18}" y="{height-48}" font-size="13">Observed</text>
  <rect x="{left+120}" y="{height-58}" width="12" height="12" fill="#7c3aed"/>
  <text x="{left+138}" y="{height-48}" font-size="13">Counterfactual</text>
</svg>'''
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)


def _write_simple_cumulative_svg(*, t: list[Any], cumulative: np.ndarray, intervention_index: int, title: str, output_path: Path) -> str:
    width, height = 960, 420
    left, top, plot_w, plot_h = 70, 70, 820, 260
    vals = np.asarray(cumulative, dtype=float)
    low = float(np.nanmin(vals))
    high = float(np.nanmax(vals))
    pad = max(1e-6, 0.08 * (high - low if high != low else abs(high) + 1.0))
    low -= pad
    high += pad
    points = _svg_polyline(vals, x0=left, y0=top, width=plot_w, height=plot_h, low=low, high=high)
    n = max(1, len(t) - 1)
    intervention_x = left + plot_w * (intervention_index / n)
    zero_y = top + plot_h - _normalize(np.asarray([0.0]), low, high)[0] * plot_h
    ticks = [0, len(t)//2 if len(t) > 2 else 0, len(t)-1]
    tick_labels = [escape(_fmt_tick(t[i])) for i in ticks]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)} — cumulative impact</text>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>
  <line x1="{left}" y1="{zero_y:.2f}" x2="{left+plot_w}" y2="{zero_y:.2f}" stroke="#999"/>
  <polyline fill="none" stroke="#dc2626" stroke-width="2.8" points="{points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top+plot_h}" stroke="#111" stroke-dasharray="6 6"/>
  <text x="{intervention_x+6:.2f}" y="{top+16}" font-size="12" fill="#111">Intervention</text>
  <text x="{left}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[0]}</text>
  <text x="{left+plot_w/2-18:.2f}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[1]}</text>
  <text x="{left+plot_w-42:.2f}" y="{top+plot_h+28}" font-size="12" fill="#444">{tick_labels[2]}</text>
</svg>'''
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
        f'<text x="{left}" y="32" font-size="24" font-weight="700">{escape(title)} — donor contributions</text>',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>',
    ]
    for i, (label, val) in enumerate(series.items()):
        x = left + i * (bar_w + gap)
        h = plot_h * (float(val) / max_v)
        y = top + plot_h - h
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{h:.2f}" fill="#2563eb"/>')
        parts.append(f'<text x="{x:.2f}" y="{top+plot_h+22}" font-size="10" fill="#444" transform="rotate(20 {x:.2f},{top+plot_h+22})">{escape(_fmt_tick(label))}</text>')
    parts.append('</svg>')
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return str(output_path)


def _write_simple_share_card_svg(*, t: list[Any], y_obs: np.ndarray, y_cf: np.ndarray, intervention_index: int, summary_text: Dict[str, str], output_path: Path) -> str:
    width, height = 1180, 480
    left, top, plot_w, plot_h = 60, 90, 420, 250
    vals = np.concatenate([np.asarray(y_obs, dtype=float), np.asarray(y_cf, dtype=float)])
    low = float(np.nanmin(vals))
    high = float(np.nanmax(vals))
    pad = max(1e-6, 0.08 * (high - low if high != low else abs(high) + 1.0))
    low -= pad
    high += pad
    obs_points = _svg_polyline(np.asarray(y_obs, dtype=float), x0=left, y0=top, width=plot_w, height=plot_h, low=low, high=high)
    cf_points = _svg_polyline(np.asarray(y_cf, dtype=float), x0=left, y0=top, width=plot_w, height=plot_h, low=low, high=high)
    n = max(1, len(t) - 1)
    intervention_x = left + plot_w * (intervention_index / n)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd" rx="10"/>
  <polyline fill="none" stroke="#0f766e" stroke-width="3" points="{obs_points}"/>
  <polyline fill="none" stroke="#7c3aed" stroke-width="3" points="{cf_points}"/>
  <line x1="{intervention_x:.2f}" y1="{top}" x2="{intervention_x:.2f}" y2="{top+plot_h}" stroke="#111" stroke-dasharray="6 6"/>
  <text x="{left}" y="48" font-size="24" font-weight="700">{escape(summary_text['title'])}</text>
  <text x="560" y="90" font-size="14" fill="#555">{escape(summary_text['badge'])}</text>
  <text x="560" y="150" font-size="18" font-weight="700">{escape(summary_text['summary'])}</text>
  <foreignObject x="560" y="210" width="540" height="170"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:22px;font-weight:700;color:#111;line-height:1.3;">{escape(summary_text['takeaway'])}</div></foreignObject>
  <text x="560" y="420" font-size="12" fill="#666">Generated by tscfbench</text>
</svg>'''
    output_path.write_text(svg, encoding="utf-8")
    return str(output_path)


def write_prediction_visuals(*, t: Iterable[Any], y_obs: np.ndarray, y_cf: np.ndarray, intervention_t: Any, output_dir: str | Path, stem: str, title: str, ylabel: str, summary_text: Dict[str, str], cumulative: Optional[np.ndarray] = None, y_cf_lower: Optional[np.ndarray] = None, y_cf_upper: Optional[np.ndarray] = None, weights: Optional[pd.Series] = None) -> Dict[str, str]:
    """Write shareable chart assets.

    If matplotlib is unavailable, tscfbench still writes SVG charts and share cards so the chart-first
    experience does not disappear on a minimal install. PNGs are added when matplotlib is available.
    """
    plt = _import_matplotlib()
    out = _ensure_dir(output_dir)
    files: Dict[str, str] = {}
    t_list = list(t)
    if cumulative is None:
        cumulative = np.cumsum(np.asarray(y_obs, dtype=float) - np.asarray(y_cf, dtype=float))
    intervention_index = min(max(t_list.index(intervention_t) if intervention_t in t_list else len(t_list)//2, 0), max(len(t_list)-1, 0))

    line_svg = out / f"{stem}_treated_vs_counterfactual.svg"
    cum_svg = out / f"{stem}_cumulative_impact.svg"
    share_svg = out / f"{stem}_share_card.svg"
    _write_simple_line_chart_svg(t=t_list, y_obs=np.asarray(y_obs, dtype=float), y_cf=np.asarray(y_cf, dtype=float), intervention_index=intervention_index, title=title, ylabel=ylabel, output_path=line_svg)
    _write_simple_cumulative_svg(t=t_list, cumulative=np.asarray(cumulative, dtype=float), intervention_index=intervention_index, title=title, output_path=cum_svg)
    _write_simple_share_card_svg(t=t_list, y_obs=np.asarray(y_obs, dtype=float), y_cf=np.asarray(y_cf, dtype=float), intervention_index=intervention_index, summary_text=summary_text, output_path=share_svg)
    files["treated_vs_counterfactual_svg"] = str(line_svg)
    files["cumulative_impact_svg"] = str(cum_svg)
    files["share_card_svg"] = str(share_svg)
    if weights is not None and not weights.empty:
        w_svg = out / f"{stem}_donor_contributions.svg"
        _write_simple_bar_svg(weights=weights, title=title, output_path=w_svg)
        files["donor_contributions_svg"] = str(w_svg)
    if plt is None:
        note = out / f"{stem}_plots_note.txt"
        note.write_text("Matplotlib was not available, so tscfbench wrote SVG charts instead of PNGs. Install the starter path (`python -m pip install -e \".[starter]\"`) or add `matplotlib` to enable PNG assets.", encoding="utf-8")
        files["note"] = str(note)
        return files

    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.plot(t_list, y_obs, label="Observed")
    ax.plot(t_list, y_cf, label="Counterfactual")
    if y_cf_lower is not None and y_cf_upper is not None:
        ax.fill_between(t_list, y_cf_lower, y_cf_upper, alpha=0.15, label="Interval")
    ax.axvline(intervention_t, linestyle="--", linewidth=1.5, label="Intervention")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.legend(loc="best")
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    line_png = out / f"{stem}_treated_vs_counterfactual.png"
    fig.tight_layout()
    fig.savefig(line_png, dpi=160)
    plt.close(fig)
    files["treated_vs_counterfactual_png"] = str(line_png)

    fig, ax = plt.subplots(figsize=(10, 5.0))
    ax.plot(t_list, cumulative, label="Cumulative effect")
    ax.axhline(0.0, linewidth=1)
    ax.axvline(intervention_t, linestyle="--", linewidth=1.5, label="Intervention")
    ax.set_title(f"{title} — cumulative impact")
    ax.set_ylabel("Cumulative effect")
    ax.legend(loc="best")
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    cum_png = out / f"{stem}_cumulative_impact.png"
    fig.tight_layout()
    fig.savefig(cum_png, dpi=160)
    plt.close(fig)
    files["cumulative_impact_png"] = str(cum_png)

    if weights is not None and not weights.empty:
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        weights.sort_values(ascending=False).plot(kind="bar", ax=ax)
        ax.set_title(f"{title} — donor contributions")
        ax.set_ylabel("Weight")
        ax.grid(axis="y", alpha=0.2)
        w_png = out / f"{stem}_donor_contributions.png"
        fig.tight_layout()
        fig.savefig(w_png, dpi=160)
        plt.close(fig)
        files["donor_contributions_png"] = str(w_png)

    fig = plt.figure(figsize=(11.2, 4.6))
    ax = fig.add_axes([0.05, 0.15, 0.42, 0.70])
    ax.plot(t_list, y_obs, linewidth=2, label="Observed")
    ax.plot(t_list, y_cf, linewidth=2, label="Counterfactual")
    ax.axvline(intervention_t, linestyle="--", linewidth=1.3)
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


def write_panel_visual_bundle(case: PanelCase, report: PanelBenchmarkOutput, *, output_dir: str | Path, stem: str, title: str, ylabel: str, takeaway: Optional[str] = None) -> Dict[str, str]:
    frame = _series_frame_from_panel(case, report)
    weights = None
    meta = report.prediction.meta or {}
    if meta.get("weights") is not None and meta.get("control_units") is not None:
        weights = pd.Series(np.asarray(meta["weights"], dtype=float), index=list(meta["control_units"]))
    m = report.metrics
    summary = f"post/pre RMSPE ratio: {m.get('post_pre_rmspe_ratio', float('nan')):.2f}; cumulative effect: {m.get('cum_effect', float('nan')):.2f}"
    card = _share_card_text(title=title, summary=summary, takeaway=takeaway or "A one-command counterfactual study can produce both a report and a shareable figure.", badge="Panel counterfactual demo")
    return write_prediction_visuals(t=frame["t"], y_obs=frame["y_obs"].to_numpy(dtype=float), y_cf=frame["y_cf_mean"].to_numpy(dtype=float), y_cf_lower=frame["y_cf_lower"].to_numpy(dtype=float) if "y_cf_lower" in frame.columns else None, y_cf_upper=frame["y_cf_upper"].to_numpy(dtype=float) if "y_cf_upper" in frame.columns else None, intervention_t=_intervention_value(case), output_dir=output_dir, stem=stem, title=title, ylabel=ylabel, summary_text=card, cumulative=frame["cumulative_effect"].to_numpy(dtype=float), weights=weights)


def write_impact_visual_bundle(case: ImpactCase, out: BenchmarkOutput, *, output_dir: str | Path, stem: str, title: str, ylabel: str, takeaway: Optional[str] = None) -> Dict[str, str]:
    frame = _series_frame_from_impact(case, out)
    m = out.metrics
    rmse = float(m.get('rmse', float('nan')))
    cum_effect = float(frame["cumulative_effect"].iloc[-1]) if len(frame) else float('nan')
    intervention = _intervention_value(case)
    intervention_index = list(frame["t"]).index(intervention) if intervention in set(frame["t"].tolist()) else int(getattr(case, 'intervention_index', max(len(frame)//2, 0)))
    post_points = max(int(len(frame) - intervention_index), 0)
    controls = len(case.x_cols)
    if np.isfinite(rmse):
        summary = f"RMSE: {rmse:.3f}; cumulative effect: {cum_effect:.2f}"
    else:
        summary = f"post-period points: {post_points}; cumulative effect: {cum_effect:.2f}; controls: {controls}"
    card = _share_card_text(title=title, summary=summary, takeaway=takeaway or "Counterfactual impact analysis is easier to explain when the default output includes a chart, not only JSON.", badge="Event impact demo")
    return write_prediction_visuals(t=frame["t"], y_obs=frame["y_obs"].to_numpy(dtype=float), y_cf=frame["y_cf_mean"].to_numpy(dtype=float), y_cf_lower=frame["y_cf_lower"].to_numpy(dtype=float) if "y_cf_lower" in frame.columns else None, y_cf_upper=frame["y_cf_upper"].to_numpy(dtype=float) if "y_cf_upper" in frame.columns else None, intervention_t=intervention, output_dir=output_dir, stem=stem, title=title, ylabel=ylabel, summary_text=card, cumulative=frame["cumulative_effect"].to_numpy(dtype=float), weights=None)


__all__ = ["write_panel_visual_bundle", "write_impact_visual_bundle"]
