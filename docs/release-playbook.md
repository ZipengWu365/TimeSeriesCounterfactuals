# Release playbook

Use this page when you want **tscfbench** to spread beyond its original maintainers.

## The package needs three surfaces

1. **A product surface** — what the package is, what it is not, and why it exists.
2. **A scenario surface** — which workflow fits which user and environment.
3. **A proof surface** — recognizable cases, reports, notebooks, and public data demos.

## A good public release should include

- a README that explains the package before it explains the code,
- one canonical benchmark report,
- one high-attention public case,
- a tutorial index,
- benchmark cards,
- and a small release kit that can be copied into a docs site or paper companion.

## Generate the release kit

```bash
python -m tscfbench make-release-kit -o release_kit
```

The generated directory includes a package story, capability map, API atlas, scenario matrix, tutorial index, benchmark cards, and a start-here page.
