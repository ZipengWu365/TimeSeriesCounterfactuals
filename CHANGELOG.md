# Changelog

## v1.8.0

- unified onboarding around `.[starter]` and `python -m tscfbench ...`
- added a documented release-asset wheel install path for non-editable installs
- fixed impact/share-package summaries so flagship demos emit non-null result fields
- promoted repo-breakout, hospital-surge, and climate-grid to README-level showcases
- upgraded key notebooks from thin stubs to walkthrough notebooks with checked outputs

## v1.5.0

- Recommend `.[viz]` for the first run while keeping SVG fallback visuals on minimal installs.
- Add flagship demos for climate-grid, hospital-surge, and repo-breakout.
- Add one-command share packages with charts, share cards, a short summary, and a citation block.
- Upgrade README/docs toward a more visual, cross-disciplinary first impression.


## 1.4.0 — 2026-03-08

- added chart-first quickstart assets, including a treated-vs-counterfactual hero chart and share card
- added six one-command demos (`city-traffic`, `product-launch`, `heatwave-health`, `electricity-shock`, `github-stars`, `crypto-event`)
- added `run-csv-panel` and `run-csv-impact` for plain-language CSV-in/report-out workflows
- narrowed the onboarding story around `python -m ...` commands for cross-platform reliability
- reduced the smallest tool profile to a tighter onboarding surface while keeping research and full profiles available
- fixed datetime intervention handling for CSV-driven panel and impact cases
- refreshed README, docs home, quickstart, demo gallery, and cross-disciplinary tutorials with real visual assets

## 1.3.0 — 2026-03-08

- narrowed the default first-run path with `quickstart`, built-in-only canonical defaults, and clearer onboarding
- fixed `estimate-tokens` JSON serialization and added a positional target argument
- added runtime profile aliases and tool export profiles (`minimal`, `research`, `full`)
- classified missing optional backends as `skipped_optional_dependency` instead of hard benchmark errors
- refreshed GitHub/website copy around package positioning, optional backend policy, and beginner-first usage

## 1.2.0 — 2026-03-08

### Added

- ecosystem-audit, feature-coverage, differentiators, github-readme, website-home, and agent-first-design narrative surfaces,
- a peer-package landscape comparing tscfbench with pysyncon, SCPI, SyntheticControlMethods, TFP CausalImpact, tfcausalimpact, CImpact, CausalPy, Darts, and StatsForecast,
- GitHub- and website-facing positioning asset generation for README, landing page, feature matrix, and ecosystem audit exports,
- new docs pages and release-kit assets for package differentiation and agent-first design.

### Changed

- README is now GitHub-first and explicitly explains what tscfbench is, what it is not, and where it fits relative to specialist packages,
- docs home page now routes users through positioning, comparison, and agent-first adoption instead of only module discovery,
- release-kit generation now includes positioning assets in addition to story/tutorial assets.

## 1.1.0 — 2026-03-07

### Added

- package-story, capability-map, api-atlas, scenario-matrix, and tutorial-index narrative surfaces,
- release-kit generation for README/docs/paper-companion style exports,
- high-traffic public case catalog for GitHub-star, crypto, and commodity event studies,
- public data loaders for GitHub stargazers, CoinGecko market-chart data, and FRED series,
- event-style `ImpactCase` construction helpers for public time-series data,
- new docs, tutorials, examples, and notebooks for public-facing case studies.

### Changed

- README and docs landing pages now explain the package in product terms before they explain modules,
- CLI and agent tool surfaces now expose the new narrative and showcase layers.
