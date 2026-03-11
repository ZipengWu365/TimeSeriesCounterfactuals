# Why tscfbench is different

This page distills the main product-positioning claims for the package.

## Protocol-first, not estimator-first

python -m tscfbench is not trying to replace specialist estimators; it standardizes how you benchmark, compare, and package them.

**Why it matters:** Researchers often need to compare panel SCM, impact/BSTS, and forecast-as-counterfactual workflows under one reproducible protocol.

**Proof points**

- Shared case schema and prediction contract.
- Canonical benchmark specs and sweep specs.
- Adapters for specialist external ecosystems.

## Cross-ecosystem coverage

python -m tscfbench spans panel synthetic control, impact analysis, and forecast-as-counterfactual instead of living inside one methodological silo.

**Why it matters:** Real research programs rarely stay inside one library family from first benchmark to final paper or release.

**Proof points**

- Panel baselines and canonical panel studies.
- Impact-case workflow and CausalImpact-style adapters.
- Forecast-as-counterfactual bridges to Darts and StatsForecast-class backends.

## Agent-native by design

python -m tscfbench treats coding-agent workflows as a first-class target, not an afterthought.

**Why it matters:** Modern research code increasingly runs through tool-calling assistants, MCP servers, and long multi-turn editing loops where token discipline matters.

**Proof points**

- OpenAI function-tool export.
- Local MCP server surface.
- Repo maps, artifact handles, and context plans.

## Token-aware workflow packaging

python -m tscfbench is designed to reduce unnecessary context load by using bundles, manifests, digests, and artifact handles instead of giant free-form prompts.

**Why it matters:** Prompt caching works best with stable prefixes and tool lists, while editing turns benefit from compact context rather than whole-repo dumps.

**Proof points**

- Context pack + run digest pattern.
- Editing-vs-planning context plans.
- Artifact read/search/preview tools instead of full inlining.

## Release-facing docs and teaching surfaces

python -m tscfbench bakes README, docs, benchmark cards, and tutorial order into the product rather than leaving communication until the end.

**Why it matters:** Packages spread when researchers can understand them quickly, cite them, and reuse case studies without reverse-engineering the repo.

**Proof points**

- GitHub-ready README generation.
- Docs landing pages and case-study pages.
- Notebook and tutorial bundles.
