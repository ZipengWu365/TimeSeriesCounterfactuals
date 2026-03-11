from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from tscfbench.core import PanelCase


_DATA_DIR = Path(__file__).resolve().parent / "data"


_SNAPSHOT_META: Dict[str, Dict[str, Any]] = {
    "german_reunification": {
        "filename": "german_reunification_snapshot.csv",
        "unit_col": "country",
        "time_col": "year",
        "y_col": "gdp",
        "treated_unit": "West Germany",
        "intervention_t": 1990,
        "title": "German reunification",
    },
    "california_prop99": {
        "filename": "california_prop99_snapshot.csv",
        "unit_col": "state",
        "time_col": "year",
        "y_col": "cigsale",
        "treated_unit": "California",
        "intervention_t": 1989,
        "title": "California Proposition 99",
    },
    "basque_country": {
        "filename": "basque_country_snapshot.csv",
        "unit_col": "region",
        "time_col": "year",
        "y_col": "gdpcap",
        "treated_unit": "Basque Country (Pais Vasco)",
        "intervention_t": 1970,
        "title": "Basque Country terrorism",
    },
}


def snapshot_path(dataset_id: str) -> Path:
    try:
        filename = _SNAPSHOT_META[dataset_id]["filename"]
    except KeyError as exc:
        raise KeyError(f"Unknown snapshot dataset_id: {dataset_id}") from exc
    return _DATA_DIR / filename



def has_snapshot(dataset_id: str) -> bool:
    try:
        return snapshot_path(dataset_id).exists()
    except KeyError:
        return False



def load_snapshot_panel(dataset_id: str) -> PanelCase:
    meta = dict(_SNAPSHOT_META[dataset_id])
    path = snapshot_path(dataset_id)
    df = pd.read_csv(path)
    return PanelCase(
        df=df,
        unit_col=meta["unit_col"],
        time_col=meta["time_col"],
        y_col=meta["y_col"],
        treated_unit=meta["treated_unit"],
        intervention_t=meta["intervention_t"],
        metadata={
            "dataset_id": dataset_id,
            "dataset_title": meta["title"],
            "data_source": "snapshot",
            "snapshot_path": str(path),
            "snapshot_kind": "ci_fixture",
            "snapshot_note": "Bundled CI-friendly snapshot matching the canonical schema; use source='remote' for a full mirror dataset.",
        },
    )


__all__ = ["has_snapshot", "load_snapshot_panel", "snapshot_path"]
