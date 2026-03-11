from __future__ import annotations

from typing import Iterable

import pandas as pd


def _escape(value: object) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def dataframe_to_markdown(df: pd.DataFrame | None, *, index: bool = False, max_rows: int | None = None) -> str:
    """Render a small markdown table without hard-failing on optional backends.

    pandas.DataFrame.to_markdown() depends on ``tabulate``. This helper keeps
    first-run paths working even if that optional import path is unavailable.
    """
    if df is None:
        return "_none_"
    view = df.head(max_rows) if max_rows is not None else df
    if view.empty:
        return "_none_"
    try:
        return view.to_markdown(index=index)
    except Exception:  # noqa: BLE001
        work = view.reset_index(drop=not index)
        headers = [_escape(col) for col in work.columns]
        lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for row in work.itertuples(index=False, name=None):
            lines.append("| " + " | ".join(_escape(v) for v in row) + " |")
        return "\n".join(lines)


__all__ = ["dataframe_to_markdown"]
