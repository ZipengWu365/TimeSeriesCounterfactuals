from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class APICard:
    id: str
    title: str
    layer: str
    entry_points: List[str]
    origin: str
    when_to_use: str
    what_it_returns: List[str]
    environments: List[str]
    cli_commands: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class UseCaseCard:
    id: str
    persona: str
    title: str
    question: str
    environment: str
    what_tscfbench_does: List[str]
    recommended_entry_points: List[str]
    outputs: List[str]
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EnvironmentProfile:
    id: str
    title: str
    best_for: str
    what_works_well: List[str]
    recommended_apis: List[str]
    recommended_cli: List[str]
    install_extras: List[str]
    cautions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CLIGuideCard:
    id: str
    title: str
    commands: List[str]
    purpose: str
    typical_user: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_OVERVIEW: Dict[str, Any] = {
    "name": "tscfbench",
    "tagline": "A research-first toolkit for benchmarking time-series counterfactual inference workflows.",
    "one_sentence": (
        "python -m tscfbench helps researchers define counterfactual benchmark tasks, run reproducible studies, compare models across"
        " panel and impact settings, and package the results for humans, CI systems, and coding agents."
    ),
    "what_problem_it_solves": [
        "Benchmark code for time-series counterfactual inference is often rewritten from scratch and drifts across projects.",
        "The ecosystem is fragmented across synthetic-control, impact-analysis, and forecasting libraries with incompatible APIs.",
        "Research packages are often hard to teach, hard to reproduce, and hard to operationalize in CI or agent-driven coding workflows.",
    ],
    "what_the_package_provides": [
        "Canonical data containers for impact and panel counterfactual tasks.",
        "Single-case and multi-model benchmark runners with placebo-aware evaluation for panel studies.",
        "Canonical study runners for Germany, Prop99, and Basque so researchers have recognizable starting points.",
        "Adapter discovery, installation planning, and optional bridges to third-party ecosystems.",
        "JSON-first specs, Markdown reports, and agent-native bundles for token-aware workflows.",
    ],
    "who_it_is_for": [
        "Methods researchers building or comparing new counterfactual estimators.",
        "Applied researchers running policy evaluation or intervention analysis on time-indexed data.",
        "Instructors who want stable teaching examples and snapshot-backed tutorials.",
        "Tool builders who need CI-friendly benchmark regressions and agent-friendly artifacts.",
    ],
    "what_it_is_not": [
        "It is not a claim that one built-in model is state of the art.",
        "It is not a data warehouse or experiment tracking platform.",
        "It is not limited to one methodological family; its job is to give them a shared protocol and workflow surface.",
    ],
    "task_families": [
        {
            "id": "impact",
            "title": "Single treated series with controls",
            "why": "Estimate the post-intervention counterfactual path of one outcome series and derive treatment impact.",
            "main_objects": ["ImpactCase", "benchmark", "OLSImpact", "tfp_causalimpact"],
        },
        {
            "id": "panel",
            "title": "Single treated unit in a panel",
            "why": "Run synthetic-control style studies with placebo diagnostics and protocol-based reporting.",
            "main_objects": ["PanelCase", "benchmark_panel", "PanelProtocolConfig", "SimpleSyntheticControl", "DifferenceInDifferences"],
        },
        {
            "id": "research_ops",
            "title": "Benchmark operations and dissemination",
            "why": "Compare models across studies, generate reproducible specs, build reports, and package artifacts for CI or agents.",
            "main_objects": ["SweepMatrixSpec", "CanonicalBenchmarkSpec", "AgentResearchTaskSpec", "build_panel_agent_bundle"],
        },
    ],
    "primary_outputs": [
        "JSON specs that can be checked into git or passed to agents.",
        "Markdown reports for experiments, canonical studies, and sweeps.",
        "Artifact bundles with manifest, digest, and context-pack files for token-aware automation.",
        "Installation and adapter catalogs to navigate the wider ecosystem.",
    ],
}


_API_CARDS: List[APICard] = [
    APICard(
        id="core-data-model",
        title="Core data model",
        layer="foundation",
        entry_points=["ImpactCase", "PanelCase", "PredictionResult"],
        origin=(
            "This layer exists because most counterfactual libraries encode data differently. tscfbench needs a small, stable schema"
            " that lets the same benchmark protocol work with built-in models, external adapters, and custom user data."
        ),
        when_to_use="Use these classes whenever you want to bring your own dataset into the package or write a new model adapter.",
        what_it_returns=[
            "Validated case objects with explicit intervention boundaries.",
            "PredictionResult objects with counterfactual path, effect path, and optional intervals.",
        ],
        environments=["notebook", "python script", "library integration", "teaching"],
        notes=[
            "ImpactCase is for one treated series plus controls/covariates.",
            "PanelCase is for one treated unit in a long-format panel.",
            "PredictionResult is the common output contract for all model wrappers.",
        ],
    ),
    APICard(
        id="single-case-benchmarking",
        title="Single-case benchmarking",
        layer="benchmark protocol",
        entry_points=["benchmark", "benchmark_panel", "PanelProtocolConfig"],
        origin=(
            "Researchers usually need more than raw predictions: they need comparable metrics and, in panel studies, placebo-based"
            " diagnostics. This layer turns one model + one case into a protocol-aware result object."
        ),
        when_to_use="Use this when you have one case and one model and want an interpretable benchmark result quickly.",
        what_it_returns=[
            "Point metrics such as RMSE, MAE, R², and cumulative-effect error for synthetic tasks.",
            "Panel diagnostics such as pre/post RMSPE style summaries and placebo tables.",
        ],
        environments=["notebook", "python script", "quick experiment", "teaching"],
        cli_commands=["python -m tscfbench demo", "python -m tscfbench make-panel-spec", "python -m tscfbench run-panel-spec"],
        notes=[
            "benchmark() is the generic entry point for cases with ground-truth counterfactuals.",
            "benchmark_panel() adds panel-specific placebo logic and reporting metadata.",
        ],
    ),
    APICard(
        id="experiment-specs",
        title="Experiment specs and reproducibility",
        layer="experiment definition",
        entry_points=["PanelExperimentSpec", "ImpactExperimentSpec", "run_panel_experiment"],
        origin=(
            "Once a benchmark leaves a notebook, ad hoc parameter passing becomes fragile. The spec layer exists so experiments can"
            " be serialized, versioned, diffed, and rerun by humans, CI jobs, or agents."
        ),
        when_to_use="Use this layer when you want JSON-first reproducibility or when you want CLI and Python workflows to mirror each other.",
        what_it_returns=[
            "Serializable experiment specifications.",
            "Protocol outputs that can be rendered into Markdown or packed into bundles.",
        ],
        environments=["CLI", "git-based collaboration", "CI", "agent workflows"],
        cli_commands=["python -m tscfbench make-panel-spec", "python -m tscfbench run-panel-spec", "python -m tscfbench render-panel-report"],
        notes=[
            "This is the best entry point for people who want reproducible experiments without writing lots of orchestration code.",
        ],
    ),
    APICard(
        id="canonical-studies",
        title="Canonical benchmark studies",
        layer="research benchmarks",
        entry_points=["list_canonical_studies", "CanonicalBenchmarkSpec", "run_canonical_benchmark", "render_canonical_markdown"],
        origin=(
            "A benchmark package becomes easier to trust and teach when it offers a small set of recognizable studies. This layer is"
            " the package's public face for empirical panel counterfactual benchmarking."
        ),
        when_to_use="Use this layer when you want a standard study battery rather than a single custom case.",
        what_it_returns=[
            "A study catalog with Germany, Prop99, and Basque metadata.",
            "Cross-study benchmark runs and a shareable Markdown report.",
        ],
        environments=["paper companion", "tutorials", "teaching", "benchmark release"],
        cli_commands=["python -m tscfbench list-canonical-studies", "python -m tscfbench make-canonical-spec", "python -m tscfbench run-canonical", "python -m tscfbench render-canonical-report"],
        notes=[
            "Use snapshot mode for reproducible tutorials and CI.",
            "Use auto/remote mode when you want fuller study data in normal research runs.",
        ],
    ),
    APICard(
        id="model-discovery",
        title="Model discovery and ecosystem planning",
        layer="ecosystem navigation",
        entry_points=["install_matrix", "adapter_catalog", "recommend_adapter_stack", "list_model_ids"],
        origin=(
            "Researchers rarely know up front which package stack is easiest to install, easiest to explain, or most suitable for a"
            " given task family. This layer exists to make that choice explicit rather than tribal knowledge."
        ),
        when_to_use="Use this layer before you commit to a benchmark stack or when you need to explain optional dependencies to users.",
        what_it_returns=[
            "Structured install metadata and import/package names.",
            "Adapter cards that describe strengths, caveats, and runtime characteristics.",
            "Recommendations for a small, research-oriented starting stack.",
        ],
        environments=["package maintenance", "onboarding", "teaching", "agent planning"],
        cli_commands=["python -m tscfbench install-matrix", "python -m tscfbench list-adapters", "python -m tscfbench recommend-stack", "python -m tscfbench list-model-ids"],
        notes=[
            "This layer is especially useful when your audience is global and needs a clearer install story.",
        ],
    ),
    APICard(
        id="sweep-studies",
        title="Sweep studies and comparison grids",
        layer="multi-run orchestration",
        entry_points=["SweepMatrixSpec", "make_default_sweep_spec", "run_sweep", "render_sweep_markdown"],
        origin=(
            "Researchers often compare several model/dataset combinations at once. The sweep layer exists so those comparisons are"
            " explicit, machine-readable, and robust to partial adapter failures."
        ),
        when_to_use="Use this layer when you are comparing multiple models, datasets, or backends in a single benchmark run.",
        what_it_returns=[
            "Per-cell results with success/error status.",
            "Comparison tables and study-level summaries.",
        ],
        environments=["benchmarking", "CI", "method comparison", "release validation"],
        cli_commands=["python -m tscfbench make-sweep-spec", "python -m tscfbench run-sweep", "python -m tscfbench render-sweep-report"],
        notes=[
            "External-package failures are recorded as cell-level errors rather than crashing the full sweep by default.",
        ],
    ),
    APICard(
        id="agent-layer",
        title="Agent-native workflow layer",
        layer="automation",
        entry_points=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools", "TSCFBenchMCPServer"],
        origin=(
            "Agent workflows need smaller, more structured artifacts than notebook-centric research code. This layer exists to turn"
            " benchmark runs into token-bounded specs, manifests, digests, and tool surfaces."
        ),
        when_to_use="Use this layer when a coding agent or tool-calling runtime participates in your research workflow.",
        what_it_returns=[
            "Compact JSON specs and bundles.",
            "Repo maps, context plans, and manifest-based artifact access.",
            "Function-tool and MCP surfaces so the package can explain itself to agents.",
        ],
        environments=["Cursor/Codex/ChatGPT", "tool-calling backends", "CI automation", "multi-step research assistants"],
        cli_commands=["python -m tscfbench make-agent-spec", "python -m tscfbench build-agent-bundle", "python -m tscfbench plan-context", "python -m tscfbench export-openai-tools", "python -m tscfbench mcp-server"],
        notes=[
            "This layer matters when you want lower token usage, smaller context windows, and resumable research tasks.",
        ],
    ),
    APICard(
        id="reports-and-teaching",
        title="Reports, teaching surfaces, and project communication",
        layer="dissemination",
        entry_points=["render_panel_markdown", "render_sweep_markdown", "render_canonical_markdown"],
        origin=(
            "A benchmark package spreads only if the outputs are understandable outside the codebase. This layer exists so results can"
            " become readable artifacts for papers, tutorials, internal memos, and classrooms."
        ),
        when_to_use="Use this layer whenever you need a human-readable output rather than raw Python objects.",
        what_it_returns=[
            "Markdown reports that summarize configuration, metrics, and comparison tables.",
            "A cleaner handoff from computation to writing or teaching.",
        ],
        environments=["paper writing", "teaching", "project website", "release notes"],
        cli_commands=["python -m tscfbench render-panel-report", "python -m tscfbench render-sweep-report", "python -m tscfbench render-canonical-report"],
        notes=[
            "These renderers are intentionally simple so they are easy to diff and easy to post-process.",
        ],
    ),
]


_USE_CASES: List[UseCaseCard] = [
    UseCaseCard(
        id="new-method-paper",
        persona="methods researcher",
        title="You are developing a new synthetic-control or counterfactual method",
        question="How do I compare my method against common baselines and canonical studies without inventing a benchmark from scratch?",
        environment="Python script + CLI + optional CI",
        what_tscfbench_does=[
            "Gives you canonical studies and built-in baselines so you can define a first comparison grid immediately.",
            "Lets you express your benchmark as JSON specs and sweep matrices rather than one-off notebook state.",
            "Produces Markdown reports that are easy to attach to a repo or paper companion.",
        ],
        recommended_entry_points=["CanonicalBenchmarkSpec", "SweepMatrixSpec", "run_sweep", "render_sweep_markdown"],
        outputs=["canonical_results.json", "panel_report.md", "sweep_report.md"],
        notes=["This is the package's most research-native use case."],
    ),
    UseCaseCard(
        id="own-panel-data",
        persona="applied empirical researcher",
        title="You have your own policy or intervention panel data",
        question="How do I plug my own long-format panel into a benchmark protocol with placebo diagnostics?",
        environment="Notebook or Python script",
        what_tscfbench_does=[
            "Lets you wrap your data in PanelCase and evaluate models under a consistent panel protocol.",
            "Provides simple SCM and DiD baselines even before you wire in external research packages.",
            "Keeps reporting logic separate from data preparation so your applied workflow stays readable.",
        ],
        recommended_entry_points=["PanelCase", "benchmark_panel", "PanelProtocolConfig", "render_panel_markdown"],
        outputs=["PanelBenchmarkOutput", "placebo tables", "panel Markdown report"],
    ),
    UseCaseCard(
        id="impact-analysis",
        persona="impact analyst",
        title="You are studying one treated time series with controls",
        question="How do I benchmark impact-analysis models and compare forecast-style counterfactuals with causal-impact style baselines?",
        environment="Notebook, script, or product analytics workflow",
        what_tscfbench_does=[
            "Lets you formalize a single-series counterfactual task with ImpactCase.",
            "Provides a built-in OLS impact baseline and room for external impact adapters.",
            "Measures both predictive counterfactual error and cumulative effect error when ground truth exists.",
        ],
        recommended_entry_points=["ImpactCase", "benchmark", "OLSImpact", "list_model_ids(task_family='impact')"],
        outputs=["BenchmarkOutput", "prediction frame", "impact metrics"],
    ),
    UseCaseCard(
        id="classroom",
        persona="instructor or teaching assistant",
        title="You need a stable teaching surface for a methods class",
        question="How can I teach canonical counterfactual case studies without depending on live downloads or fragile notebooks?",
        environment="Notebook, classroom laptops, offline lab, teaching repo",
        what_tscfbench_does=[
            "Ships snapshot-compatible canonical studies for deterministic classroom runs.",
            "Offers a small CLI so students can reproduce the same steps with less setup friction.",
            "Separates the conceptual layers of the package so you can teach data schema, protocol, and model choice independently.",
        ],
        recommended_entry_points=["list_canonical_studies", "make-canonical-spec", "run-canonical", "docs/case-studies"],
        outputs=["snapshot-backed reports", "case-study tutorials", "repeatable teaching examples"],
    ),
    UseCaseCard(
        id="ci-regression",
        persona="package maintainer",
        title="You want CI regression tests for benchmark behavior",
        question="How do I make sure a change to my library does not silently break a canonical study or the reporting protocol?",
        environment="GitHub Actions or other CI",
        what_tscfbench_does=[
            "Provides snapshot data sources so tests do not depend on network access.",
            "Lets you encode a canonical benchmark or sweep as JSON and compare outputs over time.",
            "Supports installation matrices so CI jobs can separate core coverage from optional dependency coverage.",
        ],
        recommended_entry_points=["CanonicalBenchmarkSpec", "SweepMatrixSpec", "install_matrix", "tests/"],
        outputs=["deterministic CI runs", "snapshot results", "release-ready benchmark artifacts"],
    ),
    UseCaseCard(
        id="agent-assisted-research",
        persona="research engineer using coding agents",
        title="You want coding agents to help with benchmark development without wasting context window",
        question="How can I let an agent inspect experiments, reports, and datasets without pasting huge files into chat?",
        environment="Agent-enabled IDE, MCP client, tool-calling runtime",
        what_tscfbench_does=[
            "Builds compact task specs, bundles, digests, repo maps, and context plans.",
            "Exposes a tool surface so an agent can ask for the install matrix, canonical studies, or artifact slices directly.",
            "Lets you keep large tables as artifacts and bring only the needed slices into context.",
        ],
        recommended_entry_points=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools"],
        outputs=["bundle_dir/manifest.json", "context_plan.json", "tool-calling schemas"],
    ),
]


_ENVIRONMENTS: List[EnvironmentProfile] = [
    EnvironmentProfile(
        id="notebook",
        title="Notebook research",
        best_for="Exploration, pedagogy, and first-pass method debugging.",
        what_works_well=[
            "Wrap your data in ImpactCase or PanelCase and inspect results interactively.",
            "Prototype on built-in baselines before installing heavier optional dependencies.",
            "Render Markdown reports once the notebook logic stabilizes.",
        ],
        recommended_apis=["ImpactCase", "PanelCase", "benchmark", "benchmark_panel", "render_panel_markdown"],
        recommended_cli=["python -m tscfbench demo"],
        install_extras=["core"],
        cautions=["Notebook state can drift; switch to JSON specs when you want a reproducible benchmark."],
    ),
    EnvironmentProfile(
        id="cli",
        title="CLI-first research workflow",
        best_for="Reproducible scripts, shared repositories, and low-friction onboarding.",
        what_works_well=[
            "Create specs and reports without writing orchestration code.",
            "Share the same benchmark recipe across machines and collaborators.",
            "Use canonical studies as the public entry point for the project.",
        ],
        recommended_apis=["PanelExperimentSpec", "CanonicalBenchmarkSpec", "SweepMatrixSpec"],
        recommended_cli=["python -m tscfbench make-canonical-spec", "python -m tscfbench run-canonical", "python -m tscfbench run-sweep"],
        install_extras=["core", "research"],
        cautions=["Keep output files under version control if they are part of a paper companion or release process."],
    ),
    EnvironmentProfile(
        id="ci",
        title="CI and release engineering",
        best_for="Regression checks, optional-dependency smoke tests, and repeatable releases.",
        what_works_well=[
            "Use snapshot-backed canonical studies to avoid flaky network-bound tests.",
            "Separate core tests from optional third-party install jobs.",
            "Render reports as artifacts in CI for easier inspection of failures.",
        ],
        recommended_apis=["CanonicalBenchmarkSpec", "run_canonical_benchmark", "install_matrix"],
        recommended_cli=["python -m tscfbench make-canonical-spec --data-source snapshot", "python -m tscfbench run-canonical"],
        install_extras=["dev", "research"],
        cautions=["Do not assume every optional third-party package is available on every platform; keep install tiers explicit."],
    ),
    EnvironmentProfile(
        id="agent",
        title="Agent-assisted coding environment",
        best_for="Token-aware research automation, code navigation, and structured tool use.",
        what_works_well=[
            "Build a small bundle and let the agent read manifest-backed artifacts on demand.",
            "Use function-tool or MCP exports when you want the package to explain its own surface to the agent.",
            "Keep large files out of chat and let context plans decide what enters the window.",
        ],
        recommended_apis=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools", "TSCFBenchMCPServer"],
        recommended_cli=["python -m tscfbench make-agent-spec", "python -m tscfbench build-agent-bundle", "python -m tscfbench export-openai-tools", "python -m tscfbench mcp-server"],
        install_extras=["core"],
        cautions=["Separate planning turns from editing turns if you want tighter control over token usage and tool availability."],
    ),
    EnvironmentProfile(
        id="hpc",
        title="Shared server or HPC-style batch environment",
        best_for="Larger sweeps, heavier optional models, and scheduled benchmarks.",
        what_works_well=[
            "Use sweep specs to make runs explicit and easy to rerun on another machine.",
            "Install only the extras you need for a given benchmark battery.",
            "Store JSON results and Markdown summaries as durable artifacts rather than relying on notebook state.",
        ],
        recommended_apis=["SweepMatrixSpec", "run_sweep", "render_sweep_markdown", "install_matrix"],
        recommended_cli=["python -m tscfbench make-sweep-spec", "python -m tscfbench run-sweep"],
        install_extras=["research", "forecast"],
        cautions=["Third-party deep-learning or Bayesian stacks may have platform-specific dependency constraints."],
    ),
    EnvironmentProfile(
        id="teaching",
        title="Teaching and workshop environment",
        best_for="Live demos, student assignments, and reproducible teaching materials.",
        what_works_well=[
            "Use canonical snapshot studies so every participant sees the same results.",
            "Prefer the CLI and small example scripts for classrooms with mixed Python skill levels.",
            "Use docs pages and case studies as the main narrative surface, not only raw API references.",
        ],
        recommended_apis=["list_canonical_studies", "CanonicalBenchmarkSpec", "render_canonical_markdown"],
        recommended_cli=["python -m tscfbench list-canonical-studies", "python -m tscfbench run-canonical"],
        install_extras=["core"],
        cautions=["Keep classroom exercises small and deterministic; save external-package comparisons for advanced sessions."],
    ),
]


_CLI_GUIDE: List[CLIGuideCard] = [
    CLIGuideCard(
        id="understand-package",
        title="Understand the package",
        commands=["python -m tscfbench intro", "python -m tscfbench api-handbook", "python -m tscfbench use-cases", "python -m tscfbench environments"],
        purpose="Read the package as a product: what it is, why it exists, what APIs matter, and where it fits.",
        typical_user="A new researcher, collaborator, or maintainer onboarding to the project.",
    ),
    CLIGuideCard(
        id="run-canonical",
        title="Run the standard studies",
        commands=["python -m tscfbench list-canonical-studies", "python -m tscfbench make-canonical-spec", "python -m tscfbench run-canonical", "python -m tscfbench render-canonical-report"],
        purpose="Get to a recognizable panel counterfactual benchmark quickly.",
        typical_user="A researcher who wants a trusted first run or a teaching example.",
    ),
    CLIGuideCard(
        id="compare-models",
        title="Compare multiple models",
        commands=["python -m tscfbench list-model-ids", "python -m tscfbench make-sweep-spec", "python -m tscfbench run-sweep", "python -m tscfbench render-sweep-report"],
        purpose="Build a comparison grid across models and datasets.",
        typical_user="A methods researcher or maintainer evaluating multiple adapters.",
    ),
    CLIGuideCard(
        id="agent-workflow",
        title="Work with coding agents",
        commands=["python -m tscfbench make-agent-spec", "python -m tscfbench build-agent-bundle", "python -m tscfbench plan-context", "python -m tscfbench export-openai-tools", "python -m tscfbench mcp-server"],
        purpose="Create small, machine-readable artifacts for tool-calling or MCP-style workflows.",
        typical_user="A research engineer using an LLM agent as part of development or analysis.",
    ),
]


def package_overview() -> Dict[str, Any]:
    return dict(_OVERVIEW)



def api_handbook() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _API_CARDS]



def use_case_catalog() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _USE_CASES]



def environment_profiles() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _ENVIRONMENTS]



def cli_guide() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _CLI_GUIDE]



def _md_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)



def render_package_overview_markdown() -> str:
    ov = package_overview()
    lines: List[str] = []
    lines.append("# What tscfbench is")
    lines.append("")
    lines.append(ov["one_sentence"])
    lines.append("")
    lines.append("## What problem it solves")
    lines.append("")
    lines.append(_md_list(list(ov["what_problem_it_solves"])))
    lines.append("")
    lines.append("## What the package provides")
    lines.append("")
    lines.append(_md_list(list(ov["what_the_package_provides"])))
    lines.append("")
    lines.append("## Who it is for")
    lines.append("")
    lines.append(_md_list(list(ov["who_it_is_for"])))
    lines.append("")
    lines.append("## What it is not")
    lines.append("")
    lines.append(_md_list(list(ov["what_it_is_not"])))
    lines.append("")
    lines.append("## Task families")
    lines.append("")
    for fam in ov["task_families"]:
        lines.append(f"### {fam['title']}")
        lines.append("")
        lines.append(fam["why"])
        lines.append("")
        lines.append(f"Primary objects: {', '.join(fam['main_objects'])}")
        lines.append("")
    lines.append("## Primary outputs")
    lines.append("")
    lines.append(_md_list(list(ov["primary_outputs"])))
    lines.append("")
    lines.append("## First commands to run")
    lines.append("")
    lines.append("Start narrow. You do not need the whole package surface on day one.")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench start-here")
    lines.append("python -m tscfbench quickstart")
    lines.append("python -m tscfbench doctor")
    lines.append("python -m tscfbench essentials")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)



def render_api_handbook_markdown() -> str:
    lines: List[str] = []
    lines.append("# API handbook")
    lines.append("")
    lines.append("This page organizes the package by *jobs* rather than by source files. Each section explains why that API layer exists, when to use it, and what it returns.")
    lines.append("")
    for card in _API_CARDS:
        lines.append(f"## {card.title}")
        lines.append("")
        lines.append(f"**Layer:** {card.layer}")
        lines.append("")
        lines.append(f"**Entry points:** {', '.join(card.entry_points)}")
        lines.append("")
        lines.append("**Why this API exists**")
        lines.append("")
        lines.append(card.origin)
        lines.append("")
        lines.append("**When to use it**")
        lines.append("")
        lines.append(card.when_to_use)
        lines.append("")
        lines.append("**What it returns**")
        lines.append("")
        lines.append(_md_list(card.what_it_returns))
        lines.append("")
        lines.append(f"**Works well in:** {', '.join(card.environments)}")
        lines.append("")
        if card.cli_commands:
            lines.append("**CLI counterparts**")
            lines.append("")
            lines.append("```bash")
            lines.extend(card.cli_commands)
            lines.append("```")
            lines.append("")
        if card.notes:
            lines.append("**Notes**")
            lines.append("")
            lines.append(_md_list(card.notes))
            lines.append("")
    return "\n".join(lines)



def render_use_cases_markdown() -> str:
    lines: List[str] = []
    lines.append("# Use cases")
    lines.append("")
    lines.append("The fastest way to understand tscfbench is to start from your situation rather than from the internal module tree.")
    lines.append("")
    for card in _USE_CASES:
        lines.append(f"## {card.title}")
        lines.append("")
        lines.append(f"**Persona:** {card.persona}")
        lines.append("")
        lines.append(f"**Question:** {card.question}")
        lines.append("")
        lines.append(f"**Best environment:** {card.environment}")
        lines.append("")
        lines.append("**What tscfbench does for you**")
        lines.append("")
        lines.append(_md_list(card.what_tscfbench_does))
        lines.append("")
        lines.append(f"**Recommended entry points:** {', '.join(card.recommended_entry_points)}")
        lines.append("")
        lines.append(f"**Typical outputs:** {', '.join(card.outputs)}")
        lines.append("")
        if card.notes:
            lines.append("**Notes**")
            lines.append("")
            lines.append(_md_list(card.notes))
            lines.append("")
    return "\n".join(lines)



def render_environment_profiles_markdown() -> str:
    lines: List[str] = []
    lines.append("# Environment guide")
    lines.append("")
    lines.append("python -m tscfbench is intentionally usable in several environments. The right entry point depends on how formal, reproducible, and automated your workflow needs to be.")
    lines.append("")
    for card in _ENVIRONMENTS:
        lines.append(f"## {card.title}")
        lines.append("")
        lines.append(f"**Best for:** {card.best_for}")
        lines.append("")
        lines.append("**What works well here**")
        lines.append("")
        lines.append(_md_list(card.what_works_well))
        lines.append("")
        lines.append(f"**Recommended APIs:** {', '.join(card.recommended_apis)}")
        lines.append("")
        if card.recommended_cli:
            lines.append("**Recommended CLI commands**")
            lines.append("")
            lines.append("```bash")
            lines.extend(card.recommended_cli)
            lines.append("```")
            lines.append("")
        lines.append(f"**Install extras:** {', '.join(card.install_extras)}")
        lines.append("")
        if card.cautions:
            lines.append("**Cautions**")
            lines.append("")
            lines.append(_md_list(card.cautions))
            lines.append("")
    return "\n".join(lines)



def render_cli_guide_markdown() -> str:
    lines: List[str] = []
    lines.append("# CLI guide")
    lines.append("")
    lines.append("The full CLI is broad because the package covers benchmarking, reporting, packaging, and agent workflows. Most users should start with the narrow entry surface below and ignore the rest until needed.")
    lines.append("")
    lines.append("## Narrow first-run surface")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench start-here")
    lines.append("python -m tscfbench quickstart")
    lines.append("python -m tscfbench doctor")
    lines.append("python -m tscfbench essentials")
    lines.append("```")
    lines.append("")
    lines.append("## Then expand only when needed")
    lines.append("")
    for card in _CLI_GUIDE:
        lines.append(f"## {card.title}")
        lines.append("")
        lines.append(card.purpose)
        lines.append("")
        lines.append(f"**Typical user:** {card.typical_user}")
        lines.append("")
        lines.append("```bash")
        lines.extend(card.commands)
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


__all__ = [
    "APICard",
    "CLIGuideCard",
    "EnvironmentProfile",
    "UseCaseCard",
    "api_handbook",
    "cli_guide",
    "environment_profiles",
    "package_overview",
    "render_api_handbook_markdown",
    "render_cli_guide_markdown",
    "render_environment_profiles_markdown",
    "render_package_overview_markdown",
    "render_use_cases_markdown",
    "use_case_catalog",
]
