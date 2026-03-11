from __future__ import annotations

from typing import List

import pandas as pd

from tscfbench.markdown_utils import dataframe_to_markdown
from tscfbench.core import PanelCase
from tscfbench.protocols import PanelBenchmarkOutput


def _fmt(x) -> str:
    try:
        return f"{float(x):.4f}"
    except Exception:  # noqa: BLE001
        return str(x)


def _head_markdown(df: pd.DataFrame, n: int = 8) -> str:
    if df is None or df.empty:
        return "_none_"
    return dataframe_to_markdown(df, index=False, max_rows=n)


def render_panel_markdown(case: PanelCase, report: PanelBenchmarkOutput) -> str:
    m = report.metrics
    lines: List[str] = []
    lines.append(f"# Panel benchmark report: {case.metadata.get('dataset_id', 'unnamed')}")
    lines.append("")
    lines.append(f"- treated unit: `{case.treated_unit}`")
    lines.append(f"- intervention: `{case.intervention_t}`")
    lines.append(f"- model: `{report.metadata.get('model_name', 'unknown')}`")
    lines.append("")
    lines.append("## Main fit statistics")
    lines.append("")
    lines.append(f"- pre RMSPE: {_fmt(m.get('pre_rmspe'))}")
    lines.append(f"- post RMSPE: {_fmt(m.get('post_rmspe'))}")
    lines.append(f"- post/pre RMSPE ratio: {_fmt(m.get('post_pre_rmspe_ratio'))}")
    lines.append(f"- cumulative effect: {_fmt(m.get('cum_effect'))}")
    lines.append(f"- average effect: {_fmt(m.get('avg_effect'))}")
    if "space_placebo_pvalue" in m:
        lines.append(f"- space-placebo p-value: {_fmt(m.get('space_placebo_pvalue'))}")
    if "time_placebo_pvalue" in m:
        lines.append(f"- time-placebo p-value: {_fmt(m.get('time_placebo_pvalue'))}")
    lines.append("")
    lines.append("## Space placebos")
    lines.append("")
    lines.append(_head_markdown(report.space_placebos))
    lines.append("")
    lines.append("## Time placebos")
    lines.append("")
    lines.append(_head_markdown(report.time_placebos))
    lines.append("")
    return "\n".join(lines)
