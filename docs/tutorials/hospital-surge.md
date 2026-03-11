# Hospital surge tutorial

## Question

How much ICU occupancy rose above counterfactual during the outbreak surge?

## Run it

```bash
python -m tscfbench demo hospital-surge
python -m tscfbench make-share-package --demo-id hospital-surge
```

## What you should expect

- an observed-vs-counterfactual ICU occupancy chart
- a cumulative excess-occupancy chart
- a share card with non-null summary fields
- a compact share package with report, metrics, prediction frame, and citation block

![Hospital surge](../assets/demo_hospital_surge_share_card.png)

## Why this demo matters

This is one of the clearest medicine-facing examples in the project. It shows that you do not need to start from synthetic-control jargon to understand what the package does.

## How to adapt it

Use your own admissions, ER visits, ICU occupancy, or local public-health series with one treated outcome and one or more controls.
