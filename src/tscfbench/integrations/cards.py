from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class AdapterCard:
    """Metadata about a built-in or optional integration.

    The point of the card is not to guarantee that the adapter is runnable in the
    current environment; instead it gives a stable schema that agents can reason
    over when assembling research stacks, install plans, and runtime profiles.
    """

    id: str
    display_name: str
    task_family: str
    backend: str
    import_names: List[str]
    pip_packages: List[str]
    extra_group: str
    maturity: str
    summary: str
    strengths: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    interval_support: bool = False
    placebo_support: bool = False
    agent_fit: str = "medium"
    runtime_cost: str = "medium"
    adapter_class: Optional[str] = None

    def available(self) -> bool:
        if not self.import_names:
            return True
        return any(importlib.util.find_spec(name) is not None for name in self.import_names)

    def missing_imports(self) -> List[str]:
        if not self.import_names:
            return []
        return [name for name in self.import_names if importlib.util.find_spec(name) is None]

    def install_hint(self) -> str:
        if not self.pip_packages:
            return "No additional install needed."
        pkgs = " ".join(self.pip_packages)
        return f"pip install {pkgs}"

    def to_dict(self, include_availability: bool = True) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "display_name": self.display_name,
            "task_family": self.task_family,
            "backend": self.backend,
            "import_names": list(self.import_names),
            "pip_packages": list(self.pip_packages),
            "extra_group": self.extra_group,
            "maturity": self.maturity,
            "summary": self.summary,
            "strengths": list(self.strengths),
            "caveats": list(self.caveats),
            "interval_support": bool(self.interval_support),
            "placebo_support": bool(self.placebo_support),
            "agent_fit": self.agent_fit,
            "runtime_cost": self.runtime_cost,
            "adapter_class": self.adapter_class,
            "install_hint": self.install_hint(),
        }
        if include_availability:
            payload["available"] = self.available()
            payload["missing_imports"] = self.missing_imports()
        return payload


_ADAPTERS: List[AdapterCard] = [
    AdapterCard(
        id="simple_scm_builtin",
        display_name="Built-in Simple Synthetic Control",
        task_family="panel",
        backend="tscfbench",
        import_names=[],
        pip_packages=[],
        extra_group="core",
        maturity="stable",
        summary="Lightweight synthetic-control baseline with simplex-projected donor weights.",
        strengths=["minimal dependencies", "easy to audit", "works in smoke tests"],
        caveats=["single treated unit", "basic uncertainty handling"],
        placebo_support=True,
        agent_fit="high",
        runtime_cost="low",
        adapter_class="tscfbench.models.synthetic_control.SimpleSyntheticControl",
    ),
    AdapterCard(
        id="did_builtin",
        display_name="Built-in Difference-in-Differences",
        task_family="panel",
        backend="tscfbench",
        import_names=[],
        pip_packages=[],
        extra_group="core",
        maturity="stable",
        summary="Simple DiD baseline for ablation and sanity checks.",
        strengths=["fast", "interpretable", "good benchmark floor"],
        caveats=["parallel trends assumption", "no donor weighting"],
        placebo_support=True,
        agent_fit="high",
        runtime_cost="low",
        adapter_class="tscfbench.models.did.DifferenceInDifferences",
    ),
    AdapterCard(
        id="ols_impact_builtin",
        display_name="Built-in OLS Impact",
        task_family="impact",
        backend="tscfbench",
        import_names=[],
        pip_packages=[],
        extra_group="core",
        maturity="stable",
        summary="CausalImpact-style pre-period regression baseline over controls/covariates.",
        strengths=["minimal dependencies", "good baseline for impact tasks"],
        caveats=["Gaussian linearity assumptions", "basic intervals"],
        interval_support=True,
        agent_fit="high",
        runtime_cost="low",
        adapter_class="tscfbench.models.ols.OLSImpact",
    ),
    AdapterCard(
        id="pysyncon",
        display_name="pysyncon",
        task_family="panel",
        backend="external",
        import_names=["pysyncon"],
        pip_packages=["pysyncon"],
        extra_group="research",
        maturity="research",
        summary="Synthetic-control family with robust / augmented / penalized variants plus placebo and confidence interval support.",
        strengths=["multiple SCM variants", "placebo tests", "confidence intervals"],
        caveats=["optional dependency", "API may evolve independently of tscfbench"],
        interval_support=True,
        placebo_support=True,
        agent_fit="medium",
        runtime_cost="medium",
        adapter_class="tscfbench.integrations.adapters.PysynconPanelAdapter",
    ),
    AdapterCard(
        id="scpi",
        display_name="SCPI",
        task_family="panel",
        backend="external",
        import_names=["scpi_pkg", "scpi"],
        pip_packages=["scpi_pkg"],
        extra_group="research",
        maturity="research",
        summary="Prediction and inference procedures for synthetic control with inference, multiple treated units, and staggered adoption support.",
        strengths=["inference focused", "multiple treated units", "staggered adoption support"],
        caveats=["heavier stack", "integration surface is broader than v0.5 core"],
        interval_support=True,
        placebo_support=True,
        agent_fit="medium",
        runtime_cost="medium",
        adapter_class="tscfbench.integrations.adapters.SCPIAdapter",
    ),
    AdapterCard(
        id="synthetic_control_methods",
        display_name="SyntheticControlMethods",
        task_family="panel",
        backend="external",
        import_names=["SyntheticControlMethods"],
        pip_packages=["SyntheticControlMethods"],
        extra_group="research",
        maturity="community",
        summary="Python SCM implementation with a simple panel-data entry point and visualization workflow.",
        strengths=["simple panel API", "classical SCM workflow"],
        caveats=["narrower method family", "external API stability"],
        placebo_support=False,
        agent_fit="medium",
        runtime_cost="medium",
        adapter_class="tscfbench.integrations.adapters.SyntheticControlMethodsAdapter",
    ),
    AdapterCard(
        id="causalpy",
        display_name="CausalPy",
        task_family="quasi_experiment",
        backend="external",
        import_names=["causalpy"],
        pip_packages=["CausalPy"],
        extra_group="research",
        maturity="research",
        summary="Broader quasi-experimental Python library spanning synthetic control and Bayesian/OLS workflows.",
        strengths=["broad quasi-experimental toolbox", "Bayesian and OLS options"],
        caveats=["broader than pure time-series counterfactual scope"],
        interval_support=True,
        placebo_support=False,
        agent_fit="medium",
        runtime_cost="medium",
        adapter_class="tscfbench.integrations.adapters.CausalPyAdapter",
    ),
    AdapterCard(
        id="tfp_causalimpact",
        display_name="TFP CausalImpact",
        task_family="impact",
        backend="external",
        import_names=["causalimpact"],
        pip_packages=["tfp-causalimpact"],
        extra_group="research",
        maturity="research",
        summary="Python TensorFlow Probability implementation of CausalImpact-style BSTS analysis.",
        strengths=["Bayesian impact analysis", "uncertainty intervals", "familiar CausalImpact framing"],
        caveats=["control-series assumptions", "TensorFlow Probability dependency"],
        interval_support=True,
        agent_fit="medium",
        runtime_cost="high",
        adapter_class="tscfbench.integrations.causalimpact.TFPCausalImpactAdapter",
    ),
    AdapterCard(
        id="cimpact",
        display_name="CImpact",
        task_family="impact",
        backend="external",
        import_names=["cimpact"],
        pip_packages=["cimpact"],
        extra_group="research",
        maturity="experimental",
        summary="Modular impact-analysis library supporting multiple backends such as TensorFlow Probability, Prophet, and Pyro.",
        strengths=["multiple backends", "impact-oriented API"],
        caveats=["package availability may vary by environment", "heavier dependency tree"],
        interval_support=True,
        agent_fit="low",
        runtime_cost="high",
        adapter_class="tscfbench.integrations.adapters.CImpactAdapter",
    ),
    AdapterCard(
        id="darts_forecast_cf",
        display_name="Darts Forecast-as-Counterfactual",
        task_family="forecast_cf",
        backend="external",
        import_names=["darts"],
        pip_packages=["darts"],
        extra_group="forecast",
        maturity="community",
        summary="Forecasting framework with unified fit/predict API that can be wrapped as a forecast-as-counterfactual backend.",
        strengths=["unified API", "many forecasting models", "probabilistic forecasts"],
        caveats=["not a native causal package", "benchmark protocol needs explicit counterfactual assumptions"],
        interval_support=True,
        agent_fit="medium",
        runtime_cost="medium",
        adapter_class="tscfbench.integrations.adapters.DartsForecastAdapter",
    ),
    AdapterCard(
        id="statsforecast_cf",
        display_name="StatsForecast Forecast-as-Counterfactual",
        task_family="forecast_cf",
        backend="external",
        import_names=["statsforecast"],
        pip_packages=["statsforecast"],
        extra_group="forecast",
        maturity="stable",
        summary="Statistical forecasting library suitable for large-scale forecasting baselines and forecast-as-counterfactual experiments.",
        strengths=["fast statistical models", "good benchmark baseline", "scales to many series"],
        caveats=["not a native causal package", "requires explicit design choices for post-treatment evaluation"],
        interval_support=True,
        agent_fit="high",
        runtime_cost="low",
        adapter_class="tscfbench.integrations.adapters.StatsForecastCounterfactualAdapter",
    ),
    AdapterCard(
        id="pytorch_forecasting_tft",
        display_name="PyTorch Forecasting TFT",
        task_family="forecast_cf",
        backend="external",
        import_names=["pytorch_forecasting"],
        pip_packages=["pytorch-forecasting"],
        extra_group="forecast",
        maturity="stable",
        summary="Deep-learning forecasting library including Temporal Fusion Transformer for multi-horizon forecasting.",
        strengths=["TFT available", "multi-horizon training", "interpretability tooling"],
        caveats=["GPU/Lightning stack", "not a native causal package", "heavier token footprint for code generation"],
        interval_support=True,
        agent_fit="low",
        runtime_cost="high",
        adapter_class="tscfbench.integrations.adapters.GenericForecastCounterfactualAdapter",
    ),
]


def list_adapter_cards(*, include_availability: bool = True) -> List[AdapterCard]:
    return list(_ADAPTERS)


def adapter_catalog(*, include_availability: bool = True) -> List[Dict[str, Any]]:
    return [card.to_dict(include_availability=include_availability) for card in _ADAPTERS]


def get_adapter_card(adapter_id: str) -> AdapterCard:
    for card in _ADAPTERS:
        if card.id == adapter_id:
            return card
    raise KeyError(f"Unknown adapter id: {adapter_id}")


def group_install_profiles() -> Dict[str, List[str]]:
    profiles: Dict[str, List[str]] = {}
    for card in _ADAPTERS:
        profiles.setdefault(card.extra_group, [])
        for pkg in card.pip_packages:
            if pkg not in profiles[card.extra_group]:
                profiles[card.extra_group].append(pkg)
    return profiles


def recommend_adapter_stack(
    *,
    task_family: str = "panel",
    goal: str = "research",
    token_aware: bool = True,
    max_adapters: int = 6,
) -> List[Dict[str, Any]]:
    task_family = str(task_family).strip().lower()
    goal = str(goal).strip().lower()

    preferred_task_aliases = {
        "panel": {"panel", "quasi_experiment"},
        "impact": {"impact", "quasi_experiment"},
        "forecast_cf": {"forecast_cf"},
    }
    task_set = preferred_task_aliases.get(task_family, {task_family})

    rows: List[tuple[float, AdapterCard, str]] = []
    for card in _ADAPTERS:
        if card.task_family not in task_set and not (task_family == "panel" and card.id in {"did_builtin"}):
            continue
        score = 0.0
        reasons: List[str] = []
        if card.backend == "tscfbench":
            score += 4.0
            reasons.append("built-in baseline")
        if goal == "research":
            if card.placebo_support:
                score += 2.5
                reasons.append("placebo-friendly")
            if card.interval_support:
                score += 1.5
                reasons.append("supports intervals or inference")
            if card.maturity in {"stable", "research"}:
                score += 1.0
        if token_aware:
            if card.agent_fit == "high":
                score += 2.0
                reasons.append("agent-friendly surface")
            elif card.agent_fit == "medium":
                score += 0.7
            else:
                score -= 0.5
            if card.runtime_cost == "low":
                score += 1.2
                reasons.append("low runtime cost")
            elif card.runtime_cost == "high":
                score -= 0.8
        if card.available():
            score += 0.8
            reasons.append("available in current environment")
        rows.append((score, card, ", ".join(reasons) or "general fit"))

    rows.sort(key=lambda x: (-x[0], x[1].id))
    out: List[Dict[str, Any]] = []
    for score, card, reason in rows[: max(1, int(max_adapters))]:
        payload = card.to_dict(include_availability=True)
        payload["recommendation_score"] = round(float(score), 3)
        payload["recommendation_reason"] = reason
        out.append(payload)
    return out


__all__ = [
    "AdapterCard",
    "adapter_catalog",
    "get_adapter_card",
    "group_install_profiles",
    "list_adapter_cards",
    "recommend_adapter_stack",
]
