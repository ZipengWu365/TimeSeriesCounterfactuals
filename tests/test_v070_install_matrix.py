from __future__ import annotations

from pathlib import Path

from tscfbench.install_matrix import install_matrix, render_install_matrix_markdown


def test_install_matrix_contains_expected_packages() -> None:
    rows = install_matrix()
    ids = {row.adapter_id for row in rows}
    assert {"pysyncon", "scpi", "tfp_causalimpact", "statsforecast_cf"}.issubset(ids)


def test_install_matrix_markdown_has_table() -> None:
    md = render_install_matrix_markdown()
    assert md.startswith("# Installation matrix")
    assert "| adapter_id | task_family |" in md
