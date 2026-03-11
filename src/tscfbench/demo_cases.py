from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List

from tscfbench.csv_runner import run_csv_impact, run_csv_panel


@dataclass(frozen=True)
class DemoCase:
    id: str
    title: str
    family: str
    question: str
    scenario: str
    dataset_file: str
    outcome_col: str
    controls: List[str]
    unit_col: str | None = None
    treated_unit: str | None = None
    intervention_t: str = ""
    recommended_environment: str = "CLI or notebook"
    beginner_friendly: bool = True
    public_interest: bool = False
    domain: str = "general"
    takeaway: str = ""
    flagship: bool = False
    social_angle: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_DEMOS: List[DemoCase] = [
    DemoCase("city-traffic", "City traffic intervention", "panel", "Did the treated city diverge from its donor-pool counterfactual after the intervention?", "CSV in, report out: one treated city after a transport intervention.", "demo_city_traffic.csv", "traffic_index", [], unit_col="city", treated_unit="Harbor City", intervention_t="2024-03-06", domain="transport", takeaway="A single CSV can become a treated-vs-counterfactual chart, a placebo report, and a share card.", flagship=True, social_angle="Show a colleague how one transport change turned into a city-level counterfactual chart in one command."),
    DemoCase("product-launch", "Product launch signups", "impact", "How many extra daily signups appeared after the feature launch?", "One product launch, one treated metric, two control series.", "demo_product_launch.csv", "signups", ["peer_signups", "search_interest"], intervention_t="2024-04-23", domain="product", takeaway="Event-style counterfactual analysis is easier to explain when the output starts with a chart, not a wall of JSON.", flagship=True, social_angle="A launch story that product and growth teams can understand instantly."),
    DemoCase("heatwave-health", "Heatwave and ER visits", "impact", "How many excess ER visits appeared during the heatwave window?", "Medicine / public health demo using one hospital metric before and after an extreme-heat event.", "demo_heatwave_health.csv", "er_visits", ["nearby_city_er", "temperature_proxy"], intervention_t="2024-07-14", domain="medicine", takeaway="Cross-disciplinary demos make the package legible to scientists who do not start from synthetic-control jargon.", flagship=True, social_angle="A clean excess-visits chart is much easier to share than a methods-heavy policy benchmark."),
    DemoCase("electricity-shock", "Electricity demand after a grid shock", "panel", "How much did regional demand move after the grid shock?", "Engineering operations demo with one treated region and a donor pool of other regions.", "demo_electricity_shock.csv", "demand_mwh", [], unit_col="region", treated_unit="North Grid", intervention_t="2024-03-13", domain="engineering", takeaway="Engineering teams can treat plant outages and tariff changes as the same kind of event-study object.", social_angle="A plant-outage style example for operations and energy teams."),
    DemoCase("climate-grid", "Climate shock and grid demand", "panel", "How much extra demand hit the treated grid during the climate shock window?", "Climate + energy demo: one treated grid region during a heat-driven demand spike.", "demo_climate_grid.csv", "demand_mwh", [], unit_col="region", treated_unit="Coastal Grid", intervention_t="2024-08-11", domain="climate", takeaway="Climate-and-energy narratives are easier to share when the output is a treated-vs-counterfactual demand chart with donor contributions.", flagship=True, social_angle="A climate-grid story that works for energy researchers, utilities, and LinkedIn audiences."),
    DemoCase("hospital-surge", "Hospital surge during a respiratory outbreak", "impact", "How much ICU occupancy rose above counterfactual during the outbreak surge?", "Medicine demo: one hospital-system metric before and after a respiratory outbreak wave.", "demo_hospital_surge.csv", "icu_occupancy", ["nearby_icu", "respiratory_index"], intervention_t="2024-01-17", domain="medicine", takeaway="Medicine demos become easier to trust when the workflow writes a chart, a report, and a compact share package by default.", flagship=True, social_angle="An outbreak-surge case that reads like a hospital operations story, not a methods lecture."),
    DemoCase("github-stars", "GitHub repo breakout", "impact", "Did the launch create a real breakout in daily stars, or was growth already happening?", "Public-interest demo styled after a repo launch or security event.", "demo_github_stars.csv", "stars_new", ["peer_repo_a", "peer_repo_b"], intervention_t="2025-12-18", beginner_friendly=False, public_interest=True, domain="open_source", takeaway="Public demos are easier to share when the asset is a clean counterfactual chart with one sentence of interpretation.", social_angle="A GitHub/X story about breakout attention rather than raw star counts alone."),
    DemoCase("repo-breakout", "Repo breakout after a launch", "impact", "Was the repo's breakout real, or was it already on that path?", "Internet-native public demo for launch attention, GH stars, or repo adoption.", "demo_repo_breakout.csv", "repo_stars_new", ["peer_repo_a", "peer_repo_b"], intervention_t="2025-12-18", beginner_friendly=False, public_interest=True, domain="open_source", takeaway="A repo-breakout share card makes the package legible to internet audiences who may never read a benchmark appendix.", flagship=True, social_angle="The most shareable demo: was the launch a real breakout or just trend continuation?"),
    DemoCase("crypto-event", "Crypto event study", "impact", "How much of the BTC move looks event-driven rather than co-movement with the rest of the market?", "Public-interest demo for event-driven returns analysis.", "demo_crypto_event.csv", "btc_log_return", ["eth_log_return", "sol_log_return"], intervention_t="2023-12-15", beginner_friendly=False, public_interest=True, domain="markets", takeaway="A cumulative-impact chart makes market-event narratives much more legible than raw returns alone.", social_angle="A public market-event example that can travel well on social and in talks."),
    DemoCase("detector-downtime", "Detector downtime after a solar storm", "impact", "How much detector uptime was lost after the solar storm relative to a counterfactual path?", "Physics demo: one detector uptime series before and after a solar-storm event, with a reference detector and solar proxy as controls.", "demo_detector_downtime.csv", "uptime_pct", ["reference_detector_uptime", "solar_flux_proxy"], intervention_t="2024-05-18", domain="physics", takeaway="Physics users do not need to speak synthetic-control jargon to get a chart-first counterfactual workflow.", flagship=True, social_angle="A solar-storm downtime story makes the package legible outside policy and product analytics."),
    DemoCase("minimum-wage-employment", "Regional employment after a minimum-wage change", "panel", "Did the treated region's employment index diverge after the wage-policy change?", "Economics / social-science demo with one treated region and several donor regions.", "demo_minimum_wage_employment.csv", "employment_index", [], unit_col="region", treated_unit="Metro State", intervention_t="2024-08-04", domain="economics", takeaway="An economics-style policy question can start with one command and end with a donor-based counterfactual chart plus share package.", flagship=True, social_angle="A wage-policy chart is a more broadly legible social-science demo than canonical policy cases alone."),
    DemoCase("viral-attention", "Viral attention spike", "impact", "Was the public-attention spike a real breakout, or just continuation of the existing trend?", "Social-science / public-attention demo with one treated attention index and two peer-topic controls.", "demo_viral_attention.csv", "attention_index", ["peer_topic_a", "peer_topic_b"], intervention_t="2025-10-14", beginner_friendly=False, public_interest=True, domain="social_science", takeaway="Public-attention narratives become much easier to share when the default output is a counterfactual chart instead of a methods appendix.", flagship=True, social_angle="A viral-attention case turns social-science language into a chart people actually repost."),
]

_DOWNLOADS = {
    "city-traffic": "assets/downloads/city_traffic_share_package.zip",
    "heatwave-health": "assets/downloads/heatwave_health_share_package.zip",
    "climate-grid": "assets/downloads/climate_grid_share_package.zip",
    "hospital-surge": "assets/downloads/hospital_surge_share_package.zip",
    "repo-breakout": "assets/downloads/repo_breakout_share_package.zip",
    "detector-downtime": "assets/downloads/detector_downtime_share_package.zip",
    "minimum-wage-employment": "assets/downloads/minimum_wage_employment_share_package.zip",
    "viral-attention": "assets/downloads/viral_attention_share_package.zip",
}
_ASSET_MAP = {
    "city-traffic": "assets/demo_city_traffic_share_card.png",
    "product-launch": "assets/demo_product_launch_share_card.png",
    "heatwave-health": "assets/demo_heatwave_health_share_card.png",
    "electricity-shock": "assets/demo_electricity_shock_share_card.png",
    "climate-grid": "assets/demo_climate_grid_share_card.png",
    "hospital-surge": "assets/demo_hospital_surge_share_card.png",
    "github-stars": "assets/demo_github_stars_share_card.png",
    "repo-breakout": "assets/demo_repo_breakout_share_card.png",
    "crypto-event": "assets/demo_crypto_event_share_card.png",
    "detector-downtime": "assets/demo_detector_downtime_share_card.png",
    "minimum-wage-employment": "assets/demo_minimum_wage_employment_share_card.png",
    "viral-attention": "assets/demo_viral_attention_share_card.png",
}
_BEGINNER_EXAMPLES = [
    {"title": "School attendance after a snow closure", "what_goes_in": "One attendance series, a nearby-school control series, and the closure date.", "why_it_matters": "This is a direct before/after question that educators can understand without learning causal-inference jargon first.", "data_file": "demo_school_closure_attendance.csv"},
    {"title": "Retail foot traffic after a store redesign", "what_goes_in": "One treated store, several comparison stores, and the redesign date.", "why_it_matters": "It shows the panel path on a business problem that looks nothing like a canonical policy case.", "data_file": "demo_retail_foot_traffic.csv"},
    {"title": "Website conversions after a landing-page redesign", "what_goes_in": "One conversion series, peer conversions, search interest, and the redesign date.", "why_it_matters": "It is the plainest possible product-growth explanation of an impact workflow.", "data_file": "demo_website_redesign_conversions.csv"},
]

def demo_catalog() -> List[Dict[str, Any]]:
    return [demo.to_dict() for demo in _DEMOS]

def beginner_examples() -> List[Dict[str, Any]]:
    return list(_BEGINNER_EXAMPLES)

def get_demo_case(demo_id: str) -> DemoCase:
    key = str(demo_id).strip().lower()
    aliases = {"gh-stars": "github-stars", "repo-stars": "repo-breakout", "detector": "detector-downtime", "minimum-wage": "minimum-wage-employment", "viral": "viral-attention"}
    key = aliases.get(key, key)
    for demo in _DEMOS:
        if demo.id == key:
            return demo
    raise KeyError(f"Unknown demo id: {demo_id}")

def demo_data_path(demo_id: str) -> Path:
    demo = get_demo_case(demo_id)
    data_root = resources.files("tscfbench.datasets").joinpath("data")
    return Path(str(data_root.joinpath(demo.dataset_file)))

def run_demo(demo_id: str, *, output_dir: str | Path = "tscfbench_demo", plot: bool = True) -> Dict[str, Any]:
    demo = get_demo_case(demo_id)
    csv_path = demo_data_path(demo.id)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_dir = out / demo.id
    if demo.family == "panel":
        payload = run_csv_panel(csv_path, unit_col=str(demo.unit_col), time_col="date", y_col=demo.outcome_col, treated_unit=demo.treated_unit, intervention_t=demo.intervention_t, output_dir=run_dir, title=demo.title, plot=plot, takeaway=demo.takeaway)
    else:
        payload = run_csv_impact(csv_path, time_col="date", y_col=demo.outcome_col, x_cols=demo.controls, intervention_t=demo.intervention_t, output_dir=run_dir, title=demo.title, plot=plot, takeaway=demo.takeaway)
    payload.setdefault("visual_assets", {k: v for k, v in payload.get("generated_files", {}).items() if k.endswith("_png") or k.endswith("_svg")})
    payload["demo"] = demo.to_dict()
    return payload

def render_demo_gallery_markdown() -> str:
    flagship = [d for d in _DEMOS if d.flagship]
    lines: List[str] = ["# Demo gallery", "", "These demos are deliberately plain-language and shareable. They answer: *what can I show a colleague in one minute?*", "", "Every demo can write JSON, Markdown, SVG/PNG charts, and a social-share card. Flagship demos also have ready-made downloadable share packages.", "", "## Fastest beginner examples", ""]
    for ex in _BEGINNER_EXAMPLES:
        lines.extend([f"### {ex['title']}", "", f"- what goes in: {ex['what_goes_in']}", f"- why it matters: {ex['why_it_matters']}", f"- bundled example file: `{ex['data_file']}`", ""])
    lines.extend(["## Flagship shareable demos", "", "Use these first if you want a chart that is easy to explain outside the causal-inference community.", ""])
    for demo in flagship:
        lines.extend([f"### {demo.title}", "", demo.scenario, ""])
        asset = _ASSET_MAP.get(demo.id)
        if asset:
            lines.extend([f"![{demo.title}]({asset})", ""])
        lines.extend([f"- question: {demo.question}", f"- domain: `{demo.domain}`", f"- social angle: {demo.social_angle}", f"- intervention: `{demo.intervention_t}`", f"- family: `{demo.family}`", "", "```bash", f"python -m tscfbench demo {demo.id}", f"python -m tscfbench make-share-package --demo-id {demo.id}", "```", ""])
        if demo.id in _DOWNLOADS:
            lines.extend([f"- sample download: [{demo.id} share package]({_DOWNLOADS[demo.id]})", ""])
        lines.extend([f"Takeaway: {demo.takeaway}", ""])
    lines.extend(["## Full demo catalog", "", "Use the demos below when you want a fast domain-first example without starting from canonical policy studies.", ""])
    for demo in _DEMOS:
        lines.extend([f"### {demo.title}", "", f"- family: `{demo.family}`", f"- domain: `{demo.domain}`", f"- question: {demo.question}", f"- dataset file: `{demo.dataset_file}`", f"- beginner_friendly: `{demo.beginner_friendly}`", f"- public_interest: `{demo.public_interest}`", "", "```bash", f"python -m tscfbench demo {demo.id}", "```", ""])
    return "\n".join(lines)

__all__ = ["DemoCase", "beginner_examples", "demo_catalog", "demo_data_path", "get_demo_case", "render_demo_gallery_markdown", "run_demo"]
