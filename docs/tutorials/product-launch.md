# Tutorial: product launch signups

This is the beginner-friendly **one event, one metric, two controls** impact example.

![Product launch share card](../assets/demo_product_launch_share_card.png)

## Run it

```bash
python -m tscfbench demo product-launch
```

## Question

How many extra signups appeared after a feature launch, relative to a counterfactual path predicted from related control series?

## What this writes

- `impact_metrics.json`
- `impact_report.md`
- `impact_prediction_frame.csv`
- treated-vs-counterfactual PNG/SVG
- cumulative-impact PNG/SVG
- share-card PNG/SVG

## Why this tutorial exists

Product and growth teams often have a clean before/after story but do not want to learn an entire causal-inference vocabulary before getting a usable answer.

## Bring your own CSV

```bash
python -m tscfbench run-csv-impact your_signups.csv \
  --time-col date \
  --y-col signups \
  --x-cols peer_signups search_interest \
  --intervention-t 2024-04-23
```
