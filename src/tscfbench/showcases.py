from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DataSourceCard:
    id: str
    title: str
    series_type: str
    loader: str
    what_you_get: List[str]
    good_for: List[str]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ShowcaseCase:
    id: str
    title: str
    theme: str
    why_it_has_attention: str
    question: str
    treated_series: str
    candidate_controls: List[str]
    recommended_workflow: str
    best_environment: str
    data_sources: List[str]
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_DATA_SOURCES: List[DataSourceCard] = [
    DataSourceCard(
        id="github_stars_api",
        title="GitHub stargazer history",
        series_type="daily attention / adoption",
        loader="load_github_star_history",
        what_you_get=["daily new stars", "daily cumulative stars", "repo metadata in frame attrs"],
        good_for=["repo virality", "open-source launch studies", "attention spillover around announcements"],
        notes=[
            "Uses the public GitHub stargazers endpoint with timestamp-aware media type.",
            "Great for high-attention open-source case studies such as OpenClaw-like repo surges.",
        ],
    ),
    DataSourceCard(
        id="gharchive_watch_events",
        title="GH Archive watch-event history",
        series_type="hourly or daily GitHub attention",
        loader="GH Archive / external preprocessing",
        what_you_get=["public GitHub event stream", "watch events at scale", "cross-repo comparison candidates"],
        good_for=["ecosystem-level star studies", "fake-star filtering research", "broad repo panels"],
        notes=["Useful when the native GitHub API is too rate-limited or when you want many repos at once."],
    ),
    DataSourceCard(
        id="coingecko_market_chart",
        title="CoinGecko market chart",
        series_type="crypto price / market cap / volume",
        loader="load_coingecko_market_chart",
        what_you_get=["historical prices", "market caps", "24h volume"],
        good_for=["crypto event studies", "listing news", "policy or ETF windows", "attention/price co-movement"],
        notes=["Daily data is a natural fit for event windows and quasi-experimental impact analysis."],
    ),
    DataSourceCard(
        id="fred_series",
        title="FRED commodity series",
        series_type="macro and commodity daily levels",
        loader="load_fred_series",
        what_you_get=["date/value pairs", "named public series such as WTI and Brent"],
        good_for=["oil shock studies", "macro controls", "commodity event windows"],
        notes=["WTI and Brent are especially useful because they naturally form treated/control pairs or spread-style controls."],
    ),
    DataSourceCard(
        id="lbma_gold",
        title="LBMA gold via DBnomics-compatible CSV",
        series_type="daily gold price levels",
        loader="load_csv_like_price_series",
        what_you_get=["daily gold prices", "multi-currency series when available"],
        good_for=["gold shock studies", "safe-haven behavior", "attention versus commodity price comparisons"],
        notes=["For tutorials, a CSV download or mirrored source is often the simplest path."],
    ),
]


_SHOWCASE_CASES: List[ShowcaseCase] = [
    ShowcaseCase(
        id="openclaw_stars",
        title="OpenClaw GitHub stars around major ecosystem events",
        theme="attention / open-source virality",
        why_it_has_attention=(
            "A fast-growing AI-agent repository with security news, ecosystem integrations, and large public visibility is exactly the kind"
            " of case that draws clicks, discussion, and reproducible benchmarking interest."
        ),
        question="How much additional GitHub-star growth arrived after a specific event window relative to a counterfactual built from peer repos or pre-trend dynamics?",
        treated_series="Daily new or cumulative stars for openclaw/openclaw.",
        candidate_controls=[
            "Peer agent repos with similar audiences but no event on the same day.",
            "A synthetic control built from multiple comparable repos.",
            "Search-interest proxies or broader GitHub AI-agent category activity when available.",
        ],
        recommended_workflow="Use the GitHub star-history loader, aggregate to daily counts, then run an impact-style or panel-style event study around launches, integrations, or security incidents.",
        best_environment="notebook + CLI report",
        data_sources=["github_stars_api", "gharchive_watch_events"],
        notes=[
            "This is one of the most naturally viral demo cases because the outcome variable is public attention itself.",
            "Be careful about fake-star contamination if you study broad repo panels rather than one well-known repo.",
        ],
    ),
    ShowcaseCase(
        id="repo_virality_panel",
        title="Predict or explain GitHub repo breakout trajectories",
        theme="attention / platform dynamics",
        why_it_has_attention="People love seeing which repos broke out, when they broke out, and whether a launch or endorsement actually changed the slope.",
        question="What would star growth have looked like without the launch event, ranking spike, or major influencer amplification?",
        treated_series="Daily stars for one focal repo.",
        candidate_controls=[
            "Repos in the same topic/language band.",
            "Repos launched in the same quarter but without the focal event.",
            "A donor pool built from several non-treated peers.",
        ],
        recommended_workflow="Build a repo panel from GitHub stars or GH Archive watch events, then use synthetic control or DiD-style comparisons around announcement dates.",
        best_environment="CLI + shared server",
        data_sources=["github_stars_api", "gharchive_watch_events"],
        notes=["This is a strong fit if you want media-friendly charts and a benchmark that travels well on social media."],
    ),
    ShowcaseCase(
        id="crypto_event_impact",
        title="Crypto price and volume around major events",
        theme="markets / public attention",
        why_it_has_attention="Crypto already has a built-in audience, and event windows translate naturally into counterfactual questions.",
        question="How would price, volume, or market cap have evolved without the event window?",
        treated_series="Daily price or log-return series for a focal coin such as BTC or ETH.",
        candidate_controls=[
            "Peer assets in the same category.",
            "Market-wide crypto index proxies.",
            "Volume or dominance controls depending on the event type.",
        ],
        recommended_workflow="Fetch CoinGecko market-chart data, transform prices into returns when appropriate, and run an event-style ImpactCase with peer controls.",
        best_environment="notebook + markdown report",
        data_sources=["coingecko_market_chart"],
        notes=[
            "For methodological credibility, returns or spreads are often better outcomes than raw price levels.",
            "This case is useful both for research and for attracting broader user attention to the package.",
        ],
    ),
    ShowcaseCase(
        id="gold_oil_shocks",
        title="Gold, WTI, and Brent around macro or geopolitical shocks",
        theme="commodities / macro events",
        why_it_has_attention="Commodity events are easy to explain to a broad audience and already have a large data and media ecosystem.",
        question="How far did gold or oil deviate from a control-based counterfactual around the shock window?",
        treated_series="Daily gold, WTI, or Brent price series.",
        candidate_controls=[
            "Use Brent as a control for WTI, or vice versa.",
            "Use gold together with dollar or oil controls depending on the shock.",
            "Use broader macro controls when you want a richer counterfactual model.",
        ],
        recommended_workflow="Load commodity series from FRED or CSV mirrors, align series on date, and build event windows around the macro shock of interest.",
        best_environment="notebook, teaching, public write-up",
        data_sources=["fred_series", "lbma_gold"],
        notes=["This is a strong demonstration case when you want the package to feel relevant beyond the GitHub/AI crowd."],
    ),
]


def public_data_sources() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _DATA_SOURCES]



def high_traffic_cases() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _SHOWCASE_CASES]



def _md_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)



def render_public_data_sources_markdown() -> str:
    lines: List[str] = [
        "# Public data sources for high-attention case studies",
        "",
        "These sources are useful when you want a demo or benchmark case that feels timely, public-facing, and easy to explain.",
        "",
    ]
    for card in _DATA_SOURCES:
        lines.extend([
            f"## {card.title}",
            "",
            f"**Series type:** {card.series_type}",
            "",
            f"**Loader:** {card.loader}",
            "",
            "**What you get**",
            "",
            _md_list(card.what_you_get),
            "",
            "**Good for**",
            "",
            _md_list(card.good_for),
            "",
            "**Notes**",
            "",
            _md_list(card.notes),
            "",
        ])
    return "\n".join(lines)



def render_high_traffic_cases_markdown() -> str:
    lines: List[str] = [
        "# High-traffic public cases",
        "",
        "These cases are chosen because they are both methodologically usable and public-facing enough to attract attention when you show the package.",
        "",
    ]
    for card in _SHOWCASE_CASES:
        lines.extend([
            f"## {card.title}",
            "",
            f"**Theme:** {card.theme}",
            "",
            f"**Why it has attention:** {card.why_it_has_attention}",
            "",
            f"**Counterfactual question:** {card.question}",
            "",
            f"**Treated series:** {card.treated_series}",
            "",
            "**Candidate controls**",
            "",
            _md_list(card.candidate_controls),
            "",
            f"**Recommended workflow:** {card.recommended_workflow}",
            "",
            f"**Best environment:** {card.best_environment}",
            "",
            f"**Data sources:** {', '.join(card.data_sources)}",
            "",
            "**Notes**",
            "",
            _md_list(card.notes),
            "",
        ])
    return "\n".join(lines)


__all__ = [
    "DataSourceCard",
    "ShowcaseCase",
    "high_traffic_cases",
    "public_data_sources",
    "render_high_traffic_cases_markdown",
    "render_public_data_sources_markdown",
]
