# Benchmark cards

Each card explains what a study or benchmark fixture is for, why it matters, and in which environment it is most useful.

## Germany: reunification as a canonical synthetic-control study

**Task family:** panel

**Canonical study:** yes

**Question:** How did West Germany's post-1990 trajectory differ from a synthetic donor-based counterfactual?

**Why it matters:** This is one of the most recognizable comparative-politics SCM case studies, so it is ideal for public benchmark reports.

**Dataset shape:** Single treated unit in a macro panel; annual panel with multiple OECD donor countries.

**Intervention setup:** Treatment starts at 1990 for West Germany.

**Recommended workflows:** canonical-panel-studies, method-paper-sweep

**Recommended models:** simple_scm, did, pysyncon_scm, scpi_pkg

**Typical outputs:** canonical report row, placebo diagnostics, study-specific narrative

**Works well in:** CLI, notebook, paper companion, CI snapshot regression

**Teaching angle:** Great for explaining donor pools, pre-period fit, and post/pre RMSPE ratios.

**Notes**

- Good first public example because many readers already know what the study is about.

## Prop99: policy evaluation with a familiar public-health case

**Task family:** panel

**Canonical study:** yes

**Question:** How would cigarette consumption in California have evolved after Proposition 99 without the anti-smoking intervention?

**Why it matters:** This study is intuitive to explain to applied audiences and is a natural bridge from policy analysis to formal SCM benchmarking.

**Dataset shape:** Single treated U.S. state in a state-by-year panel.

**Intervention setup:** Treatment starts at 1989 for California.

**Recommended workflows:** canonical-panel-studies, custom-panel-data, method-paper-sweep

**Recommended models:** simple_scm, did, pysyncon_augmented_scm, scpi_pkg

**Typical outputs:** canonical report row, policy-facing narrative, placebo tables

**Works well in:** CLI, teaching, workshop, docs site

**Teaching angle:** Excellent for showing how a benchmark case can still tell a policy story that non-methodologists understand.

**Notes**

- Often the easiest case for a global audience to interpret quickly.

## Basque Country: a classic economic-impact case

**Task family:** panel

**Canonical study:** yes

**Question:** How did the Basque Country's GDP per capita evolve relative to a synthetic counterfactual during the terrorism period?

**Why it matters:** This is a foundational SCM application and a useful case for historical and economic-impact teaching.

**Dataset shape:** Single treated Spanish region in a region-by-year panel.

**Intervention setup:** Treatment begins around 1970 in the canonical setup.

**Recommended workflows:** canonical-panel-studies, method-paper-sweep

**Recommended models:** simple_scm, did, pysyncon_robust_scm

**Typical outputs:** canonical report row, historical case-study page, comparison narrative

**Works well in:** CLI, notebook, teaching, case-study docs

**Teaching angle:** Useful for explaining why canonical studies are not only technical benchmarks but also narrative teaching assets.

**Notes**

- Pairs well with Germany when teaching the difference between policy and conflict case studies.

## Synthetic latent-factor panel for method debugging

**Task family:** panel

**Canonical study:** no

**Question:** Can a method recover a known counterfactual and effect path in a controlled panel DGP?

**Why it matters:** Synthetic data gives you observable ground truth, which is ideal for debugging metrics and regression tests.

**Dataset shape:** Multi-unit latent-factor panel with one treated unit and known counterfactual path.

**Intervention setup:** Configurable intervention index in synthetic generation.

**Recommended workflows:** custom-panel-data, method-paper-sweep, agent-assisted-research

**Recommended models:** simple_scm, did, external adapters via sweep matrix

**Typical outputs:** ground-truth error metrics, placebo tables, CI-safe regression fixtures

**Works well in:** notebook, CI, unit tests, agent bundles

**Teaching angle:** Ideal for showing what evaluation looks like when the counterfactual is actually known.

**Notes**

- Use this card when you want deterministic tests or a minimal example that always runs.

## Synthetic ARMA impact benchmark for single-series workflows

**Task family:** impact

**Canonical study:** no

**Question:** Can a model reconstruct the counterfactual path of one treated series with controls after an intervention?

**Why it matters:** It is the cleanest way to explain the impact-analysis branch of the package and to validate forecast-as-counterfactual logic.

**Dataset shape:** One observed treated series with optional controls and known post-treatment counterfactual path.

**Intervention setup:** Configurable intervention index in synthetic generation.

**Recommended workflows:** impact-analysis, package-tour

**Recommended models:** ols_impact, tfp_causalimpact, forecast_cf adapters

**Typical outputs:** prediction frame, effect error metrics, teaching notebook figures

**Works well in:** notebook, script, teaching

**Teaching angle:** A good first stop when the audience thinks only in time-series rather than panel terms.

**Notes**

- This card helps broaden the package identity beyond synthetic control alone.
