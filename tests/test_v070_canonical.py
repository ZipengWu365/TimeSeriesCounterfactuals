from __future__ import annotations

from pathlib import Path

from tscfbench.canonical import CanonicalBenchmarkSpec, list_canonical_studies, render_canonical_markdown, run_canonical_benchmark
from tscfbench.datasets import load_named_dataset


def test_snapshot_dataset_loader_marks_snapshot_source() -> None:
    case = load_named_dataset("german_reunification", source="snapshot")
    assert case.metadata["data_source"] == "snapshot"
    assert case.metadata["snapshot_kind"] == "ci_fixture"


def test_canonical_benchmark_runs_on_snapshots() -> None:
    spec = CanonicalBenchmarkSpec(data_source="snapshot", include_external=False)
    run = run_canonical_benchmark(spec)
    summary = run.summary()
    assert summary["cells"] >= 3
    assert summary["ok"] >= 3
    md = render_canonical_markdown(run)
    assert "German reunification" in md
    assert "California Proposition 99" in md
    assert "Basque Country terrorism" in md


def test_canonical_registry_contains_expected_ids() -> None:
    ids = [study.id for study in list_canonical_studies()]
    assert ids == ["germany", "prop99", "basque"]
