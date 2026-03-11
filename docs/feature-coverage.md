# Feature coverage matrix

This matrix summarizes **primary documented focus** in reviewed public materials. It is not a proof that a package cannot do something beyond the table; it is a positioning aid for README and docs.

## Legend

- **Primary** — Primary documented focus
- **Native** — Native package feature
- **Bridge** — Bridge / adapter / benchmark wrapper
- **Partial** — Partial or adjacent documented support
- **Not primary** — Not the primary documented package focus in reviewed materials

| feature | tscfbench | pysyncon | scpi | synthetic_control_methods | tfp_causalimpact | tfcausalimpact | cimpact | causalpy | darts | statsforecast |
|---|---|---|---|---|---|---|---|---|---|---|
| Primary documented package scope | Benchmark / workflow / agent | Panel SCM | Panel SCM + inference | Panel SCM | Impact / BSTS | Impact / BSTS | Impact / modular backends | Broad quasi-experimental | Forecasting | Forecasting |
| Panel synthetic-control workflows | Native + bridge | Primary | Primary | Primary | Not primary | Not primary | Not primary | Partial | Not primary | Not primary |
| Impact / BSTS event analysis | Native + bridge | Not primary | Not primary | Not primary | Primary | Primary | Primary | Not primary | Not primary | Not primary |
| Forecast-as-counterfactual route | Bridge | Not primary | Not primary | Not primary | Not primary | Not primary | Partial | Not primary | Primary | Primary |
| Canonical benchmark studies and study runners | Native | Partial | Partial | Partial | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary |
| JSON-first experiment specs and CLI reproducibility | Native | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary |
| Agent tool / MCP / structured workflow surface | Native | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary |
| Token-aware artifact packaging and context planning | Native | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary | Not primary |

## Why these rows

### Primary documented package scope

This tells users what job each package is fundamentally built to do.

### Panel synthetic-control workflows

Core need for Germany / Prop99 / Basque-style comparative case studies.

### Impact / BSTS event analysis

Needed for CausalImpact-style counterfactual analyses with one treated series and controls.

### Forecast-as-counterfactual route

Useful when researchers want to benchmark forecasting models as counterfactual generators.

### Canonical benchmark studies and study runners

A benchmark package is easier to trust and teach when it ships recognizable studies and report workflows.

### JSON-first experiment specs and CLI reproducibility

This matters for CI, paper companions, and agent-driven reruns where notebook state is fragile.

### Agent tool / MCP / structured workflow surface

This matters when research code is driven through tool-calling assistants instead of one-shot notebook sessions.

### Token-aware artifact packaging and context planning

Important for lower-cost, lower-latency agent use and cleaner editing turns.
