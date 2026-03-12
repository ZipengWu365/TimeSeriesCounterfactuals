from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from tscfbench.onramp import render_essential_commands_markdown, render_feedback_response_markdown, render_tool_profiles_markdown
from tscfbench.demo_cases import render_demo_gallery_markdown


@dataclass(frozen=True)
class PeerPackage:
    id: str
    display_name: str
    category: str
    primary_job: str
    documented_strengths: List[str]
    best_when: str
    how_tscfbench_relates: str
    reviewed_sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DifferentiatorCard:
    id: str
    title: str
    claim: str
    why_it_matters: str
    proof_points: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CoverageRow:
    id: str
    feature: str
    why_it_matters: str
    coverage: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_REVIEW_DATE = "2026-03-08"
_STATUS_LEGEND: Dict[str, str] = {
    "primary": "Primary documented focus",
    "native": "Native package feature",
    "bridge": "Bridge / adapter / benchmark wrapper",
    "partial": "Partial or adjacent documented support",
    "not_primary": "Not the primary documented package focus in reviewed materials",
}


_PEERS: List[PeerPackage] = [
    PeerPackage(
        id="tscfbench",
        display_name="tscfbench",
        category="benchmark + workflow + agent layer",
        primary_job="Define shared benchmark protocols across panel, impact, and forecast-as-counterfactual workflows; then package results for CLI, docs, CI, and agents.",
        documented_strengths=[
            "Canonical studies, sweep specs, and Markdown reports.",
            "Bridge layer over specialist estimator ecosystems instead of forcing one modeling family.",
            "Agent-native surfaces such as function tools, MCP, artifact handles, context plans, and repo maps.",
        ],
        best_when="You need a research workflow package, not just a single estimator package.",
        how_tscfbench_relates="This is the orchestration and dissemination layer. It complements, rather than replaces, specialist estimation packages.",
        reviewed_sources=[],
    ),
    PeerPackage(
        id="pysyncon",
        display_name="pysyncon",
        category="panel SCM family",
        primary_job="Implement classical, robust, augmented, and penalized synthetic control in Python.",
        documented_strengths=[
            "Multiple SCM variants.",
            "Placebo tests and confidence intervals.",
            "Examples reproducing landmark SCM studies.",
        ],
        best_when="You want a focused synthetic-control estimator package and are already committed to the SCM family.",
        how_tscfbench_relates="python -m tscfbench should use pysyncon as a specialist backend inside a broader benchmark protocol.",
        reviewed_sources=["https://pypi.org/project/pysyncon/", "https://github.com/sdfordham/pysyncon"],
    ),
    PeerPackage(
        id="scpi",
        display_name="SCPI",
        category="panel SCM inference",
        primary_job="Estimate synthetic controls with uncertainty quantification, including multiple treated units and staggered adoption settings.",
        documented_strengths=[
            "Prediction intervals and inference emphasis.",
            "Multiple treated units.",
            "Staggered adoption support.",
        ],
        best_when="You need synthetic-control inference, especially beyond the simplest one-treated-unit setup.",
        how_tscfbench_relates="python -m tscfbench should benchmark around SCPI and standardize how its outputs are compared against other families.",
        reviewed_sources=["https://pypi.org/project/scpi-pkg/", "https://github.com/nppackages/scpi"],
    ),
    PeerPackage(
        id="synthetic_control_methods",
        display_name="SyntheticControlMethods",
        category="panel SCM",
        primary_job="Offer a straightforward Python entry point for classical synthetic control workflows on panel data.",
        documented_strengths=[
            "Simple entry point for classical SCM.",
            "Germany reunification example and visualization workflow.",
        ],
        best_when="You want a direct Python SCM class with a classical workflow and lightweight mental model.",
        how_tscfbench_relates="python -m tscfbench can wrap it for recognizable benchmarks, but it is narrower than tscfbench's protocol and workflow scope.",
        reviewed_sources=["https://github.com/OscarEngelbrektson/SyntheticControlMethods"],
    ),
    PeerPackage(
        id="tfp_causalimpact",
        display_name="TFP CausalImpact",
        category="impact / BSTS",
        primary_job="Run CausalImpact-style Bayesian structural time-series analysis in Python via TensorFlow Probability.",
        documented_strengths=[
            "Direct CausalImpact framing.",
            "Bayesian impact analysis with intervals.",
            "Familiar pre-period / post-period workflow.",
        ],
        best_when="You specifically want CausalImpact-style impact analysis rather than a cross-method benchmark stack.",
        how_tscfbench_relates="python -m tscfbench should treat this as a specialist impact backend and compare it under a shared spec with simpler baselines and forecast-as-counterfactual routes.",
        reviewed_sources=["https://pypi.org/project/tfp-causalimpact/", "https://github.com/google/tfp-causalimpact"],
    ),
    PeerPackage(
        id="tfcausalimpact",
        display_name="tfcausalimpact",
        category="impact / BSTS",
        primary_job="Provide a TensorFlow Probability implementation of Google's CausalImpact algorithm with variational and HMC fitting options.",
        documented_strengths=[
            "Direct causal-impact workflow.",
            "Published performance trade-off between VI and HMC.",
            "Public fixtures and examples.",
        ],
        best_when="You want a standalone impact-analysis package with a familiar CausalImpact API.",
        how_tscfbench_relates="python -m tscfbench can wrap or benchmark around it, but its purpose is broader and more protocol-oriented.",
        reviewed_sources=["https://pypi.org/project/tfcausalimpact/", "https://github.com/WillianFuks/tfcausalimpact"],
    ),
    PeerPackage(
        id="cimpact",
        display_name="CImpact",
        category="impact / modular backends",
        primary_job="Offer modular impact analysis over multiple backends such as TensorFlow Probability, Prophet, and Pyro.",
        documented_strengths=[
            "Multiple impact-analysis backends.",
            "Explicit modular adapter architecture.",
            "Impact-oriented visualization and evaluation.",
        ],
        best_when="You want to stay inside impact analysis while comparing multiple backend model families.",
        how_tscfbench_relates="python -m tscfbench should treat CImpact as a backend family and add benchmark protocol, canonical studies, and agent/runtime packaging around it.",
        reviewed_sources=["https://github.com/Sanofi-Public/CImpact"],
    ),
    PeerPackage(
        id="causalpy",
        display_name="CausalPy",
        category="broad quasi-experimental",
        primary_job="Provide a broad Python package for quasi-experimental causal inference across designs such as synthetic control and regression discontinuity.",
        documented_strengths=[
            "Broad quasi-experimental scope.",
            "Bayesian and OLS workflows.",
            "Clear quickstart and model abstractions.",
        ],
        best_when="You need a broad quasi-experimental toolbox rather than a time-series counterfactual benchmark platform.",
        how_tscfbench_relates="python -m tscfbench is narrower methodologically but broader operationally: it focuses on time-series counterfactual benchmarking and agent-friendly workflow packaging.",
        reviewed_sources=["https://pypi.org/project/causalpy/", "https://github.com/pymc-labs/CausalPy"],
    ),
    PeerPackage(
        id="darts",
        display_name="Darts",
        category="forecasting",
        primary_job="Expose a user-friendly unified forecasting API spanning statistical and deep models, backtesting, and probabilistic forecasting.",
        documented_strengths=[
            "Unified fit/predict API.",
            "Probabilistic forecasting and backtesting.",
            "Many forecasting models and covariate support.",
        ],
        best_when="You want a general forecasting framework, especially for forecast-as-counterfactual experiments.",
        how_tscfbench_relates="python -m tscfbench uses Darts as a forecasting backend candidate, then adds counterfactual protocol, study specs, and agent/runtime packaging on top.",
        reviewed_sources=["https://github.com/unit8co/darts"],
    ),
    PeerPackage(
        id="statsforecast",
        display_name="StatsForecast",
        category="forecasting",
        primary_job="Scale statistical forecasting with fast fit/predict, probabilistic forecasts, and exogenous-variable support.",
        documented_strengths=[
            "Large-scale statistical forecasting.",
            "Prediction intervals.",
            "Exogenous variable support and distributed runtimes.",
        ],
        best_when="You need strong scalable forecasting baselines or forecast-as-counterfactual experiments over many series.",
        how_tscfbench_relates="python -m tscfbench should treat StatsForecast as a scalable baseline engine, then add causal benchmark protocol and dissemination surfaces around it.",
        reviewed_sources=["https://nixtlaverse.nixtla.io/statsforecast/", "https://github.com/Nixtla/statsforecast"],
    ),
]


_DIFFERENTIATORS: List[DifferentiatorCard] = [
    DifferentiatorCard(
        id="not_another_estimator",
        title="Protocol-first, not estimator-first",
        claim="python -m tscfbench is not trying to replace specialist estimators; it standardizes how you benchmark, compare, and package them.",
        why_it_matters="Researchers often need to compare panel SCM, impact/BSTS, and forecast-as-counterfactual workflows under one reproducible protocol.",
        proof_points=[
            "Shared case schema and prediction contract.",
            "Canonical benchmark specs and sweep specs.",
            "Adapters for specialist external ecosystems.",
        ],
    ),
    DifferentiatorCard(
        id="cross_ecosystem",
        title="Cross-ecosystem coverage",
        claim="python -m tscfbench spans panel synthetic control, impact analysis, and forecast-as-counterfactual instead of living inside one methodological silo.",
        why_it_matters="Real research programs rarely stay inside one library family from first benchmark to final paper or release.",
        proof_points=[
            "Panel baselines and canonical panel studies.",
            "Impact-case workflow and CausalImpact-style adapters.",
            "Forecast-as-counterfactual bridges to Darts and StatsForecast-class backends.",
        ],
    ),
    DifferentiatorCard(
        id="agent_native",
        title="Agent-native by design",
        claim="python -m tscfbench treats coding-agent workflows as a first-class target, not an afterthought.",
        why_it_matters="Modern research code increasingly runs through tool-calling assistants, MCP servers, and long multi-turn editing loops where token discipline matters.",
        proof_points=[
            "OpenAI function-tool export.",
            "Local MCP server surface.",
            "Repo maps, artifact handles, and context plans.",
        ],
    ),
    DifferentiatorCard(
        id="token_discipline",
        title="Token-aware workflow packaging",
        claim="python -m tscfbench is designed to reduce unnecessary context load by using bundles, manifests, digests, and artifact handles instead of giant free-form prompts.",
        why_it_matters="Prompt caching works best with stable prefixes and tool lists, while editing turns benefit from compact context rather than whole-repo dumps.",
        proof_points=[
            "Context pack + run digest pattern.",
            "Editing-vs-planning context plans.",
            "Artifact read/search/preview tools instead of full inlining.",
        ],
    ),
    DifferentiatorCard(
        id="release_surface",
        title="Release-facing docs and teaching surfaces",
        claim="python -m tscfbench bakes README, docs, benchmark cards, and tutorial order into the product rather than leaving communication until the end.",
        why_it_matters="Packages spread when researchers can understand them quickly, cite them, and reuse case studies without reverse-engineering the repo.",
        proof_points=[
            "GitHub-ready README generation.",
            "Docs landing pages and case-study pages.",
            "Notebook and tutorial bundles.",
        ],
    ),
]


_COVERAGE_ROWS: List[CoverageRow] = [
    CoverageRow(
        id="primary_scope",
        feature="Primary documented package scope",
        why_it_matters="This tells users what job each package is fundamentally built to do.",
        coverage={
            "tscfbench": "benchmark/workflow/agent",
            "pysyncon": "panel_scm",
            "scpi": "panel_scm_inference",
            "synthetic_control_methods": "panel_scm",
            "tfp_causalimpact": "impact_bsts",
            "tfcausalimpact": "impact_bsts",
            "cimpact": "impact_modular",
            "causalpy": "quasi_experimental",
            "darts": "forecasting",
            "statsforecast": "forecasting",
        },
    ),
    CoverageRow(
        id="panel_scm",
        feature="Panel synthetic-control workflows",
        why_it_matters="Core need for Germany / Prop99 / Basque-style comparative case studies.",
        coverage={
            "tscfbench": "native+bridge",
            "pysyncon": "primary",
            "scpi": "primary",
            "synthetic_control_methods": "primary",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "not_primary",
            "causalpy": "partial",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
    CoverageRow(
        id="impact_bsts",
        feature="Impact / BSTS event analysis",
        why_it_matters="Needed for CausalImpact-style counterfactual analyses with one treated series and controls.",
        coverage={
            "tscfbench": "native+bridge",
            "pysyncon": "not_primary",
            "scpi": "not_primary",
            "synthetic_control_methods": "not_primary",
            "tfp_causalimpact": "primary",
            "tfcausalimpact": "primary",
            "cimpact": "primary",
            "causalpy": "not_primary",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
    CoverageRow(
        id="forecast_cf",
        feature="Forecast-as-counterfactual route",
        why_it_matters="Useful when researchers want to benchmark forecasting models as counterfactual generators.",
        coverage={
            "tscfbench": "bridge",
            "pysyncon": "not_primary",
            "scpi": "not_primary",
            "synthetic_control_methods": "not_primary",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "partial",
            "causalpy": "not_primary",
            "darts": "primary",
            "statsforecast": "primary",
        },
    ),
    CoverageRow(
        id="canonical_studies",
        feature="Canonical benchmark studies and study runners",
        why_it_matters="A benchmark package is easier to trust and teach when it ships recognizable studies and report workflows.",
        coverage={
            "tscfbench": "native",
            "pysyncon": "partial",
            "scpi": "partial",
            "synthetic_control_methods": "partial",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "not_primary",
            "causalpy": "not_primary",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
    CoverageRow(
        id="json_specs_cli",
        feature="JSON-first experiment specs and CLI reproducibility",
        why_it_matters="This matters for CI, paper companions, and agent-driven reruns where notebook state is fragile.",
        coverage={
            "tscfbench": "native",
            "pysyncon": "not_primary",
            "scpi": "not_primary",
            "synthetic_control_methods": "not_primary",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "not_primary",
            "causalpy": "not_primary",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
    CoverageRow(
        id="agent_surface",
        feature="Agent tool / MCP / structured workflow surface",
        why_it_matters="This matters when research code is driven through tool-calling assistants instead of one-shot notebook sessions.",
        coverage={
            "tscfbench": "native",
            "pysyncon": "not_primary",
            "scpi": "not_primary",
            "synthetic_control_methods": "not_primary",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "not_primary",
            "causalpy": "not_primary",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
    CoverageRow(
        id="token_aware",
        feature="Token-aware artifact packaging and context planning",
        why_it_matters="Important for lower-cost, lower-latency agent use and cleaner editing turns.",
        coverage={
            "tscfbench": "native",
            "pysyncon": "not_primary",
            "scpi": "not_primary",
            "synthetic_control_methods": "not_primary",
            "tfp_causalimpact": "not_primary",
            "tfcausalimpact": "not_primary",
            "cimpact": "not_primary",
            "causalpy": "not_primary",
            "darts": "not_primary",
            "statsforecast": "not_primary",
        },
    ),
]


def peer_landscape() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _PEERS]


def package_differentiators() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _DIFFERENTIATORS]


def feature_coverage_matrix() -> List[Dict[str, Any]]:
    return [row.to_dict() for row in _COVERAGE_ROWS]


def ecosystem_audit() -> Dict[str, Any]:
    return {
        "name": "tscfbench ecosystem audit",
        "review_date": _REVIEW_DATE,
        "framing": (
            "The goal of this audit is not to claim that tscfbench supersedes specialist estimators. The goal is to clarify where"
            " specialist packages are strongest and where tscfbench adds a distinct benchmark, workflow, and agent-oriented layer."
        ),
        "legend": dict(_STATUS_LEGEND),
        "thesis": [
            "Use specialist packages when you need one estimator family deeply.",
            "Use tscfbench when you need shared protocols, recognizable benchmark studies, reproducible specs, or agent-friendly research workflows across families.",
            "The most accurate positioning is 'benchmark-and-workflow layer over specialist backends', not 'another estimator package'.",
        ],
        "peers": peer_landscape(),
        "differentiators": package_differentiators(),
        "coverage_matrix": feature_coverage_matrix(),
    }

from tscfbench.onramp import render_essential_commands_markdown, render_feedback_response_markdown, render_tool_profiles_markdown
from tscfbench.demo_cases import render_demo_gallery_markdown


def _md_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _format_status(value: str) -> str:
    mapping = {
        "native": "Native",
        "bridge": "Bridge",
        "partial": "Partial",
        "primary": "Primary",
        "not_primary": "Not primary",
        "native+bridge": "Native + bridge",
        "benchmark/workflow/agent": "Benchmark / workflow / agent",
        "panel_scm": "Panel SCM",
        "panel_scm_inference": "Panel SCM + inference",
        "impact_bsts": "Impact / BSTS",
        "impact_modular": "Impact / modular backends",
        "quasi_experimental": "Broad quasi-experimental",
        "forecasting": "Forecasting",
    }
    return mapping.get(value, value)


def render_differentiators_markdown() -> str:
    lines: List[str] = [
        "# Why tscfbench is different",
        "",
        "This page distills the main product-positioning claims for the package.",
        "",
    ]
    for card in _DIFFERENTIATORS:
        lines.extend([
            f"## {card.title}",
            "",
            card.claim,
            "",
            f"**Why it matters:** {card.why_it_matters}",
            "",
            "**Proof points**",
            "",
            _md_list(card.proof_points),
            "",
        ])
    return "\n".join(lines)


def render_ecosystem_audit_markdown() -> str:
    audit = ecosystem_audit()
    lines: List[str] = [
        "# Ecosystem audit",
        "",
        f"Reviewed on {audit['review_date']}.",
        "",
        audit["framing"],
        "",
        "## Core thesis",
        "",
        _md_list(list(audit["thesis"])),
        "",
        "## Reviewed packages",
        "",
    ]
    for peer in _PEERS:
        lines.extend([
            f"### {peer.display_name}",
            "",
            f"**Category:** {peer.category}",
            "",
            f"**Primary job:** {peer.primary_job}",
            "",
            "**Documented strengths**",
            "",
            _md_list(peer.documented_strengths),
            "",
            f"**Best when:** {peer.best_when}",
            "",
            f"**How tscfbench relates:** {peer.how_tscfbench_relates}",
            "",
        ])
        if peer.reviewed_sources:
            lines.extend([
                "**Reviewed sources**",
                "",
                _md_list(peer.reviewed_sources),
                "",
            ])
    return "\n".join(lines)


def render_feature_coverage_markdown() -> str:
    package_ids = [peer.id for peer in _PEERS]
    headers = ["feature"] + package_ids
    lines: List[str] = [
        "# Feature coverage matrix",
        "",
        "This matrix summarizes **primary documented focus** in reviewed public materials. It is not a proof that a package cannot do something beyond the table; it is a positioning aid for README and docs.",
        "",
        "## Legend",
        "",
        _md_list([f"**{_format_status(k)}** — {v}" for k, v in _STATUS_LEGEND.items()]),
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in _COVERAGE_ROWS:
        values = [row.feature] + [_format_status(row.coverage.get(pid, "not_primary")) for pid in package_ids]
        lines.append("| " + " | ".join(v.replace("|", "\\|") for v in values) + " |")
    lines.extend([
        "",
        "## Why these rows",
        "",
    ])
    for row in _COVERAGE_ROWS:
        lines.extend([
            f"### {row.feature}",
            "",
            row.why_it_matters,
            "",
        ])
    return "\n".join(lines)


def render_github_readme_markdown() -> str:
    lines: List[str] = [
        "# tscfbench (v1.8.0)",
        "",
        "![Python](https://img.shields.io/badge/python-3.10%2B-blue)",
        "![License](https://img.shields.io/badge/license-MIT-green)",
        "![Starter install](https://img.shields.io/badge/starter-install%20tested-success)",
        "![Charts](https://img.shields.io/badge/output-chart--first-orange)",
        "![Agents](https://img.shields.io/badge/agents-ready-purple)",
        "",
        "**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**",
        "",
        "![tscfbench quickstart hero](docs/assets/hero_quickstart.png)",
        "",
        "`tscfbench` is for the moment when a raw estimator is not enough: you want a chart, a report, a shareable package, and a machine-readable handoff under one reproducible spec.",
        "",
        "## When to use this instead of a single estimator package",
        "",
        "| If you need... | Use... |",
        "|---|---|",
        "| One specific estimator family and nothing else | a specialist package such as `tfcausalimpact`, `pysyncon`, `SCPI`, or `Darts` |",
        "| One workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs | `tscfbench` |",
        "| Something you can show a colleague or post online, not just model output | `tscfbench` |",
        "",
        "## 60-second quickstart",
        "",
        "```bash",
        "python -m pip install -e \".[starter]\"",
        "python -m tscfbench quickstart",
        "python -m tscfbench doctor",
        "```",
        "",
        "That path is the single recommended onboarding path in v1.8: built-in backends, bundled snapshot data, clean report generation in a fresh environment, and immediate chart/report/share assets.",
        "",
        "If you are installing from a release asset instead of a source checkout:",
        "",
        "```bash",
        "python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib",
        "python -m tscfbench quickstart",
        "```",
        "",
        "PyPI-first installation is prepared in this release, but the package is not published to PyPI from this environment.",
        "",
        "## What you get on the first run",
        "",
        _md_list([
            "A canonical study spec and results JSON.",
            "A Markdown report that works in a clean environment.",
            "Treated-vs-counterfactual, cumulative-impact, and share-card visuals.",
            "A `summary.json` file plus generated-files metadata and a narrow next-step path.",
        ]),
        "",
        "## Demo-first showcase",
        "",
        "![Demo mosaic](docs/assets/demo_mosaic.png)",
        "",
        '<table><tr><td><img src="docs/assets/demo_repo_breakout_share_card.png" alt="repo breakout" width="260"></td><td><img src="docs/assets/demo_detector_downtime_share_card.png" alt="detector downtime" width="260"></td><td><img src="docs/assets/demo_hospital_surge_share_card.png" alt="hospital surge" width="260"></td></tr></table>',
        "",
        "```bash",
        "python -m tscfbench demo repo-breakout",
        "python -m tscfbench demo detector-downtime",
        "python -m tscfbench demo hospital-surge",
        "python -m tscfbench demo minimum-wage-employment",
        "python -m tscfbench demo viral-attention",
        "```",
        "",
        "These are the five most internet-legible paths in the repo today: breakout attention, detector downtime, hospital pressure, wage-policy divergence, and viral-attention spikes.",
        "",
        "## Make something you can post online",
        "",
        "```bash",
        "python -m tscfbench make-share-package --demo-id repo-breakout",
        "python -m tscfbench make-share-package --demo-id detector-downtime",
        "```",
        "",
        "That command writes a share package with a chart, share card, report, summary JSON, citation block, and manifest.",
        "",
        "## Agent-first, but not agent-only",
        "",
        "You can use the package from CLI, notebooks, Python scripts, or tool-calling runtimes. For agent workflows, start with the smallest tool surface first.",
        "",
        "```bash",
        "python -m tscfbench export-openai-tools --profile starter -o openai_tools_starter.json",
        "python -m tscfbench list-tool-profiles",
        "```",
        "",
        "Use `starter` first. Promote to `minimal` or `research` only after the narrow path succeeds.",
        "",
        "## Try now",
        "",
        _md_list([
            "`docs/try-now.md` — zero-install gallery / Colab-ready entry points",
            "`docs/demo-gallery.md` — chart-first demos",
            "`docs/showcase-gallery.md` — share cards and downloadable example outputs",
            "`docs/plain-language-guide.md` — a non-jargon guide to counterfactual charts",
            "`docs/installation.md` — source checkout, wheel install, and PyPI-ready notes",
        ]),
        "",
        "## License",
        "",
        "MIT",
        "",
    ]
    return "\n".join(lines)


def render_docs_homepage_markdown() -> str:
    lines: List[str] = [
        "# tscfbench",
        "",
        "**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**",
        "",
        "![Quickstart hero](assets/hero_quickstart.png)",
        "",
        "This package is easiest to understand as a **counterfactual workflow product**: it helps you go from a question to a chart, a report, and a handoff artifact without inventing a one-off workflow every time.",
        "",
        "## First minute",
        "",
        "```bash",
        "python -m pip install -e \".[starter]\"",
        "python -m tscfbench quickstart",
        "python -m tscfbench doctor",
        "```",
        "",
        "The starter extra is the single recommended onboarding path. A release wheel is bundled with the release assets, and the package metadata is ready for PyPI publication once you push a live release.",
        "",
        "## Why not just install one estimator?",
        "",
        _md_list([
            "Use a specialist estimator when you already know the exact model family you want.",
            "Use `tscfbench` when you need one workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs.",
            "Use `tscfbench` when the deliverable matters as much as the model: chart, report, share package, and structured handoff.",
        ]),
        "",
        "## Start from your real question",
        "",
        "### I want the fastest possible first result",
        "",
        _md_list([
            "[Quickstart](quickstart.md)",
            "[Essential commands](essential-commands.md)",
            "[Doctor](doctor.md)",
        ]),
        "",
        "### I want a demo I can show another person",
        "",
        _md_list([
            "[Demo gallery](demo-gallery.md)",
            "[Showcase gallery](showcase-gallery.md)",
            "[Detector downtime tutorial](tutorials/detector-downtime.md)",
            "[Minimum-wage employment tutorial](tutorials/minimum-wage-employment.md)",
            "[Viral attention tutorial](tutorials/viral-attention.md)",
        ]),
        "",
        "### I want a no-jargon explanation",
        "",
        _md_list([
            "[Plain-language guide](plain-language-guide.md)",
            "[Try now](try-now.md)",
        ]),
        "",
        "### I care about coding agents and token cost",
        "",
        _md_list([
            "[Agent-first design](agent-first-design.md)",
            "[Tool profiles](tool-profiles.md)",
            "[Environment guide](environments.md)",
        ]),
        "",
    ]
    return "\n".join(lines)


def render_agent_first_design_markdown() -> str:
    lines: List[str] = [
        "# Agent-first design",
        "",
        "`tscfbench` is designed for researchers who increasingly work through coding agents, tool-calling runtimes, or editor agents.",
        "",
        "## Design principles",
        "",
        _md_list([
            "**Spec-first.** Prefer JSON specs over long free-form prompts.",
            "**Bundle-first.** Materialize manifests, digests, and artifact handles for each run.",
            "**Handle-first.** Read only the artifact slices you need.",
            "**Turn separation.** Keep planning/retrieval turns separate from compact editing turns.",
            "**Docs as tools.** Expose package explanation and comparison surfaces through CLI and tool schemas, not only prose.",
        ]),
        "",
        "## What that means in practice",
        "",
        _md_list([
            "`build-agent-bundle` writes a manifest, digest, context pack, and artifacts.",
            "`plan-context` assembles a bounded context plan for triage, analysis, editing, or reporting.",
            "`repo-map` gives agents a compact structural view of the repository.",
            "`export-openai-tools` and `mcp-server` expose the package as a tool surface.",
        ]),
        "",
        "## Why this should save tokens",
        "",
        _md_list([
            "Stable instructions and stable tool lists are easier to cache.",
            "Small artifact previews are cheaper than full data dumps.",
            "Editing turns work better when they only see the necessary files and diffs.",
        ]),
        "",
    ]
    return "\n".join(lines)


def render_github_readme_markdown() -> str:
    lines: List[str] = [
        "# tscfbench (v1.8.0)",
        "",
        "![Python](https://img.shields.io/badge/python-3.10%2B-blue)",
        "![License](https://img.shields.io/badge/license-MIT-green)",
        "![Starter install](https://img.shields.io/badge/starter-install%20tested-success)",
        "![Charts](https://img.shields.io/badge/output-chart--first-orange)",
        "![Agents](https://img.shields.io/badge/agents-ready-purple)",
        "",
        "**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**",
        "",
        "![tscfbench quickstart hero](docs/assets/hero_quickstart.png)",
        "",
        "`tscfbench` is for the moment when a raw estimator is not enough: you want a chart, a report, a shareable package, and a machine-readable handoff under one reproducible spec.",
        "",
        "## Python-first quickstart",
        "",
        "```python",
        "from tscfbench import run_demo",
        "",
        "result = run_demo(\"city-traffic\", output_dir=\"city_traffic_run\")",
        "result[\"summary\"]",
        "```",
        "",
        "Start here if the package is being read by a person rather than a shell script: import one function, run one demo, and inspect the summary while charts and reports are written to `city_traffic_run/`.",
        "",
        "## When to use this instead of a single estimator package",
        "",
        "| If you need... | Use... |",
        "|---|---|",
        "| One specific estimator family and nothing else | a specialist package such as `tfcausalimpact`, `pysyncon`, `SCPI`, or `Darts` |",
        "| One workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs | `tscfbench` |",
        "| Something you can show a colleague or post online, not just model output | `tscfbench` |",
        "",
        "## CLI quickstart",
        "",
        "```bash",
        "python -m pip install -e \".[starter]\"",
        "python -m tscfbench quickstart",
        "python -m tscfbench doctor",
        "```",
        "",
        "That path is the single recommended onboarding path in v1.8 when you want a fresh-environment smoke test with built-in backends, bundled snapshot data, and immediate chart/report/share assets.",
        "",
        "If you are installing from a release asset instead of a source checkout:",
        "",
        "```bash",
        "python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib",
        "python -m tscfbench quickstart",
        "```",
        "",
        "PyPI-first installation is prepared in this release, but the package is not published to PyPI from this environment.",
        "",
        "## Use your own data",
        "",
        "If you already have a CSV or DataFrame, the human-facing path is Python first and CLI second.",
        "",
        "### Panel data: one treated unit plus donor pool",
        "",
        "```python",
        "import pandas as pd",
        "from tscfbench import run_panel_data",
        "",
        "df = pd.read_csv(\"my_panel.csv\")",
        "result = run_panel_data(",
        "    df,",
        "    unit_col=\"city\",",
        "    time_col=\"date\",",
        "    y_col=\"traffic_index\",",
        "    treated_unit=\"Harbor City\",",
        "    intervention_t=\"2024-03-06\",",
        "    output_dir=\"my_panel_run\",",
        ")",
        "",
        "result[\"summary\"]",
        "```",
        "",
        "CLI equivalent:",
        "",
        "```bash",
        "python -m tscfbench run-csv-panel my_panel.csv --unit-col city --time-col date --y-col traffic_index --treated-unit \"Harbor City\" --intervention-t 2024-03-06 --output my_panel_run",
        "```",
        "",
        "### Impact data: one treated series plus controls",
        "",
        "```python",
        "import pandas as pd",
        "from tscfbench import run_impact_data",
        "",
        "df = pd.read_csv(\"my_impact.csv\")",
        "result = run_impact_data(",
        "    df,",
        "    time_col=\"date\",",
        "    y_col=\"signups\",",
        "    x_cols=[\"peer_signups\", \"search_interest\"],",
        "    intervention_t=\"2024-04-23\",",
        "    output_dir=\"my_impact_run\",",
        ")",
        "",
        "result[\"summary\"]",
        "```",
        "",
        "CLI equivalent:",
        "",
        "```bash",
        "python -m tscfbench run-csv-impact my_impact.csv --time-col date --y-col signups --x-cols peer_signups search_interest --intervention-t 2024-04-23 --output my_impact_run",
        "```",
        "",
        "## What you get on the first run",
        "",
        _md_list([
            "A canonical study spec and results JSON.",
            "A Markdown report that works in a clean environment.",
            "Treated-vs-counterfactual, cumulative-impact, and share-card visuals.",
            "A `summary.json` file plus generated-files metadata and a narrow next-step path.",
        ]),
        "",
        "## Demo-first showcase",
        "",
        "![Demo mosaic](docs/assets/demo_mosaic.png)",
        "",
        '<table><tr><td><img src="docs/assets/demo_repo_breakout_share_card.png" alt="repo breakout" width="260"></td><td><img src="docs/assets/demo_detector_downtime_share_card.png" alt="detector downtime" width="260"></td><td><img src="docs/assets/demo_hospital_surge_share_card.png" alt="hospital surge" width="260"></td></tr></table>',
        "",
        "```bash",
        "python -m tscfbench demo repo-breakout",
        "python -m tscfbench demo detector-downtime",
        "python -m tscfbench demo hospital-surge",
        "python -m tscfbench demo minimum-wage-employment",
        "python -m tscfbench demo viral-attention",
        "```",
        "",
        "These are the five most internet-legible paths in the repo today: breakout attention, detector downtime, hospital pressure, wage-policy divergence, and viral-attention spikes.",
        "",
        "## Make something you can post online",
        "",
        "```bash",
        "python -m tscfbench make-share-package --demo-id repo-breakout",
        "python -m tscfbench make-share-package --demo-id detector-downtime",
        "```",
        "",
        "That command writes a share package with a chart, share card, report, summary JSON, citation block, and manifest.",
        "",
        "## Agent-first, but not agent-only",
        "",
        "You can use the package from CLI, notebooks, Python scripts, or tool-calling runtimes. For agent workflows, start with the smallest tool surface first.",
        "",
        "```bash",
        "python -m tscfbench export-openai-tools --profile starter -o openai_tools_starter.json",
        "python -m tscfbench list-tool-profiles",
        "```",
        "",
        "Use `starter` first. Promote to `minimal` or `research` only after the narrow path succeeds.",
        "",
        "## Try now",
        "",
        _md_list([
            "`docs/try-now.md` - zero-install gallery / Colab-ready entry points",
            "`docs/demo-gallery.md` - chart-first demos",
            "`docs/showcase-gallery.md` - share cards and downloadable example outputs",
            "`docs/plain-language-guide.md` - a non-jargon guide to counterfactual charts",
            "`docs/installation.md` - source checkout, wheel install, and PyPI-ready notes",
        ]),
        "",
        "## License",
        "",
        "MIT",
        "",
    ]
    return "\n".join(lines)


def render_docs_homepage_markdown() -> str:
    lines: List[str] = [
        "# tscfbench",
        "",
        "**Turn a before/after time-series question into a counterfactual chart, a reproducible report, a share package, and an AI-agent-ready handoff.**",
        "",
        "![Quickstart hero](assets/hero_quickstart.png)",
        "",
        "This package is easiest to understand as a **counterfactual workflow product**: it helps you go from a question to a chart, a report, and a handoff artifact without inventing a one-off workflow every time.",
        "",
        "## Start in Python",
        "",
        "```python",
        "from tscfbench import run_demo",
        "",
        "result = run_demo(\"city-traffic\", output_dir=\"city_traffic_run\")",
        "result[\"summary\"]",
        "```",
        "",
        "This is the shortest human-facing example: import the package, run one function, and open the generated chart/report assets in `city_traffic_run/`.",
        "",
        "## Bring your own data in Python",
        "",
        "```python",
        "import pandas as pd",
        "from tscfbench import run_panel_data",
        "",
        "df = pd.read_csv(\"my_panel.csv\")",
        "result = run_panel_data(",
        "    df,",
        "    unit_col=\"city\",",
        "    time_col=\"date\",",
        "    y_col=\"traffic_index\",",
        "    treated_unit=\"Harbor City\",",
        "    intervention_t=\"2024-03-06\",",
        "    output_dir=\"my_panel_run\",",
        ")",
        "",
        "result[\"summary\"]",
        "```",
        "",
        "If your question is one treated series with controls instead of one treated unit with donor units, switch to `run_impact_data`. The full walkthrough is [Bring your own data](bring-your-own-data.md).",
        "",
        "## CLI quickstart",
        "",
        "```bash",
        "python -m pip install -e \".[starter]\"",
        "python -m tscfbench quickstart",
        "python -m tscfbench doctor",
        "```",
        "",
        "Use the CLI when you want the narrow install smoke test in a fresh environment. A release wheel is bundled with the release assets, and the package metadata is ready for PyPI publication once you push a live release.",
        "",
        "## Why not just install one estimator?",
        "",
        _md_list([
            "Use a specialist estimator when you already know the exact model family you want.",
            "Use `tscfbench` when you need one workflow surface across panel studies, event-style impact studies, demos, reports, and agent handoffs.",
            "Use `tscfbench` when the deliverable matters as much as the model: chart, report, share package, and structured handoff.",
        ]),
        "",
        "## Start from your real question",
        "",
        "### I want the fastest possible first result",
        "",
        _md_list([
            "[Quickstart](quickstart.md)",
            "[Bring your own data](bring-your-own-data.md)",
            "[Essential commands](essential-commands.md)",
            "[Doctor](doctor.md)",
        ]),
        "",
        "### I want a demo I can show another person",
        "",
        _md_list([
            "[Demo gallery](demo-gallery.md)",
            "[Showcase gallery](showcase-gallery.md)",
            "[Detector downtime tutorial](tutorials/detector-downtime.md)",
            "[Minimum-wage employment tutorial](tutorials/minimum-wage-employment.md)",
            "[Viral attention tutorial](tutorials/viral-attention.md)",
        ]),
        "",
        "### I want a no-jargon explanation",
        "",
        _md_list([
            "[Plain-language guide](plain-language-guide.md)",
            "[Try now](try-now.md)",
        ]),
        "",
        "### I care about coding agents and token cost",
        "",
        _md_list([
            "[Agent-first design](agent-first-design.md)",
            "[Tool profiles](tool-profiles.md)",
            "[Environment guide](environments.md)",
        ]),
        "",
    ]
    return "\n".join(lines)


def write_positioning_assets(output_dir: str | Path) -> Dict[str, Any]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    assets = {
        "README_GITHUB.md": render_github_readme_markdown(),
        "WEBSITE_HOME.md": render_docs_homepage_markdown(),
        "ECOSYSTEM_AUDIT.md": render_ecosystem_audit_markdown(),
        "FEATURE_COVERAGE.md": render_feature_coverage_markdown(),
        "WHY_TSCFBENCH.md": render_differentiators_markdown(),
        "AGENT_FIRST_DESIGN.md": render_agent_first_design_markdown(),
        "ESSENTIAL_COMMANDS.md": render_essential_commands_markdown(),
        "TOOL_PROFILES.md": render_tool_profiles_markdown(),
        "FEEDBACK_CHANGES.md": render_feedback_response_markdown(),
        "DEMO_GALLERY.md": render_demo_gallery_markdown(),
    }
    for name, text in assets.items():
        (root / name).write_text(text, encoding="utf-8")
    manifest = {
        "kind": "positioning_assets",
        "review_date": _REVIEW_DATE,
        "files": sorted(list(assets.keys())),
        "output_dir": str(root),
    }
    (root / "manifest.json").write_text(__import__("json").dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


__all__ = [
    "peer_landscape",
    "package_differentiators",
    "feature_coverage_matrix",
    "ecosystem_audit",
    "render_differentiators_markdown",
    "render_ecosystem_audit_markdown",
    "render_feature_coverage_markdown",
    "render_github_readme_markdown",
    "render_docs_homepage_markdown",
    "render_agent_first_design_markdown",
    "write_positioning_assets",
]
