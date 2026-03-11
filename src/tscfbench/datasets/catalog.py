from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from tscfbench.core import PanelCase
from tscfbench.datasets.fixtures import has_snapshot
from tscfbench.datasets.remote import (
    load_basque_country,
    load_california_prop99,
    load_german_reunification,
)


@dataclass(frozen=True)
class DatasetCard:
    id: str
    task_type: str
    title: str
    treated_unit: str
    intervention_t: int
    outcome: str
    summary: str
    source: str
    loader_name: str
    snapshot_available: bool = True
    remote_available: bool = True
    canonical: bool = True


_PANEL_DATASETS: Dict[str, tuple[DatasetCard, Callable[..., PanelCase]]] = {
    "german_reunification": (
        DatasetCard(
            id="german_reunification",
            task_type="panel",
            title="German reunification",
            treated_unit="West Germany",
            intervention_t=1990,
            outcome="GDP per capita",
            summary="Classic synthetic-control case study from comparative politics.",
            source="SyntheticControlMethods / scpi mirrors with bundled snapshot fallback",
            loader_name="load_german_reunification",
            snapshot_available=has_snapshot("german_reunification"),
        ),
        load_german_reunification,
    ),
    "california_prop99": (
        DatasetCard(
            id="california_prop99",
            task_type="panel",
            title="California Proposition 99",
            treated_unit="California",
            intervention_t=1989,
            outcome="Per-capita cigarette consumption",
            summary="Canonical tobacco-control synthetic-control benchmark.",
            source="synthdid / tslib mirrors with bundled snapshot fallback",
            loader_name="load_california_prop99",
            snapshot_available=has_snapshot("california_prop99"),
        ),
        load_california_prop99,
    ),
    "basque_country": (
        DatasetCard(
            id="basque_country",
            task_type="panel",
            title="Basque Country terrorism",
            treated_unit="Basque Country (Pais Vasco)",
            intervention_t=1970,
            outcome="GDP per capita",
            summary="Foundational SCM application based on the Basque conflict.",
            source="pysyncon / Synth-style mirrors with bundled snapshot fallback",
            loader_name="load_basque_country",
            snapshot_available=has_snapshot("basque_country"),
        ),
        load_basque_country,
    ),
}



def list_dataset_cards() -> List[DatasetCard]:
    return [card for card, _ in _PANEL_DATASETS.values()]



def get_dataset_card(dataset_id: str) -> DatasetCard:
    try:
        return _PANEL_DATASETS[dataset_id][0]
    except KeyError as exc:
        raise KeyError(f"Unknown dataset_id: {dataset_id}") from exc



def load_named_dataset(dataset_id: str, *, source: str = "auto") -> PanelCase:
    try:
        _, loader = _PANEL_DATASETS[dataset_id]
    except KeyError as exc:
        raise KeyError(f"Unknown dataset_id: {dataset_id}") from exc
    return loader(source=source)
