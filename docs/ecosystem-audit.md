# Ecosystem audit

Reviewed on 2026-03-08.

The goal of this audit is not to claim that tscfbench supersedes specialist estimators. The goal is to clarify where specialist packages are strongest and where tscfbench adds a distinct benchmark, workflow, and agent-oriented layer.

## Core thesis

- Use specialist packages when you need one estimator family deeply.
- Use tscfbench when you need shared protocols, recognizable benchmark studies, reproducible specs, or agent-friendly research workflows across families.
- The most accurate positioning is 'benchmark-and-workflow layer over specialist backends', not 'another estimator package'.

## Reviewed packages

### tscfbench

**Category:** benchmark + workflow + agent layer

**Primary job:** Define shared benchmark protocols across panel, impact, and forecast-as-counterfactual workflows; then package results for CLI, docs, CI, and agents.

**Documented strengths**

- Canonical studies, sweep specs, and Markdown reports.
- Bridge layer over specialist estimator ecosystems instead of forcing one modeling family.
- Agent-native surfaces such as function tools, MCP, artifact handles, context plans, and repo maps.

**Best when:** You need a research workflow package, not just a single estimator package.

**How tscfbench relates:** This is the orchestration and dissemination layer. It complements, rather than replaces, specialist estimation packages.

### pysyncon

**Category:** panel SCM family

**Primary job:** Implement classical, robust, augmented, and penalized synthetic control in Python.

**Documented strengths**

- Multiple SCM variants.
- Placebo tests and confidence intervals.
- Examples reproducing landmark SCM studies.

**Best when:** You want a focused synthetic-control estimator package and are already committed to the SCM family.

**How tscfbench relates:** tscfbench should use pysyncon as a specialist backend inside a broader benchmark protocol.

**Reviewed sources**

- https://pypi.org/project/pysyncon/
- https://github.com/sdfordham/pysyncon

### SCPI

**Category:** panel SCM inference

**Primary job:** Estimate synthetic controls with uncertainty quantification, including multiple treated units and staggered adoption settings.

**Documented strengths**

- Prediction intervals and inference emphasis.
- Multiple treated units.
- Staggered adoption support.

**Best when:** You need synthetic-control inference, especially beyond the simplest one-treated-unit setup.

**How tscfbench relates:** tscfbench should benchmark around SCPI and standardize how its outputs are compared against other families.

**Reviewed sources**

- https://pypi.org/project/scpi-pkg/
- https://github.com/nppackages/scpi

### SyntheticControlMethods

**Category:** panel SCM

**Primary job:** Offer a straightforward Python entry point for classical synthetic control workflows on panel data.

**Documented strengths**

- Simple entry point for classical SCM.
- Germany reunification example and visualization workflow.

**Best when:** You want a direct Python SCM class with a classical workflow and lightweight mental model.

**How tscfbench relates:** tscfbench can wrap it for recognizable benchmarks, but it is narrower than tscfbench's protocol and workflow scope.

**Reviewed sources**

- https://github.com/OscarEngelbrektson/SyntheticControlMethods

### TFP CausalImpact

**Category:** impact / BSTS

**Primary job:** Run CausalImpact-style Bayesian structural time-series analysis in Python via TensorFlow Probability.

**Documented strengths**

- Direct CausalImpact framing.
- Bayesian impact analysis with intervals.
- Familiar pre-period / post-period workflow.

**Best when:** You specifically want CausalImpact-style impact analysis rather than a cross-method benchmark stack.

**How tscfbench relates:** tscfbench should treat this as a specialist impact backend and compare it under a shared spec with simpler baselines and forecast-as-counterfactual routes.

**Reviewed sources**

- https://pypi.org/project/tfp-causalimpact/
- https://github.com/google/tfp-causalimpact

### tfcausalimpact

**Category:** impact / BSTS

**Primary job:** Provide a TensorFlow Probability implementation of Google's CausalImpact algorithm with variational and HMC fitting options.

**Documented strengths**

- Direct causal-impact workflow.
- Published performance trade-off between VI and HMC.
- Public fixtures and examples.

**Best when:** You want a standalone impact-analysis package with a familiar CausalImpact API.

**How tscfbench relates:** tscfbench can wrap or benchmark around it, but its purpose is broader and more protocol-oriented.

**Reviewed sources**

- https://pypi.org/project/tfcausalimpact/
- https://github.com/WillianFuks/tfcausalimpact

### CImpact

**Category:** impact / modular backends

**Primary job:** Offer modular impact analysis over multiple backends such as TensorFlow Probability, Prophet, and Pyro.

**Documented strengths**

- Multiple impact-analysis backends.
- Explicit modular adapter architecture.
- Impact-oriented visualization and evaluation.

**Best when:** You want to stay inside impact analysis while comparing multiple backend model families.

**How tscfbench relates:** tscfbench should treat CImpact as a backend family and add benchmark protocol, canonical studies, and agent/runtime packaging around it.

**Reviewed sources**

- https://github.com/Sanofi-Public/CImpact

### CausalPy

**Category:** broad quasi-experimental

**Primary job:** Provide a broad Python package for quasi-experimental causal inference across designs such as synthetic control and regression discontinuity.

**Documented strengths**

- Broad quasi-experimental scope.
- Bayesian and OLS workflows.
- Clear quickstart and model abstractions.

**Best when:** You need a broad quasi-experimental toolbox rather than a time-series counterfactual benchmark platform.

**How tscfbench relates:** tscfbench is narrower methodologically but broader operationally: it focuses on time-series counterfactual benchmarking and agent-friendly workflow packaging.

**Reviewed sources**

- https://pypi.org/project/causalpy/
- https://github.com/pymc-labs/CausalPy

### Darts

**Category:** forecasting

**Primary job:** Expose a user-friendly unified forecasting API spanning statistical and deep models, backtesting, and probabilistic forecasting.

**Documented strengths**

- Unified fit/predict API.
- Probabilistic forecasting and backtesting.
- Many forecasting models and covariate support.

**Best when:** You want a general forecasting framework, especially for forecast-as-counterfactual experiments.

**How tscfbench relates:** tscfbench uses Darts as a forecasting backend candidate, then adds counterfactual protocol, study specs, and agent/runtime packaging on top.

**Reviewed sources**

- https://github.com/unit8co/darts

### StatsForecast

**Category:** forecasting

**Primary job:** Scale statistical forecasting with fast fit/predict, probabilistic forecasts, and exogenous-variable support.

**Documented strengths**

- Large-scale statistical forecasting.
- Prediction intervals.
- Exogenous variable support and distributed runtimes.

**Best when:** You need strong scalable forecasting baselines or forecast-as-counterfactual experiments over many series.

**How tscfbench relates:** tscfbench should treat StatsForecast as a scalable baseline engine, then add causal benchmark protocol and dissemination surfaces around it.

**Reviewed sources**

- https://nixtlaverse.nixtla.io/statsforecast/
- https://github.com/Nixtla/statsforecast
