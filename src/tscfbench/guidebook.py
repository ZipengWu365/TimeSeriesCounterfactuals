from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class WorkflowRecipe:
    id: str
    title: str
    summary: str
    persona: str
    task_family: str
    best_environment: str
    environment_tags: List[str]
    persona_tags: List[str]
    goal_tags: List[str]
    why_this_exists: str
    what_you_do: List[str]
    recommended_apis: List[str]
    recommended_cli: List[str]
    recommended_docs: List[str]
    recommended_examples: List[str]
    recommended_notebooks: List[str]
    expected_outputs: List[str]
    benchmark_cards: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkCard:
    id: str
    title: str
    task_family: str
    canonical: bool
    question: str
    why_it_matters: str
    dataset_shape: str
    intervention: str
    recommended_workflows: List[str]
    recommended_models: List[str]
    outputs: List[str]
    environments: List[str]
    teaching_angle: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_RECIPES: List[WorkflowRecipe] = [
    WorkflowRecipe(
        id="package-tour",
        title="Start by understanding the package before choosing a method",
        summary="Best for new users who need a mental model of the package, its layers, and its outputs.",
        persona="new researcher or collaborator",
        task_family="overview",
        best_environment="docs site + notebook + short CLI session",
        environment_tags=["docs", "notebook", "cli", "teaching"],
        persona_tags=["new", "researcher", "collaborator", "student", "teacher"],
        goal_tags=["understand", "overview", "onboarding", "learn"],
        why_this_exists=(
            "Most research packages fail adoption because a newcomer cannot tell what the package is for, which layer matters,"
            " and what a successful first run should produce. This recipe fixes that first-contact problem."
        ),
        what_you_do=[
            "Read the product-level introduction and the API handbook rather than jumping straight into source files.",
            "Run a tiny canonical benchmark so you can see the shape of the outputs.",
            "Use the package tour notebook to connect concepts, CLI commands, and Python objects.",
        ],
        recommended_apis=["package_overview", "api_handbook", "use_case_catalog"],
        recommended_cli=["python -m tscfbench start-here", "python -m tscfbench intro", "python -m tscfbench api-handbook", "python -m tscfbench recommend-path --persona new --goal understand"],
        recommended_docs=["docs/index.md", "docs/start-here.md", "docs/what-is-tscfbench.md", "docs/api-handbook.md"],
        recommended_examples=["examples/package_tour.py", "examples/recommend_path_demo.py"],
        recommended_notebooks=["notebooks/01_start_here.ipynb", "notebooks/02_package_tour.ipynb"],
        expected_outputs=["A clear mental model of task layer / benchmark layer / workflow layer", "A first canonical JSON spec", "A first Markdown report"],
        notes=["Use this recipe in workshops, onboarding docs, and when introducing the package to a new lab member."],
    ),
    WorkflowRecipe(
        id="canonical-panel-studies",
        title="Run recognizable panel counterfactual studies first",
        summary="Best for methods researchers or reviewers who want standard reference cases before custom data.",
        persona="methods researcher",
        task_family="panel",
        best_environment="CLI-first workflow or reproducible notebook",
        environment_tags=["cli", "notebook", "ci", "docs"],
        persona_tags=["methods", "researcher", "reviewer", "benchmark"],
        goal_tags=["benchmark", "paper", "compare", "canonical"],
        why_this_exists=(
            "Germany, Prop99, and Basque are the public face of the package because they give researchers familiar landmarks"
            " and make benchmark reports immediately legible to the literature."
        ),
        what_you_do=[
            "Generate a canonical benchmark spec instead of hand-writing a one-off notebook flow.",
            "Run the canonical study battery on snapshot or remote data.",
            "Render a Markdown report that can live in a repo, paper companion, or docs site.",
        ],
        recommended_apis=["CanonicalBenchmarkSpec", "run_canonical_benchmark", "render_canonical_markdown"],
        recommended_cli=["python -m tscfbench make-canonical-spec --data-source snapshot -o canonical.json", "python -m tscfbench run-canonical canonical.json -o canonical_results.json", "python -m tscfbench render-canonical-report canonical.json -o canonical_report.md"],
        recommended_docs=["docs/case-studies/germany.md", "docs/case-studies/prop99.md", "docs/case-studies/basque.md", "docs/benchmark-cards.md"],
        recommended_examples=["examples/canonical_benchmark_demo.py"],
        recommended_notebooks=["notebooks/03_canonical_benchmark.ipynb"],
        expected_outputs=["canonical.json", "canonical_results.json", "canonical_report.md"],
        benchmark_cards=["german_reunification", "california_prop99", "basque_country"],
        notes=["This is the most publication-friendly entry path for a new benchmark paper."],
    ),
    WorkflowRecipe(
        id="custom-panel-data",
        title="Bring your own panel data into a placebo-aware benchmark",
        summary="Best for applied researchers with their own policy or intervention panel data.",
        persona="applied researcher",
        task_family="panel",
        best_environment="notebook for exploration, then Python script or CLI for reproduction",
        environment_tags=["notebook", "script", "cli", "shared-server"],
        persona_tags=["applied", "researcher", "policy", "economist", "analyst"],
        goal_tags=["own data", "policy", "evaluation", "panel"],
        why_this_exists=(
            "Researchers often have panel data ready to go but no stable way to impose placebo checks, consistent outputs, and"
            " a benchmark protocol. This recipe provides that bridge."
        ),
        what_you_do=[
            "Wrap your long-format panel in PanelCase.",
            "Select a baseline or adapter and run benchmark_panel under a fixed protocol.",
            "Inspect placebo diagnostics and render a Markdown report for collaborators.",
        ],
        recommended_apis=["PanelCase", "benchmark_panel", "PanelProtocolConfig", "render_panel_markdown"],
        recommended_cli=["python -m tscfbench make-panel-spec --dataset synthetic_latent_factor -o panel.json", "python -m tscfbench run-panel-spec panel.json", "python -m tscfbench render-panel-report panel.json -o panel_report.md"],
        recommended_docs=["docs/tutorials/custom-panel-workflow.md", "docs/use-cases.md", "docs/environments.md"],
        recommended_examples=["examples/custom_panel_data_demo.py", "examples/panel_research_demo.py"],
        recommended_notebooks=["notebooks/04_custom_panel_data.ipynb"],
        expected_outputs=["PanelBenchmarkOutput", "placebo tables", "panel_report.md"],
        benchmark_cards=["synthetic_latent_factor", "german_reunification"],
        notes=["Use this path when the scientific question is applied and the workflow needs to stay readable for collaborators."],
    ),
    WorkflowRecipe(
        id="impact-analysis",
        title="Benchmark one treated time series with controls",
        summary="Best for intervention analysis, product analytics, or forecast-as-counterfactual workflows.",
        persona="impact analyst",
        task_family="impact",
        best_environment="notebook or lightweight script",
        environment_tags=["notebook", "script", "product-analytics"],
        persona_tags=["impact", "analyst", "marketing", "forecast", "causal"],
        goal_tags=["impact", "intervention", "single series", "counterfactual"],
        why_this_exists=(
            "Time-series counterfactual work is not only synthetic control. This recipe gives a single-series path with controls,"
            " predictive counterfactuals, and effect error metrics."
        ),
        what_you_do=[
            "Define an ImpactCase with pre/post intervention periods and any controls.",
            "Run benchmark on a built-in baseline or an external impact adapter.",
            "Examine counterfactual error, effect-path error, and cumulative effect summaries.",
        ],
        recommended_apis=["ImpactCase", "benchmark", "OLSImpact"],
        recommended_cli=["python -m tscfbench demo", "python -m tscfbench list-model-ids --task-family impact", "python -m tscfbench make-sweep-spec --task-family impact -o impact_sweep.json"],
        recommended_docs=["docs/use-cases.md", "docs/api-handbook.md", "docs/benchmark-cards.md"],
        recommended_examples=["examples/package_tour.py"],
        recommended_notebooks=["notebooks/06_impact_workflow.ipynb"],
        expected_outputs=["BenchmarkOutput", "prediction frame", "impact metrics"],
        benchmark_cards=["synthetic_arma_impact"],
        notes=["This path is the most natural bridge to forecast-as-counterfactual adapters such as TFT-style workflows."],
    ),
    WorkflowRecipe(
        id="method-paper-sweep",
        title="Run a multi-model sweep for a methods paper",
        summary="Best for researchers comparing several models or adapters under one protocol.",
        persona="methods researcher",
        task_family="research_ops",
        best_environment="CLI + CI + structured reports",
        environment_tags=["cli", "ci", "shared-server", "release"],
        persona_tags=["methods", "researcher", "benchmark", "maintainer"],
        goal_tags=["compare", "sweep", "paper", "ablation", "benchmark"],
        why_this_exists=(
            "A paper-grade benchmark needs more than a single run. This recipe standardizes sweep matrices, error-tolerant execution,"
            " and comparison reports so experiments stay reproducible."
        ),
        what_you_do=[
            "Create a sweep spec that lists studies, models, and data source choices.",
            "Run the sweep with cell-level error tolerance for optional dependencies.",
            "Render a compact comparison report and store the JSON results for regression testing.",
        ],
        recommended_apis=["SweepMatrixSpec", "run_sweep", "render_sweep_markdown"],
        recommended_cli=["python -m tscfbench make-sweep-spec --task-family panel -o panel_sweep.json", "python -m tscfbench run-sweep panel_sweep.json -o panel_results.json", "python -m tscfbench render-sweep-report panel_sweep.json -o panel_report.md"],
        recommended_docs=["docs/benchmark-protocol.md", "docs/cli-guide.md", "docs/workflow-recipes.md"],
        recommended_examples=["examples/panel_research_demo.py"],
        recommended_notebooks=["notebooks/07_method_paper_sweep.ipynb"],
        expected_outputs=["panel_sweep.json", "panel_results.json", "panel_report.md"],
        benchmark_cards=["german_reunification", "california_prop99", "basque_country"],
        notes=["This is the path most likely to land in a benchmark appendix, CI regression suite, or paper companion repo."],
    ),
    WorkflowRecipe(
        id="agent-assisted-research",
        title="Use coding agents without blowing up token usage",
        summary="Best for research engineers using MCP, function calling, or agent-enabled IDEs.",
        persona="research engineer",
        task_family="research_ops",
        best_environment="agent-enabled IDE or tool-calling runtime",
        environment_tags=["agent", "mcp", "tool-calling", "ci", "ide"],
        persona_tags=["agent", "engineer", "automation", "mcp", "tool"],
        goal_tags=["agent", "token", "automation", "mcp", "vibe coding"],
        why_this_exists=(
            "Large benchmark artifacts are awkward in chat and IDE agents. This recipe packages experiments into specs, digests, repo maps,"
            " and bounded artifact handles so an agent can reason without seeing the whole dataset."
        ),
        what_you_do=[
            "Create a compact research task spec instead of describing the entire task in free-form text.",
            "Build an artifact bundle with manifest, digest, context plan, and optional repo map.",
            "Use function tools or MCP to fetch only the artifact slices you actually need in context.",
        ],
        recommended_apis=["AgentResearchTaskSpec", "build_panel_agent_bundle", "build_context_plan", "export_openai_function_tools"],
        recommended_cli=["python -m tscfbench make-agent-spec -o agent_spec.json", "python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir", "python -m tscfbench plan-context bundle_dir/manifest.json --phase editing"],
        recommended_docs=["docs/tutorials/agent-workflows.md", "docs/environments.md", "docs/workflow-recipes.md"],
        recommended_examples=["examples/agent_bundle_demo.py", "examples/openai_function_tools_demo.py", "examples/mcp_roundtrip_demo.py"],
        recommended_notebooks=["notebooks/05_agent_workflow.ipynb"],
        expected_outputs=["agent_spec.json", "bundle_dir/manifest.json", "context_plan.json", "OpenAI function-tool schemas"],
        notes=["This path is explicitly designed for token-aware, agent-driven research engineering."],
    ),
]


_BENCHMARK_CARDS: List[BenchmarkCard] = [
    BenchmarkCard(
        id="german_reunification",
        title="Germany: reunification as a canonical synthetic-control study",
        task_family="panel",
        canonical=True,
        question="How did West Germany's post-1990 trajectory differ from a synthetic donor-based counterfactual?",
        why_it_matters="This is one of the most recognizable comparative-politics SCM case studies, so it is ideal for public benchmark reports.",
        dataset_shape="Single treated unit in a macro panel; annual panel with multiple OECD donor countries.",
        intervention="Treatment starts at 1990 for West Germany.",
        recommended_workflows=["canonical-panel-studies", "method-paper-sweep"],
        recommended_models=["simple_scm", "did", "pysyncon_scm", "scpi_pkg"],
        outputs=["canonical report row", "placebo diagnostics", "study-specific narrative"],
        environments=["CLI", "notebook", "paper companion", "CI snapshot regression"],
        teaching_angle="Great for explaining donor pools, pre-period fit, and post/pre RMSPE ratios.",
        notes=["Good first public example because many readers already know what the study is about."],
    ),
    BenchmarkCard(
        id="california_prop99",
        title="Prop99: policy evaluation with a familiar public-health case",
        task_family="panel",
        canonical=True,
        question="How would cigarette consumption in California have evolved after Proposition 99 without the anti-smoking intervention?",
        why_it_matters="This study is intuitive to explain to applied audiences and is a natural bridge from policy analysis to formal SCM benchmarking.",
        dataset_shape="Single treated U.S. state in a state-by-year panel.",
        intervention="Treatment starts at 1989 for California.",
        recommended_workflows=["canonical-panel-studies", "custom-panel-data", "method-paper-sweep"],
        recommended_models=["simple_scm", "did", "pysyncon_augmented_scm", "scpi_pkg"],
        outputs=["canonical report row", "policy-facing narrative", "placebo tables"],
        environments=["CLI", "teaching", "workshop", "docs site"],
        teaching_angle="Excellent for showing how a benchmark case can still tell a policy story that non-methodologists understand.",
        notes=["Often the easiest case for a global audience to interpret quickly."],
    ),
    BenchmarkCard(
        id="basque_country",
        title="Basque Country: a classic economic-impact case",
        task_family="panel",
        canonical=True,
        question="How did the Basque Country's GDP per capita evolve relative to a synthetic counterfactual during the terrorism period?",
        why_it_matters="This is a foundational SCM application and a useful case for historical and economic-impact teaching.",
        dataset_shape="Single treated Spanish region in a region-by-year panel.",
        intervention="Treatment begins around 1970 in the canonical setup.",
        recommended_workflows=["canonical-panel-studies", "method-paper-sweep"],
        recommended_models=["simple_scm", "did", "pysyncon_robust_scm"],
        outputs=["canonical report row", "historical case-study page", "comparison narrative"],
        environments=["CLI", "notebook", "teaching", "case-study docs"],
        teaching_angle="Useful for explaining why canonical studies are not only technical benchmarks but also narrative teaching assets.",
        notes=["Pairs well with Germany when teaching the difference between policy and conflict case studies."],
    ),
    BenchmarkCard(
        id="synthetic_latent_factor",
        title="Synthetic latent-factor panel for method debugging",
        task_family="panel",
        canonical=False,
        question="Can a method recover a known counterfactual and effect path in a controlled panel DGP?",
        why_it_matters="Synthetic data gives you observable ground truth, which is ideal for debugging metrics and regression tests.",
        dataset_shape="Multi-unit latent-factor panel with one treated unit and known counterfactual path.",
        intervention="Configurable intervention index in synthetic generation.",
        recommended_workflows=["custom-panel-data", "method-paper-sweep", "agent-assisted-research"],
        recommended_models=["simple_scm", "did", "external adapters via sweep matrix"],
        outputs=["ground-truth error metrics", "placebo tables", "CI-safe regression fixtures"],
        environments=["notebook", "CI", "unit tests", "agent bundles"],
        teaching_angle="Ideal for showing what evaluation looks like when the counterfactual is actually known.",
        notes=["Use this card when you want deterministic tests or a minimal example that always runs."],
    ),
    BenchmarkCard(
        id="synthetic_arma_impact",
        title="Synthetic ARMA impact benchmark for single-series workflows",
        task_family="impact",
        canonical=False,
        question="Can a model reconstruct the counterfactual path of one treated series with controls after an intervention?",
        why_it_matters="It is the cleanest way to explain the impact-analysis branch of the package and to validate forecast-as-counterfactual logic.",
        dataset_shape="One observed treated series with optional controls and known post-treatment counterfactual path.",
        intervention="Configurable intervention index in synthetic generation.",
        recommended_workflows=["impact-analysis", "package-tour"],
        recommended_models=["ols_impact", "tfp_causalimpact", "forecast_cf adapters"],
        outputs=["prediction frame", "effect error metrics", "teaching notebook figures"],
        environments=["notebook", "script", "teaching"],
        teaching_angle="A good first stop when the audience thinks only in time-series rather than panel terms.",
        notes=["This card helps broaden the package identity beyond synthetic control alone."],
    ),
]


def workflow_recipes() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _RECIPES]


def benchmark_cards() -> List[Dict[str, Any]]:
    return [card.to_dict() for card in _BENCHMARK_CARDS]


def _match_score(recipe: WorkflowRecipe, *, persona: Optional[str], task_family: Optional[str], environment: Optional[str], goal: Optional[str], need_agents: Optional[bool]) -> int:
    score = 0
    persona_l = (persona or "").lower()
    task_l = (task_family or "").lower()
    env_l = (environment or "").lower()
    goal_l = (goal or "").lower()
    if task_l and (task_l == recipe.task_family.lower() or (task_l in {"panel", "impact"} and recipe.task_family.lower() == task_l)):
        score += 5
    if persona_l and any(tag in persona_l for tag in recipe.persona_tags):
        score += 4
    if env_l and any(tag in env_l for tag in recipe.environment_tags):
        score += 3
    if goal_l and any(tag in goal_l for tag in recipe.goal_tags):
        score += 4
    if need_agents is True and "agent" in recipe.environment_tags:
        score += 6
    if need_agents is False and "agent" not in recipe.environment_tags:
        score += 1
    return score


def recommend_start_path(
    *,
    persona: Optional[str] = None,
    task_family: Optional[str] = None,
    environment: Optional[str] = None,
    goal: Optional[str] = None,
    need_agents: Optional[bool] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    scored = [
        {
            "score": _match_score(recipe, persona=persona, task_family=task_family, environment=environment, goal=goal, need_agents=need_agents),
            "recipe": recipe,
        }
        for recipe in _RECIPES
    ]
    scored.sort(key=lambda item: (item["score"], item["recipe"].id != "package-tour"), reverse=True)
    selected = [item["recipe"] for item in scored[: max(1, int(top_k))]]
    primary = selected[0]
    related_cards = [card.to_dict() for card in _BENCHMARK_CARDS if card.id in primary.benchmark_cards]
    return {
        "query": {
            "persona": persona,
            "task_family": task_family,
            "environment": environment,
            "goal": goal,
            "need_agents": need_agents,
            "top_k": top_k,
        },
        "primary_recipe": primary.to_dict(),
        "recommended_recipes": [recipe.to_dict() for recipe in selected],
        "recommended_docs": sorted({doc for recipe in selected for doc in recipe.recommended_docs}),
        "recommended_examples": sorted({ex for recipe in selected for ex in recipe.recommended_examples}),
        "recommended_notebooks": sorted({nb for recipe in selected for nb in recipe.recommended_notebooks}),
        "recommended_cli": [cmd for recipe in selected for cmd in recipe.recommended_cli[:2]],
        "recommended_apis": sorted({api for recipe in selected for api in recipe.recommended_apis}),
        "benchmark_cards": related_cards,
        "why": (
            f"The top recommendation is '{primary.title}' because it best matches the requested task family, environment, and goal."
            if any([persona, task_family, environment, goal, need_agents is not None])
            else "The default recommendation starts with package orientation and then moves into a canonical benchmark, because that is the lowest-friction path for most new users."
        ),
    }


def _md_list(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_start_here_markdown(
    *,
    persona: Optional[str] = None,
    task_family: Optional[str] = None,
    environment: Optional[str] = None,
    goal: Optional[str] = None,
    need_agents: Optional[bool] = None,
) -> str:
    rec = recommend_start_path(persona=persona, task_family=task_family, environment=environment, goal=goal, need_agents=need_agents)
    primary = rec["primary_recipe"]
    lines: List[str] = []
    lines.append("# Start here")
    lines.append("")
    lines.append("**tscfbench** helps you answer a before/after question with a counterfactual, compare methods under one recipe, and save the result as a report plus agent-ready files.")
    lines.append("")
    lines.append("In plain language: give the package one treated series or one treated unit, and it helps you build the comparison, run the study, and save outputs you can read, share, or hand to an agent.")
    lines.append("")
    lines.append("## If you only do one thing")
    lines.append("")
    lines.append("Run the narrow first-run path. It uses built-in models only, bundled snapshots, and avoids optional dependencies.")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench quickstart")
    lines.append("```")
    lines.append("")
    lines.append("That command writes a spec, results JSON, report, next-steps file, and—when plotting support is available—a shareable chart into `tscfbench_quickstart/`.")
    lines.append("")
    lines.append("## If you want a more human, domain-first example")
    lines.append("")
    lines.append("Start with one of the cross-disciplinary demos. They are easier to read if words like placebo, donor pool, or synthetic control are still unfamiliar.")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench demo city-traffic")
    lines.append("python -m tscfbench demo product-launch")
    lines.append("python -m tscfbench demo heatwave-health")
    lines.append("```")
    lines.append("")
    lines.append("## What should you do after that?")
    lines.append("")
    lines.append(rec["why"])
    lines.append("")
    lines.append(f"### Recommended next path: {primary['title']}")
    lines.append("")
    lines.append(primary["summary"])
    lines.append("")
    lines.append(f"**Best environment:** {primary['best_environment']}")
    lines.append("")
    lines.append("**Why this path exists**")
    lines.append("")
    lines.append(primary["why_this_exists"])
    lines.append("")
    lines.append("**What you do in this path**")
    lines.append("")
    lines.append(_md_list(primary["what_you_do"]))
    lines.append("")
    lines.append("**Start with these CLI commands**")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench doctor")
    lines.extend(primary["recommended_cli"])
    lines.append("```")
    lines.append("")
    lines.append("**Then read / open**")
    lines.append("")
    lines.append(_md_list(rec["recommended_docs"]))
    lines.append("")
    lines.append("**Useful notebooks**")
    lines.append("")
    lines.append(_md_list(rec["recommended_notebooks"]))
    lines.append("")
    lines.append("## Common first paths")
    lines.append("")
    lines.append("| Situation | Start with | Main deliverable |")
    lines.append("|---|---|---|")
    lines.append("| I am new to the package | quickstart | zero-error canonical starter run |")
    lines.append("| I want standard public benchmarks | canonical-panel-studies | canonical report |")
    lines.append("| I have my own panel data | custom-panel-data | placebo-aware panel report |")
    lines.append("| I work on a single treated series | impact-analysis | impact metrics + prediction frame |")
    lines.append("| I need many models / many studies | method-paper-sweep | sweep JSON + comparison report |")
    lines.append("| I work with coding agents | agent-assisted-research | bundle + context plan + tools |")
    lines.append("")
    lines.append("## One important note")
    lines.append("")
    lines.append("Optional backends are useful, but they are not required for the first run. When you explicitly ask for them and they are not installed, the benchmark should mark them as skipped optional dependencies rather than looking broken.")
    lines.append("")
    return "\n".join(lines)


def render_workflow_recipes_markdown() -> str:
    lines: List[str] = []
    lines.append("# Workflow recipes")
    lines.append("")
    lines.append("These recipes explain the package from the user's point of view: situation first, API second.")
    lines.append("")
    for recipe in _RECIPES:
        lines.append(f"## {recipe.title}")
        lines.append("")
        lines.append(recipe.summary)
        lines.append("")
        lines.append(f"**Persona:** {recipe.persona}")
        lines.append("")
        lines.append(f"**Task family:** {recipe.task_family}")
        lines.append("")
        lines.append(f"**Best environment:** {recipe.best_environment}")
        lines.append("")
        lines.append("**Why this recipe exists**")
        lines.append("")
        lines.append(recipe.why_this_exists)
        lines.append("")
        lines.append("**What you do**")
        lines.append("")
        lines.append(_md_list(recipe.what_you_do))
        lines.append("")
        lines.append(f"**Recommended APIs:** {', '.join(recipe.recommended_apis)}")
        lines.append("")
        lines.append("**Recommended CLI**")
        lines.append("")
        lines.append("```bash")
        lines.extend(recipe.recommended_cli)
        lines.append("```")
        lines.append("")
        lines.append(f"**Recommended docs:** {', '.join(recipe.recommended_docs)}")
        lines.append("")
        lines.append(f"**Recommended examples:** {', '.join(recipe.recommended_examples)}")
        lines.append("")
        lines.append(f"**Recommended notebooks:** {', '.join(recipe.recommended_notebooks)}")
        lines.append("")
        lines.append(f"**Expected outputs:** {', '.join(recipe.expected_outputs)}")
        lines.append("")
        if recipe.notes:
            lines.append("**Notes**")
            lines.append("")
            lines.append(_md_list(recipe.notes))
            lines.append("")
    return "\n".join(lines)


def render_benchmark_cards_markdown() -> str:
    lines: List[str] = []
    lines.append("# Benchmark cards")
    lines.append("")
    lines.append("Each card explains what a study or benchmark fixture is for, why it matters, and in which environment it is most useful.")
    lines.append("")
    for card in _BENCHMARK_CARDS:
        lines.append(f"## {card.title}")
        lines.append("")
        lines.append(f"**Task family:** {card.task_family}")
        lines.append("")
        lines.append(f"**Canonical study:** {'yes' if card.canonical else 'no'}")
        lines.append("")
        lines.append(f"**Question:** {card.question}")
        lines.append("")
        lines.append(f"**Why it matters:** {card.why_it_matters}")
        lines.append("")
        lines.append(f"**Dataset shape:** {card.dataset_shape}")
        lines.append("")
        lines.append(f"**Intervention setup:** {card.intervention}")
        lines.append("")
        lines.append(f"**Recommended workflows:** {', '.join(card.recommended_workflows)}")
        lines.append("")
        lines.append(f"**Recommended models:** {', '.join(card.recommended_models)}")
        lines.append("")
        lines.append(f"**Typical outputs:** {', '.join(card.outputs)}")
        lines.append("")
        lines.append(f"**Works well in:** {', '.join(card.environments)}")
        lines.append("")
        lines.append(f"**Teaching angle:** {card.teaching_angle}")
        lines.append("")
        if card.notes:
            lines.append("**Notes**")
            lines.append("")
            lines.append(_md_list(card.notes))
            lines.append("")
    return "\n".join(lines)


def render_start_here_markdown(
    *,
    persona: Optional[str] = None,
    task_family: Optional[str] = None,
    environment: Optional[str] = None,
    goal: Optional[str] = None,
    need_agents: Optional[bool] = None,
) -> str:
    rec = recommend_start_path(persona=persona, task_family=task_family, environment=environment, goal=goal, need_agents=need_agents)
    primary = rec["primary_recipe"]
    lines: List[str] = []
    lines.append("# Start here")
    lines.append("")
    lines.append("**tscfbench** helps you answer a before/after question with a counterfactual, compare methods under one recipe, and save the result as a report plus agent-ready files.")
    lines.append("")
    lines.append("In plain language: give the package one treated series or one treated unit, and it helps you build the comparison, run the study, and save outputs you can read, share, or hand to an agent.")
    lines.append("")
    lines.append("## If you only do one thing")
    lines.append("")
    lines.append("Start from Python so the package looks like a library rather than a terminal wrapper.")
    lines.append("")
    lines.append("```python")
    lines.append("from tscfbench import run_demo")
    lines.append("")
    lines.append("result = run_demo(\"city-traffic\", output_dir=\"city_traffic_run\")")
    lines.append("result[\"summary\"]")
    lines.append("```")
    lines.append("")
    lines.append("If you want a fresh-environment smoke test after that, the CLI quickstart still works:")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench quickstart")
    lines.append("```")
    lines.append("")
    lines.append("That command writes a spec, results JSON, report, next-steps file, and, when plotting support is available, a shareable chart into `tscfbench_quickstart/`.")
    lines.append("")
    lines.append("## If you want a more human, domain-first example")
    lines.append("")
    lines.append("Start with one of the cross-disciplinary demos. They are easier to read if words like placebo, donor pool, or synthetic control are still unfamiliar.")
    lines.append("")
    lines.append("```python")
    lines.append("from tscfbench import run_demo")
    lines.append("")
    lines.append("run_demo(\"city-traffic\", output_dir=\"city_traffic_run\")")
    lines.append("run_demo(\"product-launch\", output_dir=\"product_launch_run\")")
    lines.append("run_demo(\"heatwave-health\", output_dir=\"heatwave_health_run\")")
    lines.append("```")
    lines.append("")
    lines.append("## If you already have your own CSV")
    lines.append("")
    lines.append("Use the DataFrame-friendly helpers first.")
    lines.append("")
    lines.append("```python")
    lines.append("import pandas as pd")
    lines.append("from tscfbench import run_panel_data")
    lines.append("")
    lines.append("df = pd.read_csv(\"my_panel.csv\")")
    lines.append("result = run_panel_data(")
    lines.append("    df,")
    lines.append("    unit_col=\"city\",")
    lines.append("    time_col=\"date\",")
    lines.append("    y_col=\"traffic_index\",")
    lines.append("    treated_unit=\"Harbor City\",")
    lines.append("    intervention_t=\"2024-03-06\",")
    lines.append(")")
    lines.append("```")
    lines.append("")
    lines.append("Read [`docs/bring-your-own-data.md`](bring-your-own-data.md) if you want both the Python and CLI shapes side by side.")
    lines.append("")
    lines.append("## What should you do after that?")
    lines.append("")
    lines.append(rec["why"])
    lines.append("")
    lines.append(f"### Recommended next path: {primary['title']}")
    lines.append("")
    lines.append(primary["summary"])
    lines.append("")
    lines.append(f"**Best environment:** {primary['best_environment']}")
    lines.append("")
    lines.append("**Why this path exists**")
    lines.append("")
    lines.append(primary["why_this_exists"])
    lines.append("")
    lines.append("**What you do in this path**")
    lines.append("")
    lines.append(_md_list(primary["what_you_do"]))
    lines.append("")
    lines.append("**Start with these CLI commands**")
    lines.append("")
    lines.append("```bash")
    lines.append("python -m tscfbench doctor")
    lines.extend(primary["recommended_cli"])
    lines.append("```")
    lines.append("")
    lines.append("**Then read / open**")
    lines.append("")
    lines.append(_md_list(rec["recommended_docs"]))
    lines.append("")
    lines.append("**Useful notebooks**")
    lines.append("")
    lines.append(_md_list(rec["recommended_notebooks"]))
    lines.append("")
    lines.append("## Common first paths")
    lines.append("")
    lines.append("| Situation | Start with | Main deliverable |")
    lines.append("|---|---|---|")
    lines.append("| I am new to the package | quickstart | zero-error canonical starter run |")
    lines.append("| I want standard public benchmarks | canonical-panel-studies | canonical report |")
    lines.append("| I have my own panel data | custom-panel-data | placebo-aware panel report |")
    lines.append("| I work on a single treated series | impact-analysis | impact metrics + prediction frame |")
    lines.append("| I need many models / many studies | method-paper-sweep | sweep JSON + comparison report |")
    lines.append("| I work with coding agents | agent-assisted-research | bundle + context plan + tools |")
    lines.append("")
    lines.append("## One important note")
    lines.append("")
    lines.append("Optional backends are useful, but they are not required for the first run. When you explicitly ask for them and they are not installed, the benchmark should mark them as skipped optional dependencies rather than looking broken.")
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "BenchmarkCard",
    "WorkflowRecipe",
    "benchmark_cards",
    "workflow_recipes",
    "recommend_start_path",
    "render_benchmark_cards_markdown",
    "render_start_here_markdown",
    "render_workflow_recipes_markdown",
]
