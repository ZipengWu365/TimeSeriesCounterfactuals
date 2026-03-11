# FAQ

## Is this a modeling library or a benchmark library?

It is primarily a **benchmark-and-workflow library**. It includes some built-in baselines, but its main value is the shared protocol, reproducibility surface, and surrounding workflow tools.

## Do I need to use the canonical studies?

No. They are there because they are recognizable and easy to teach. If you have your own data, start with `PanelCase` or `ImpactCase`.

## Why does the package talk about agents and tokens?

Because more research workflows now include coding agents. Large benchmark outputs are hard to move through a chat or tool-calling runtime. The bundle/context-plan layer exists to keep those workflows structured and efficient.

## Should beginners start with external adapters?

Usually no. Start with the built-in baselines and the benchmark protocol. Add optional ecosystems only after you understand what comparison you want to make.

## When should I use the CLI instead of the Python API?

Use the Python API when you are still shaping a custom workflow. Use the CLI when you want reproducibility, easier onboarding, or a command sequence that maps directly to docs and CI.
