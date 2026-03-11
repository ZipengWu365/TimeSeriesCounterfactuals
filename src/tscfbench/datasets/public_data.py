from __future__ import annotations

import io
import json
import math
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

import numpy as np
import pandas as pd

from tscfbench.core import ImpactCase


USER_AGENT = "tscfbench/1.1"


class PublicDataError(RuntimeError):
    """Raised when a public data download or normalization step fails."""


def _open_url(url: str, *, headers: Optional[Mapping[str, str]] = None, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(dict(headers or {}))})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _json_url(url: str, *, headers: Optional[Mapping[str, str]] = None, timeout: int = 30) -> object:
    payload = _open_url(url, headers=headers, timeout=timeout)
    return json.loads(payload.decode("utf-8"))


def _csv_url(url: str, *, headers: Optional[Mapping[str, str]] = None, timeout: int = 30) -> pd.DataFrame:
    payload = _open_url(url, headers=headers, timeout=timeout)
    return pd.read_csv(io.BytesIO(payload))


def load_github_star_history(
    owner: str,
    repo: str,
    *,
    token: str | None = None,
    max_pages: int | None = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """Load daily GitHub stargazer history using the timestamp-aware stargazers endpoint.

    Returns a dataframe with columns:
    - date
    - stars_new
    - stars_cumulative
    """

    base = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
    headers: Dict[str, str] = {
        "Accept": "application/vnd.github.star+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    starred: List[str] = []
    page = 1
    while True:
        if max_pages is not None and page > max_pages:
            break
        url = f"{base}?per_page=100&page={page}"
        payload = _json_url(url, headers=headers, timeout=timeout)
        if not isinstance(payload, list):
            raise PublicDataError(f"Unexpected GitHub stargazers payload type: {type(payload)!r}")
        if not payload:
            break
        for item in payload:
            if isinstance(item, MutableMapping) and item.get("starred_at"):
                starred.append(str(item["starred_at"]))
        if len(payload) < 100:
            break
        page += 1

    if not starred:
        return pd.DataFrame(columns=["date", "stars_new", "stars_cumulative"])

    dates = pd.to_datetime(pd.Series(starred), utc=True).dt.tz_convert(None).dt.normalize()
    daily = dates.value_counts().sort_index().rename_axis("date").reset_index(name="stars_new")
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date").reset_index(drop=True)
    daily["stars_cumulative"] = daily["stars_new"].cumsum()
    daily.attrs["source"] = "github_stargazers"
    daily.attrs["owner"] = owner
    daily.attrs["repo"] = repo
    return daily


def load_coingecko_market_chart(
    coin_id: str,
    *,
    vs_currency: str = "usd",
    days: str | int = "max",
    interval: str | None = None,
    api_key: str | None = None,
    timeout: int = 30,
) -> pd.DataFrame:
    """Load historical price/market cap/volume from CoinGecko market_chart."""

    params = {"vs_currency": vs_currency, "days": str(days)}
    if interval:
        params["interval"] = interval
    url = f"https://api.coingecko.com/api/v3/coins/{urllib.parse.quote(coin_id)}/market_chart?{urllib.parse.urlencode(params)}"
    headers: Dict[str, str] = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    payload = _json_url(url, headers=headers, timeout=timeout)
    if not isinstance(payload, MutableMapping):
        raise PublicDataError(f"Unexpected CoinGecko payload type: {type(payload)!r}")

    def _frame(key: str, value_name: str) -> pd.DataFrame:
        rows = payload.get(key)
        if not isinstance(rows, list):
            raise PublicDataError(f"Missing key {key!r} in CoinGecko payload")
        df = pd.DataFrame(rows, columns=["timestamp_ms", value_name])
        df["date"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True).dt.tz_convert(None).dt.normalize()
        return df[["date", value_name]]

    prices = _frame("prices", "price")
    market_caps = _frame("market_caps", "market_cap")
    volumes = _frame("total_volumes", "total_volume")
    df = prices.merge(market_caps, on="date", how="outer").merge(volumes, on="date", how="outer")
    df = df.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    df.attrs["source"] = "coingecko_market_chart"
    df.attrs["coin_id"] = coin_id
    df.attrs["vs_currency"] = vs_currency
    return df


def load_fred_series(series_id: str, *, timeout: int = 30) -> pd.DataFrame:
    """Load a FRED series via the CSV graph endpoint."""

    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(series_id)}"
    df = _csv_url(url, timeout=timeout)
    cols = {c.lower(): c for c in df.columns}
    if "date" not in cols or "value" not in cols:
        # some FRED downloads use DATE / VALUE
        if "date" not in cols and "DATE" in df.columns:
            cols["date"] = "DATE"
        if "value" not in cols and "VALUE" in df.columns:
            cols["value"] = "VALUE"
    date_col = cols.get("date") or "DATE"
    value_col = cols.get("value") or "VALUE"
    df = df.rename(columns={date_col: "date", value_col: "value"})
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    df.attrs["source"] = "fred"
    df.attrs["series_id"] = series_id
    return df[["date", "value"]]


def load_csv_like_price_series(
    path_or_url: str,
    *,
    date_col: str = "date",
    value_col: str = "value",
    timeout: int = 30,
) -> pd.DataFrame:
    """Load a simple price series from a local CSV path or URL."""

    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        df = _csv_url(path_or_url, timeout=timeout)
    else:
        df = pd.read_csv(path_or_url)
    if date_col not in df.columns or value_col not in df.columns:
        raise PublicDataError(f"Expected columns {date_col!r} and {value_col!r}")
    out = df[[date_col, value_col]].rename(columns={date_col: "date", value_col: "value"}).copy()
    out["date"] = pd.to_datetime(out["date"])
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    out.attrs["source"] = "csv_like"
    out.attrs["path_or_url"] = path_or_url
    return out


def to_log_returns(df: pd.DataFrame, *, value_col: str = "value", out_col: str = "log_return") -> pd.DataFrame:
    out = df.copy()
    values = pd.to_numeric(out[value_col], errors="coerce").astype(float)
    out[out_col] = np.log(values).diff()
    return out


def align_series_on_date(
    outcome: pd.DataFrame,
    controls: Mapping[str, pd.DataFrame],
    *,
    outcome_col: str = "value",
    control_value_col: str = "value",
    join: str = "inner",
    fill_method: str | None = None,
) -> pd.DataFrame:
    """Align one outcome series and many control series on date.

    All dataframes must contain a `date` column.
    """

    if "date" not in outcome.columns:
        raise PublicDataError("Outcome dataframe must contain a 'date' column")
    merged = outcome[["date", outcome_col]].rename(columns={outcome_col: "y"}).copy()
    merged["date"] = pd.to_datetime(merged["date"])
    for name, ctrl in controls.items():
        if "date" not in ctrl.columns:
            raise PublicDataError(f"Control {name!r} is missing a 'date' column")
        piece = ctrl[["date", control_value_col]].rename(columns={control_value_col: name}).copy()
        piece["date"] = pd.to_datetime(piece["date"])
        merged = merged.merge(piece, on="date", how=join)
    merged = merged.sort_values("date").reset_index(drop=True)
    if fill_method:
        merged = merged.fillna(method=fill_method)
    return merged


def make_event_impact_case(
    outcome: pd.DataFrame,
    controls: Mapping[str, pd.DataFrame],
    *,
    intervention_t: str | pd.Timestamp,
    outcome_col: str = "value",
    control_value_col: str = "value",
    join: str = "inner",
    fill_method: str | None = None,
    metadata: Optional[Dict[str, object]] = None,
) -> ImpactCase:
    aligned = align_series_on_date(
        outcome,
        controls,
        outcome_col=outcome_col,
        control_value_col=control_value_col,
        join=join,
        fill_method=fill_method,
    )
    x_cols = [c for c in aligned.columns if c not in {"date", "y"}]
    intervention_ts = pd.Timestamp(intervention_t)
    mask = pd.to_datetime(aligned["date"]) == intervention_ts
    intervention_key: object
    meta = dict(metadata or {})
    meta.setdefault("intervention_time_value", intervention_ts.isoformat())
    if bool(mask.any()):
        intervention_key = int(np.flatnonzero(mask.to_numpy())[0])
    else:
        intervention_key = intervention_ts
    return ImpactCase(
        df=aligned,
        time_col="date",
        y_col="y",
        x_cols=x_cols,
        intervention_t=intervention_key,
        metadata=meta,
    )


__all__ = [
    "PublicDataError",
    "align_series_on_date",
    "load_coingecko_market_chart",
    "load_csv_like_price_series",
    "load_fred_series",
    "load_github_star_history",
    "make_event_impact_case",
    "to_log_returns",
]
