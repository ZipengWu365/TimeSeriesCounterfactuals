from __future__ import annotations

from pathlib import Path

import pandas as pd

from tscfbench.agent import export_openai_function_tools
from tscfbench.agent.tokens import estimate_json_tokens
from tscfbench.markdown_utils import dataframe_to_markdown
from tscfbench.onramp import doctor_report, tool_profile_notes


def test_v170_markdown_table_fallback_without_tabulate(monkeypatch) -> None:
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    def boom(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ImportError("tabulate missing")

    monkeypatch.setattr(pd.DataFrame, "to_markdown", boom, raising=True)
    rendered = dataframe_to_markdown(df)
    assert "| a | b |" in rendered
    assert "| 1 | 3 |" in rendered


def test_v170_pyproject_declares_tabulate_dependency() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert '"tabulate>=0.9"' in text


def test_v170_readme_prefers_starter_and_python_module_invocation() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "README.md").read_text(encoding="utf-8")
    assert 'python -m pip install -e ".[starter]"' in text
    assert 'python -m tscfbench quickstart' in text
    assert 'python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib' in text


def test_v170_tool_profile_notes_report_actual_token_estimates() -> None:
    rows = {row["id"]: row for row in tool_profile_notes()}
    assert rows["minimal"]["approx_tokens"] < 3000
    assert rows["research"]["approx_tokens"] < 5000
    assert rows["minimal"]["approx_tokens"] < rows["research"]["approx_tokens"] < rows["full"]["approx_tokens"]


def test_v170_minimal_export_is_significantly_smaller_than_full() -> None:
    minimal = export_openai_function_tools(profile="minimal")
    full = export_openai_function_tools(profile="full")
    assert estimate_json_tokens(minimal).approx_tokens < 3000
    assert estimate_json_tokens(full).approx_tokens > estimate_json_tokens(minimal).approx_tokens


def test_v170_repo_root_is_clean_of_packaging_artifacts() -> None:
    root = Path(__file__).resolve().parents[1]
    assert not (root / "build").exists()
    assert not (root / "dist_build").exists()
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    manifest = (root / "MANIFEST.in").read_text(encoding="utf-8")
    assert ".pytest_cache/" in gitignore
    assert "prune .pytest_cache" in manifest


def test_v170_doctor_still_promotes_single_onboarding_path() -> None:
    rep = doctor_report()
    assert rep["safe_first_run"]["commands"] == [
        'python -m pip install -e ".[starter]"',
        'python -m tscfbench quickstart',
        'python -m tscfbench doctor',
    ]
