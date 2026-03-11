from __future__ import annotations

from tscfbench.canonical import CanonicalBenchmarkSpec, render_canonical_markdown, run_canonical_benchmark


def main() -> None:
    spec = CanonicalBenchmarkSpec(data_source="snapshot", include_external=False)
    run = run_canonical_benchmark(spec)
    print(run.summary())
    print(render_canonical_markdown(run))


if __name__ == "__main__":
    main()
