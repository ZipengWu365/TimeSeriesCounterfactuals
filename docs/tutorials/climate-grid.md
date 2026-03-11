# Climate grid tutorial

## Question

How much extra demand hit the treated grid during the climate shock window?

## Run it

```bash
python -m tscfbench demo climate-grid
python -m tscfbench make-share-package --demo-id climate-grid
```

## What you should expect

- a treated-vs-counterfactual demand chart
- donor contribution diagnostics
- a share card you can post or embed in slides
- a share package directory with report, metrics, and summary assets

![Climate grid](../assets/demo_climate_grid_share_card.png)

## Why this demo matters

This demo gives the package a climate-and-energy face. It helps explain that the same counterfactual workflow can cover grid shocks, weather events, and industrial load questions.

## How to adapt it

Use your own regional load data, public weather covariates, or tariff-change events. The same panel surface applies to climate, energy, and economics use cases.
