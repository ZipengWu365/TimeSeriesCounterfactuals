# Plain-language guide

This page explains `tscfbench` without assuming causal-inference jargon.

## The core question

A before/after question sounds simple:

- Did the launch really increase signups?
- Did the heatwave really increase ER visits?
- Did the outage really change grid demand?

The hard part is deciding what would have happened **otherwise**.

`tscfbench` helps you estimate that missing path and package the result into a chart, a report, and a shareable handoff.

## Translations from research language to everyday language

- **Counterfactual** → the path you think would have happened without the event.
- **Treated series** → the one series you care about.
- **Controls** → other series that help anchor the missing baseline.
- **Donor pool** → the comparison units used to build a synthetic baseline.
- **Placebo test** → a sanity check asking whether the same method would claim an effect where there should be none.

## Three beginner patterns

### One product launch
Use one outcome series and a few control series.

### One treated region
Use one treated city/state/region and several comparison units.

### One public event
Use a public attention or market series with peer-series controls.

## What makes `tscfbench` different from just installing a model package?

A model package gives you an estimate. `tscfbench` gives you the estimate **plus the workflow output**: charts, a report, a share package, and agent-ready structured files.
