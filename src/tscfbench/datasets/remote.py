from __future__ import annotations

import os
import pathlib
import urllib.request
from typing import Callable, Optional, Sequence

import pandas as pd

from tscfbench.core import PanelCase
from tscfbench.datasets.fixtures import load_snapshot_panel


SourceMode = str


def _default_cache_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("TSCFBENCH_CACHE", pathlib.Path.home() / ".cache" / "tscfbench"))



def download_text(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "tscfbench/0.7"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8")



def cached_download(urls: Sequence[str], cache_name: str, cache_dir: Optional[pathlib.Path] = None) -> pathlib.Path:
    cache_dir = cache_dir or _default_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / cache_name
    if path.exists() and path.stat().st_size > 0:
        return path

    last_err = None
    for url in urls:
        try:
            txt = download_text(url)
            path.write_text(txt, encoding="utf-8")
            return path
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    raise RuntimeError(f"Failed to download any of {len(urls)} URLs. Last error: {last_err}")



def _load_csv_with_fallback(urls: Sequence[str], cache_name: str) -> pd.DataFrame:
    path = cached_download(urls, cache_name=cache_name)
    return pd.read_csv(path)



def _normalize_germany(df: pd.DataFrame) -> pd.DataFrame:
    if "code" in df.columns:
        df = df.drop(columns=["code"])
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    for src, dst in [("country", "country"), ("year", "year"), ("gdp", "gdp")]:
        if dst not in df.columns and src in cols:
            rename[cols[src]] = dst
    if rename:
        df = df.rename(columns=rename)
    required = {"country", "year", "gdp"}
    if not required.issubset(df.columns):
        raise ValueError(f"Germany dataset is missing required columns: {sorted(required - set(df.columns))}")
    df = df.copy()
    df["year"] = df["year"].astype(int)
    df["gdp"] = df["gdp"].astype(float)
    return df.sort_values(["country", "year"]).reset_index(drop=True)



def _normalize_prop99(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    if "state" in cols:
        rename[cols["state"]] = "state"
    elif "locationdesc" in cols:
        rename[cols["locationdesc"]] = "state"
    if "year" in cols:
        rename[cols["year"]] = "year"
    if "packspercapita" in cols:
        rename[cols["packspercapita"]] = "cigsale"
    elif "cigsale" in cols:
        rename[cols["cigsale"]] = "cigsale"
    elif "data_value" in cols:
        rename[cols["data_value"]] = "cigsale"
    if "treated" in cols:
        rename[cols["treated"]] = "treated"
    df = df.rename(columns=rename)
    required = {"state", "year", "cigsale"}
    if not required.issubset(df.columns):
        raise ValueError("Could not normalize Proposition 99 columns to state/year/cigsale")
    df = df.copy()
    df["year"] = df["year"].astype(int)
    df["cigsale"] = df["cigsale"].astype(float)
    if "treated" in df.columns:
        df["treated"] = df["treated"].astype(int)
    return df.sort_values(["state", "year"]).reset_index(drop=True)



def _normalize_basque(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    rename = {}
    for src, dst in [("regionname", "region"), ("region", "region"), ("year", "year"), ("gdpcap", "gdpcap")]:
        if src in cols:
            rename[cols[src]] = dst
    df = df.rename(columns=rename)
    required = {"region", "year", "gdpcap"}
    if not required.issubset(df.columns):
        raise ValueError("Could not normalize Basque columns to region/year/gdpcap")
    df = df.copy()
    df["year"] = df["year"].astype(int)
    df["gdpcap"] = df["gdpcap"].astype(float)
    return df.sort_values(["region", "year"]).reset_index(drop=True)



def _with_meta(case: PanelCase, **extra: object) -> PanelCase:
    meta = dict(case.metadata)
    meta.update(extra)
    return PanelCase(
        df=case.df.copy(),
        unit_col=case.unit_col,
        time_col=case.time_col,
        y_col=case.y_col,
        treated_unit=case.treated_unit,
        intervention_t=case.intervention_t,
        y_cf_true=case.y_cf_true.copy() if case.y_cf_true is not None else None,
        metadata=meta,
    )



def _resolve_panel_dataset(
    *,
    dataset_id: str,
    source: SourceMode,
    urls: Sequence[str],
    cache_name: str,
    normalizer: Callable[[pd.DataFrame], pd.DataFrame],
    unit_col: str,
    time_col: str,
    y_col: str,
    treated_unit: str,
    intervention_t: int,
    title: str,
) -> PanelCase:
    source = str(source or "auto").lower().strip()
    if source not in {"auto", "remote", "snapshot"}:
        raise ValueError("source must be one of: auto, remote, snapshot")

    def _load_remote() -> PanelCase:
        df = normalizer(_load_csv_with_fallback(urls, cache_name=cache_name))
        return PanelCase(
            df=df,
            unit_col=unit_col,
            time_col=time_col,
            y_col=y_col,
            treated_unit=treated_unit,
            intervention_t=intervention_t,
            metadata={
                "dataset_id": dataset_id,
                "dataset_title": title,
                "data_source": "remote",
                "cache_name": cache_name,
            },
        )

    if source == "snapshot":
        return _with_meta(load_snapshot_panel(dataset_id), requested_source=source)
    if source == "remote":
        return _load_remote()

    try:
        return _load_remote()
    except Exception as exc:  # noqa: BLE001
        snap = load_snapshot_panel(dataset_id)
        return _with_meta(snap, requested_source="auto", remote_error=str(exc), remote_fallback=True)



def load_german_reunification(*, source: SourceMode = "auto") -> PanelCase:
    urls = [
        "https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/german_reunification.csv",
        "https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/datasets/german_reunification.csv",
        "https://raw.githubusercontent.com/jgreathouse9/mlsynth/main/basedata/german_reunification.csv",
    ]
    return _resolve_panel_dataset(
        dataset_id="german_reunification",
        source=source,
        urls=urls,
        cache_name="german_reunification.csv",
        normalizer=_normalize_germany,
        unit_col="country",
        time_col="year",
        y_col="gdp",
        treated_unit="West Germany",
        intervention_t=1990,
        title="German reunification",
    )



def load_california_prop99(*, source: SourceMode = "auto") -> PanelCase:
    urls = [
        "https://raw.githubusercontent.com/synth-inference/synthdid/master/data/california_prop99.csv",
        "https://raw.githubusercontent.com/synth-inference/synthdid/master/experiments/california_smoking/data/california_prop99.csv",
        "https://raw.githubusercontent.com/jehangiramjad/tslib/master/tests/testdata/prop99.csv",
        "https://raw.githubusercontent.com/tom-beer/Synthetic-Control-Examples/master/Data/prop99.csv",
    ]
    return _resolve_panel_dataset(
        dataset_id="california_prop99",
        source=source,
        urls=urls,
        cache_name="california_prop99.csv",
        normalizer=_normalize_prop99,
        unit_col="state",
        time_col="year",
        y_col="cigsale",
        treated_unit="California",
        intervention_t=1989,
        title="California Proposition 99",
    )



def load_basque_country(*, source: SourceMode = "auto") -> PanelCase:
    urls = [
        "https://raw.githubusercontent.com/sdfordham/pysyncon/main/data/basque.csv",
        "https://raw.githubusercontent.com/sdfordham/pysyncon/main/examples/basque.csv",
        "https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/basque.csv",
    ]
    return _resolve_panel_dataset(
        dataset_id="basque_country",
        source=source,
        urls=urls,
        cache_name="basque_country.csv",
        normalizer=_normalize_basque,
        unit_col="region",
        time_col="year",
        y_col="gdpcap",
        treated_unit="Basque Country (Pais Vasco)",
        intervention_t=1970,
        title="Basque Country terrorism",
    )


__all__ = [
    "cached_download",
    "download_text",
    "load_basque_country",
    "load_california_prop99",
    "load_german_reunification",
]
