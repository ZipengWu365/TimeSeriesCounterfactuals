from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from tscfbench.integrations.cards import adapter_catalog


@dataclass(frozen=True)
class InstallMatrixRow:
    adapter_id: str
    display_name: str
    task_family: str
    pip_package: str
    import_name: str
    extra_group: str
    install_command: str
    runtime_cost: str
    interval_support: bool
    placebo_support: bool
    ci_tier: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



def install_matrix() -> List[InstallMatrixRow]:
    rows: List[InstallMatrixRow] = []
    for card in adapter_catalog(include_availability=False):
        pip_packages = list(card.get("pip_packages") or [""])
        import_names = list(card.get("import_names") or [""])
        if not pip_packages:
            pip_packages = [""]
        if not import_names:
            import_names = [""]
        pip_pkg = pip_packages[0] if pip_packages else ""
        import_name = import_names[0] if import_names else ""
        if card["extra_group"] == "core":
            ci_tier = "required"
            note = "Always exercised by the core test suite."
        elif card["task_family"] == "panel":
            ci_tier = "optional-smoke"
            note = "Recommended for canonical panel benchmarks."
        elif card["task_family"] == "impact":
            ci_tier = "optional-smoke"
            note = "Useful for impact-analysis comparisons."
        else:
            ci_tier = "optional-smoke"
            note = "Forecast-as-counterfactual path; usually too heavy for default CI."
        rows.append(
            InstallMatrixRow(
                adapter_id=card["id"],
                display_name=card["display_name"],
                task_family=card["task_family"],
                pip_package=pip_pkg,
                import_name=import_name,
                extra_group=card["extra_group"],
                install_command=card["install_hint"],
                runtime_cost=card["runtime_cost"],
                interval_support=bool(card["interval_support"]),
                placebo_support=bool(card["placebo_support"]),
                ci_tier=ci_tier,
                note=note,
            )
        )
    return rows



def install_matrix_json() -> List[Dict[str, Any]]:
    return [row.to_dict() for row in install_matrix()]



def render_install_matrix_markdown() -> str:
    rows = install_matrix_json()
    headers = ["adapter_id", "task_family", "pip_package", "import_name", "extra_group", "install_command", "ci_tier", "note"]
    lines = ["# Installation matrix", "", "Use this table to decide which optional dependencies belong in your local environment, docs examples, or CI jobs.", ""]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(row[h]).replace("|", "\\|") for h in headers) + " |")
    lines.append("")
    return "\n".join(lines)


__all__ = ["InstallMatrixRow", "install_matrix", "install_matrix_json", "render_install_matrix_markdown"]
