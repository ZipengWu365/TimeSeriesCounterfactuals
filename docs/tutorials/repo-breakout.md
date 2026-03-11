# Repo breakout tutorial

## Question

Was the repo's breakout real, or was it already on that path?

## Run it

```bash
python -m tscfbench demo repo-breakout
python -m tscfbench make-share-package --demo-id repo-breakout
```

## What you should expect

- a treated-vs-counterfactual daily-stars chart
- a cumulative impact chart
- a social share card
- a share package with `summary.json`, `SUMMARY.md`, `report.md`, metrics, and the prediction frame

![Repo breakout](../assets/demo_repo_breakout_share_card.png)

## Why this demo matters

This is the most internet-native demo in the package. It gives the repo a chart people can understand in seconds and a share package that can move across GitHub, X, talks, and docs.

## How to adapt it

Swap in your own GitHub stars, signups, search interest, or product-attention series. The point is not GitHub specifically; it is that public attention can be studied with the same counterfactual workflow.
