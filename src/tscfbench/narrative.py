from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List
import json

from .guidebook import (
    render_benchmark_cards_markdown,
    render_start_here_markdown,
    render_workflow_recipes_markdown,
)
from .product import (
    api_handbook,
    render_api_handbook_markdown,
    render_environment_profiles_markdown,
    render_package_overview_markdown,
    render_use_cases_markdown,
)
from .onramp import (
    render_doctor_markdown,
    render_essential_commands_markdown,
    render_feedback_response_markdown,
    render_tool_profiles_markdown,
)


@dataclass(frozen=True)
class CapabilityArea:
    id: str
    title: str
    question_it_answers: str
    why_it_exists: str
    primary_apis: List[str]
    primary_cli: List[str]
    best_environments: List[str]
    outputs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScenarioCard:
    id: str
    title: str
    persona: str
    environment: str
    question: str
    where_tscfbench_helps: List[str]
    primary_apis: List[str]
    primary_cli: List[str]
    outputs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TutorialCard:
    id: str
    title: str
    audience: str
    best_environment: str
    time_to_first_result: str
    what_you_build: List[str]
    entry_points: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_PACKAGE_STORY: Dict[str, Any] = {
    "name": "tscfbench",
    "headline": "A benchmark-and-workflow package for time-series counterfactual inference.",
    "plain_language": (
        "python -m tscfbench helps you turn a counterfactual question into a reproducible study, a readable report, and a reusable workflow. "
        "It is not only a model package: it also provides benchmark protocols, canonical studies, teaching surfaces, and agent-friendly artifacts."
    ),
    "what_it_is": [
        "A stable schema for impact and panel counterfactual tasks.",
        "A benchmark layer for single studies, canonical studies, and model sweeps.",
        "A workflow layer for reports, notebooks, docs, CI, and coding-agent use.",
    ],
    "what_it_is_not": [
        "It is not a claim that one built-in baseline is the last word in methodology.",
        "It is not a giant all-in-one causal inference framework.",
        "It is not only a demo notebook; it is meant to survive in real research workflows.",
    ],
    "why_people_adopt_it": [
        "It starts from recognizable research jobs instead of source files.",
        "It tells users why each API exists, where it works best, and what it returns.",
        "It ships canonical studies, benchmark cards, tutorials, and release-facing docs.",
        "It is also designed for token-aware, agent-driven research workflows.",
    ],
}


_CAPABILITY_AREAS: List[CapabilityArea] = [
    CapabilityArea(
        id="orientation",
        title="Orientation and package framing",
        question_it_answers="What is this package and where should I start?",
        why_it_exists="Research packages are hard to adopt when a newcomer has to reverse-engineer the repo before they can run a first result.",
        primary_apis=["package_overview", "recommend_start_path", "workflow_recipes"],
        primary_cli=["python -m tscfbench intro", "python -m tscfbench start-here", "python -m tscfbench workflow-recipes"],
        best_environments=["docs site", "CLI", "teaching", "notebook onboarding"],
        outputs=["package mental model", "recommended first path", "onboarding reading order"],
    ),
    CapabilityArea(
        id="task-schema",
        title="Counterfactual task schema",
        question_it_answers="How do I express my own data so different models and workflows share one protocol?",
        why_it_exists="Counterfactual tooling is fragmented across panel, impact, and forecasting ecosystems; the schema layer keeps them interoperable.",
        primary_apis=["ImpactCase", "PanelCase", "PredictionResult"],
        primary_cli=["python -m tscfbench make-panel-spec"],
        best_environments=["notebook", "python script", "library integration"],
        outputs=["validated case objects", "shared prediction contract", "JSON specs"],
    ),
    CapabilityArea(
        id="single-study",
        title="Single-study benchmarking",
        question_it_answers="How do I run one interpretable benchmark with diagnostics instead of just a fitted curve?",
        why_it_exists="Researchers need metrics, placebo logic, and readable outputs, not only predictions.",
        primary_apis=["benchmark", "benchmark_panel", "PanelProtocolConfig", "render_panel_markdown"],
        primary_cli=["python -m tscfbench demo", "python -m tscfbench run-panel-spec", "python -m tscfbench render-panel-report"],
        best_environments=["notebook", "script", "CLI"],
        outputs=["metrics", "placebo tables", "markdown report"],
    ),
    CapabilityArea(
        id="canonical",
        title="Canonical benchmark studies",
        question_it_answers="How do I benchmark on recognizable cases that other researchers already know?",
        why_it_exists="A benchmark package becomes more legible when it ships with a small number of public landmark studies.",
        primary_apis=["CanonicalBenchmarkSpec", "run_canonical_benchmark", "render_canonical_markdown"],
        primary_cli=["python -m tscfbench make-canonical-spec", "python -m tscfbench run-canonical", "python -m tscfbench render-canonical-report"],
        best_environments=["CLI", "paper companion", "docs site", "CI"],
        outputs=["canonical benchmark JSON", "cross-study report", "snapshot regression runs"],
    ),
    CapabilityArea(
        id="comparison",
        title="Model comparison and ecosystem planning",
        question_it_answers="How do I compare built-in and external models under one protocol?",
        why_it_exists="Benchmark stacks often break because dependency planning and experiment comparison live in different places.",
        primary_apis=["SweepMatrixSpec", "run_sweep", "adapter_catalog", "install_matrix"],
        primary_cli=["python -m tscfbench make-sweep-spec", "python -m tscfbench run-sweep", "python -m tscfbench install-matrix", "python -m tscfbench list-adapters"],
        best_environments=["CLI", "CI", "shared server", "methods notebook"],
        outputs=["sweep specs", "comparison reports", "install plans"],
    ),
    CapabilityArea(
        id="communication",
        title="Teaching, tutorials, and dissemination",
        question_it_answers="How do I make the package understandable to collaborators, reviewers, and students?",
        why_it_exists="Good code still fails to spread if there is no public-facing package story, tutorial order, or benchmark card layer.",
        primary_apis=["render_benchmark_cards_markdown", "render_workflow_recipes_markdown"],
        primary_cli=["python -m tscfbench benchmark-cards", "python -m tscfbench tutorial-index", "python -m tscfbench package-story"],
        best_environments=["README", "docs site", "teaching", "conference tutorial"],
        outputs=["benchmark cards", "tutorial reading order", "release-facing markdown"],
    ),
    CapabilityArea(
        id="agent",
        title="Agent-native research workflows",
        question_it_answers="How do I use coding agents without sending the whole repo and the whole dataset every turn?",
        why_it_exists="Agent-friendly workflows need specs, bundles, handles, and context plans rather than giant free-form prompts.",
        primary_apis=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools"],
        primary_cli=["python -m tscfbench make-agent-spec", "python -m tscfbench build-agent-bundle", "python -m tscfbench plan-context", "python -m tscfbench export-openai-tools"],
        best_environments=["agent IDE", "tool-calling runtime", "CI"],
        outputs=["agent spec JSON", "bundle manifest", "context plan", "tool schemas"],
    ),
]


_SCENARIOS: List[ScenarioCard] = [
    ScenarioCard(
        id="method-paper",
        title="You are writing a new counterfactual method paper",
        persona="methods researcher",
        environment="CLI + notebook + CI",
        question="How do I compare my method against recognizable studies without wiring everything by hand?",
        where_tscfbench_helps=[
            "Gives you canonical studies other researchers already recognize.",
            "Lets you express sweeps as JSON specs instead of notebook state.",
            "Turns runs into reports that fit a paper companion or CI job.",
        ],
        primary_apis=["CanonicalBenchmarkSpec", "SweepMatrixSpec", "run_canonical_benchmark", "run_sweep"],
        primary_cli=["python -m tscfbench make-canonical-spec", "python -m tscfbench make-sweep-spec", "python -m tscfbench run-sweep"],
        outputs=["canonical report", "sweep report", "JSON results"],
    ),
    ScenarioCard(
        id="own-panel-data",
        title="You have your own panel data",
        persona="applied researcher",
        environment="notebook first, then script or CLI",
        question="How do I get from my long-format panel to a placebo-aware report that collaborators can read?",
        where_tscfbench_helps=[
            "Wraps your data in a shared PanelCase schema.",
            "Adds placebo diagnostics and report rendering.",
            "Keeps exploration and reproduction aligned.",
        ],
        primary_apis=["PanelCase", "benchmark_panel", "PanelProtocolConfig", "render_panel_markdown"],
        primary_cli=["python -m tscfbench make-panel-spec", "python -m tscfbench run-panel-spec", "python -m tscfbench render-panel-report"],
        outputs=["panel benchmark output", "placebo tables", "markdown report"],
    ),
    ScenarioCard(
        id="single-series",
        title="You study one treated time series",
        persona="impact analyst",
        environment="notebook or lightweight script",
        question="How do I benchmark a single-series counterfactual workflow and keep it comparable to my panel work?",
        where_tscfbench_helps=[
            "Provides ImpactCase and BenchmarkOutput contracts.",
            "Keeps single-series analysis on the same benchmark philosophy as panel studies.",
            "Acts as a bridge to forecast-as-counterfactual adapters.",
        ],
        primary_apis=["ImpactCase", "benchmark", "OLSImpact"],
        primary_cli=["python -m tscfbench demo", "python -m tscfbench make-sweep-spec --task-family impact"],
        outputs=["prediction frame", "effect metrics", "impact workflow demo"],
    ),
    ScenarioCard(
        id="teaching",
        title="You want to teach this topic",
        persona="instructor or lab lead",
        environment="docs site + notebooks",
        question="How do I introduce the package without dumping source files on the audience?",
        where_tscfbench_helps=[
            "Provides a package story, benchmark cards, and tutorial order.",
            "Ships notebooks that mirror the docs.",
            "Makes the first successful run explicit.",
        ],
        primary_apis=["package_overview", "workflow_recipes", "render_benchmark_cards_markdown"],
        primary_cli=["python -m tscfbench package-story", "python -m tscfbench benchmark-cards", "python -m tscfbench tutorial-index"],
        outputs=["teaching-friendly docs", "notebook reading order", "public benchmark examples"],
    ),
    ScenarioCard(
        id="agent-workflow",
        title="You use coding agents and care about token cost",
        persona="research engineer",
        environment="agent-enabled IDE or tool runtime",
        question="How do I keep the agent useful when the benchmark has many files and large artifacts?",
        where_tscfbench_helps=[
            "Bundles runs into manifests, digests, and artifact handles.",
            "Provides repo maps and context plans.",
            "Exports tool schemas and an MCP server surface.",
        ],
        primary_apis=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools"],
        primary_cli=["python -m tscfbench build-agent-bundle", "python -m tscfbench plan-context", "python -m tscfbench mcp-server"],
        outputs=["manifest.json", "run_digest.json", "context_plan.json", "tool schemas"],
    ),
]


_TUTORIALS: List[TutorialCard] = [
    TutorialCard(
        id="package-tour",
        title="Package tour",
        audience="new user, student, collaborator",
        best_environment="docs + notebook",
        time_to_first_result="5-10 minutes",
        what_you_build=["a mental map of the package", "a first recommended path", "a tiny demo run"],
        entry_points=["docs/package-story.md", "docs/capability-map.md", "notebooks/01_start_here.ipynb"],
    ),
    TutorialCard(
        id="canonical-benchmark",
        title="Canonical panel benchmark",
        audience="methods researcher, reviewer, benchmark author",
        best_environment="CLI + notebook",
        time_to_first_result="10-15 minutes",
        what_you_build=["canonical spec", "canonical results JSON", "canonical report"],
        entry_points=["docs/quickstart.md", "docs/case-studies/germany.md", "notebooks/03_canonical_benchmark.ipynb"],
    ),
    TutorialCard(
        id="custom-panel",
        title="Bring your own panel data",
        audience="applied researcher",
        best_environment="notebook first, then script",
        time_to_first_result="15-25 minutes",
        what_you_build=["PanelCase", "protocol config", "panel report"],
        entry_points=["docs/tutorials/custom-panel-workflow.md", "notebooks/04_custom_panel_data.ipynb", "examples/custom_panel_data_demo.py"],
    ),
    TutorialCard(
        id="agent-workflow",
        title="Agent-assisted benchmark workflow",
        audience="research engineer",
        best_environment="agent-enabled IDE",
        time_to_first_result="15-25 minutes",
        what_you_build=["agent spec", "artifact bundle", "context plan"],
        entry_points=["docs/tutorials/agent-workflows.md", "notebooks/05_agent_workflow.ipynb", "examples/agent_bundle_demo.py"],
    ),
    TutorialCard(
        id="high-traffic-cases",
        title="High-traffic public cases",
        audience="maintainer, package evangelist, applied researcher",
        best_environment="docs + notebook + CLI",
        time_to_first_result="10-20 minutes",
        what_you_build=["event-driven case ideas", "public data fetch plans", "attention-oriented demos"],
        entry_points=["docs/high-traffic-cases.md", "docs/tutorials/github-stars-impact.md", "docs/tutorials/crypto-event-impact.md"],
    ),
]


def package_story() -> Dict[str, Any]:
    return dict(_PACKAGE_STORY)


def capability_map() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _CAPABILITY_AREAS]


def scenario_matrix() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _SCENARIOS]


def tutorial_index() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _TUTORIALS]


def api_atlas() -> Dict[str, Any]:
    return {
        "package_story": package_story(),
        "capability_map": capability_map(),
        "api_handbook": api_handbook(),
        "scenario_matrix": scenario_matrix(),
    }


def _md_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_package_story_markdown() -> str:
    story = package_story()
    lines: List[str] = ["# tscfbench", "", story["headline"], "", story["plain_language"], "", "## What it is", "", _md_list(list(story["what_it_is"])), "", "## What it is not", "", _md_list(list(story["what_it_is_not"])), "", "## Why people adopt it", "", _md_list(list(story["why_people_adopt_it"])), "", "## First commands to run", "", "```bash", "python -m tscfbench package-story", "python -m tscfbench capability-map", "python -m tscfbench api-atlas", "python -m tscfbench scenario-matrix", "python -m tscfbench tutorial-index", "```", ""]
    return "\n".join(lines)


def render_capability_map_markdown() -> str:
    lines: List[str] = ["# Capability map", "", "This page explains **what each part of tscfbench is for**, **why that part exists**, and **where it works best**.", ""]
    for card in _CAPABILITY_AREAS:
        lines.extend([
            f"## {card.title}",
            "",
            f"**Question it answers:** {card.question_it_answers}",
            "",
            f"**Why this exists:** {card.why_it_exists}",
            "",
            f"**Primary APIs:** {', '.join(card.primary_apis)}",
            "",
            "**Primary CLI commands**",
            "",
            "```bash",
            *card.primary_cli,
            "```",
            "",
            f"**Best environments:** {', '.join(card.best_environments)}",
            "",
            "**Typical outputs**",
            "",
            _md_list(card.outputs),
            "",
        ])
    return "\n".join(lines)


def render_scenario_matrix_markdown() -> str:
    lines: List[str] = ["# Scenario matrix", "", "Use this page when the question is not *what function exists?* but *what should I do in my situation?*", ""]
    for card in _SCENARIOS:
        lines.extend([
            f"## {card.title}",
            "",
            f"**Persona:** {card.persona}",
            "",
            f"**Environment:** {card.environment}",
            "",
            f"**Question:** {card.question}",
            "",
            "**Where tscfbench helps**",
            "",
            _md_list(card.where_tscfbench_helps),
            "",
            f"**Primary APIs:** {', '.join(card.primary_apis)}",
            "",
            "**Primary CLI**",
            "",
            "```bash",
            *card.primary_cli,
            "```",
            "",
            f"**Outputs:** {', '.join(card.outputs)}",
            "",
        ])
    return "\n".join(lines)


def render_tutorial_index_markdown() -> str:
    lines: List[str] = ["# Tutorial index", "", "This page tells a new user which tutorial to pick, what they will build, and how long it should take to get to a first useful result.", ""]
    for card in _TUTORIALS:
        lines.extend([
            f"## {card.title}",
            "",
            f"**Audience:** {card.audience}",
            "",
            f"**Best environment:** {card.best_environment}",
            "",
            f"**Time to first result:** {card.time_to_first_result}",
            "",
            "**What you build**",
            "",
            _md_list(card.what_you_build),
            "",
            "**Entry points**",
            "",
            _md_list(card.entry_points),
            "",
        ])
    return "\n".join(lines)


def render_api_atlas_markdown() -> str:
    lines: List[str] = ["# API atlas", "", "The API atlas combines the package story, the capability map, and the API handbook so a user can answer three questions in one place:", "", "- What job am I trying to do?", "- Which API layer exists for that job?", "- In which environment should I use that API?", "", "## Read this page in order", "", "1. Read the package story so you know what tscfbench is for.", "2. Read the capability map so you know which layer solves your problem.", "3. Read the API handbook so you know the exact entry points.", "", render_package_story_markdown(), "", render_capability_map_markdown(), "", render_api_handbook_markdown()]
    return "\n".join(lines)


def write_release_kit(output_dir: str | Path) -> Dict[str, Any]:
    from tscfbench.positioning import write_positioning_assets
    from tscfbench.demo_cases import render_demo_gallery_markdown

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "README_LANDING.md": render_package_story_markdown(),
        "PACKAGE_OVERVIEW.md": render_package_overview_markdown(),
        "API_ATLAS.md": render_api_atlas_markdown(),
        "SCENARIO_MATRIX.md": render_scenario_matrix_markdown(),
        "TUTORIAL_INDEX.md": render_tutorial_index_markdown(),
        "USE_CASES.md": render_use_cases_markdown(),
        "ENVIRONMENTS.md": render_environment_profiles_markdown(),
        "WORKFLOW_RECIPES.md": render_workflow_recipes_markdown(),
        "BENCHMARK_CARDS.md": render_benchmark_cards_markdown(),
        "DEMO_GALLERY.md": render_demo_gallery_markdown(),
        "START_HERE.md": render_start_here_markdown(),
        "DOCTOR.md": render_doctor_markdown(),
        "ESSENTIAL_COMMANDS.md": render_essential_commands_markdown(),
        "TOOL_PROFILES.md": render_tool_profiles_markdown(),
        "FEEDBACK_CHANGES.md": render_feedback_response_markdown(),
    }
    written: List[str] = []
    for name, content in files.items():
        path = out / name
        path.write_text(content, encoding="utf-8")
        written.append(str(path.name))

    positioning_manifest = write_positioning_assets(out)
    for name in positioning_manifest.get("files", []):
        if name not in written:
            written.append(name)

    manifest = {
        "package": "tscfbench",
        "kind": "release_kit",
        "files": written,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


__all__ = [
    "CapabilityArea",
    "ScenarioCard",
    "TutorialCard",
    "api_atlas",
    "capability_map",
    "package_story",
    "render_api_atlas_markdown",
    "render_capability_map_markdown",
    "render_package_story_markdown",
    "render_scenario_matrix_markdown",
    "render_tutorial_index_markdown",
    "scenario_matrix",
    "tutorial_index",
    "write_release_kit",
]
