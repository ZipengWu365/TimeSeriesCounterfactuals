"""Datasets, cards, remote loaders, and public time-series helpers."""

from .catalog import DatasetCard, get_dataset_card, list_dataset_cards, load_named_dataset
from .fixtures import has_snapshot, load_snapshot_panel, snapshot_path
from .public_data import (
    PublicDataError,
    align_series_on_date,
    load_coingecko_market_chart,
    load_csv_like_price_series,
    load_fred_series,
    load_github_star_history,
    make_event_impact_case,
    to_log_returns,
)
from .remote import load_basque_country, load_california_prop99, load_german_reunification
from .synthetic import make_arma_impact, make_panel_latent_factor

__all__ = [
    "DatasetCard",
    "get_dataset_card",
    "list_dataset_cards",
    "load_named_dataset",
    "load_german_reunification",
    "load_california_prop99",
    "load_basque_country",
    "has_snapshot",
    "load_snapshot_panel",
    "snapshot_path",
    "make_arma_impact",
    "make_panel_latent_factor",
    "PublicDataError",
    "align_series_on_date",
    "load_github_star_history",
    "load_coingecko_market_chart",
    "load_fred_series",
    "load_csv_like_price_series",
    "to_log_returns",
    "make_event_impact_case",
]
