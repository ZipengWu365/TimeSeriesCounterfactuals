# AGENTS.md

This repository is optimized for **research-first, token-efficient, agent-assisted development**.

## Working rules

- Prefer **JSON specs** over long natural-language prompts.
- Prefer **artifact handles** over inlining large tables.
- Keep **planning/retrieval** and **editing** in separate turns when using coding agents.
- When changing benchmark logic, update:
  - the runnable code,
  - the canonical report templates,
  - the tutorial or case-study page,
  - and the regression tests.
- Do not silently change benchmark metrics or placebo rules.
- Preserve English-first docs and CLI help text.

## Benchmark discipline

If you change canonical studies or dataset loaders:

1. keep schema compatibility when possible,
2. update the snapshot fixtures or their tests,
3. update `docs/case-studies/` and `README.md`,
4. record any compatibility caveat in release notes.

## Documentation discipline

Every public feature should land with:

- at least one CLI example,
- one docs page or tutorial section,
- and one regression test.

## Preferred edit style

- patch the smallest surface that solves the task,
- keep diffs readable,
- keep return payloads compact,
- avoid adding heavy dependencies unless they are behind an optional extra.
