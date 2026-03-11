from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List

from tscfbench.canonical import CanonicalBenchmarkSpec, render_canonical_markdown, run_canonical_benchmark
from tscfbench.experiments import PanelExperimentSpec, materialize_panel_case, run_panel_experiment
from tscfbench.install_matrix import install_matrix_json
from tscfbench.integrations.cards import adapter_catalog
from tscfbench.visuals import write_panel_visual_bundle


def _viz_available() -> bool:
    return importlib.util.find_spec("matplotlib") is not None


def essential_commands() -> List[Dict[str, Any]]:
    source_install = 'python -m pip install -e ".[starter]"'
    return [
        {"id": "first_minute", "title": "First 60 seconds", "why": "Use this copy-paste path when you want the most reliable first result across Linux, macOS, and Windows.", "commands": [source_install, "python -m tscfbench quickstart", "python -m tscfbench doctor"]},
        {"id": "public_demos", "title": "Public demos people understand fast", "why": "Use these when you want a chart-first story before you think about protocols, placebos, or adapters.", "commands": ["python -m tscfbench demo repo-breakout", "python -m tscfbench demo climate-grid", "python -m tscfbench demo hospital-surge", "python -m tscfbench demo detector-downtime", "python -m tscfbench demo minimum-wage-employment", "python -m tscfbench demo viral-attention"]},
        {"id": "share_package", "title": "Make something you can actually post", "why": "Use this when you want a chart, share card, short summary, and citation block that can be posted or sent to a colleague.", "commands": ["python -m tscfbench make-share-package --demo-id repo-breakout", "python -m tscfbench make-share-package --demo-id detector-downtime"]},
        {"id": "narrow_agents", "title": "Narrow agent path", "why": "Use this when you want the smallest tool surface and a bounded artifact bundle before moving to broader profiles.", "commands": ["python -m tscfbench export-openai-tools --profile starter -o openai_tools_starter.json", "python -m tscfbench make-agent-spec -o agent_spec.json", "python -m tscfbench build-agent-bundle agent_spec.json -o bundle_dir"]},
    ]


def render_essential_commands_markdown() -> str:
    lines: List[str] = ["# Essential commands", "", "This page is intentionally narrow. It shows the small command set most users need before the wider research and agent surfaces.", ""]
    for section in essential_commands():
        lines.append(f"## {section['title']}")
        lines.append("")
        lines.append(section["why"])
        lines.append("")
        lines.append("```bash")
        lines.extend(section["commands"])
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def tool_profile_notes() -> List[Dict[str, Any]]:
    from tscfbench.agent.tools import export_openai_function_tools, list_tool_profiles
    from tscfbench.agent.tokens import estimate_json_tokens
    rows: List[Dict[str, Any]] = []
    for row in list_tool_profiles():
        exported = export_openai_function_tools(profile=row["id"])
        estimate = estimate_json_tokens(exported).to_dict()
        rows.append({**row, "approx_tokens": estimate["approx_tokens"], "chars": estimate["chars"]})
    return rows


def render_tool_profiles_markdown() -> str:
    profiles = tool_profile_notes()
    lines: List[str] = ["# Tool profiles", "", "Do not start by dumping the whole tool catalog into context.", "", "Use `starter` for onboarding and the first successful run. Promote to `minimal` or `research` only when you need canonical studies, agent bundles, or bounded artifact reads. Keep `full` for MCP servers, docs generation, or deep automation.", ""]
    for profile in profiles:
        lines.append(f"## {profile['id']}")
        lines.append("")
        lines.append(profile["summary"])
        lines.append("")
        lines.append(f"- tool_count: {profile['tool_count']}")
        lines.append(f"- approx_tokens: {profile.get('approx_tokens', 'n/a')}")
        lines.append(f"- recommended_for: {profile['recommended_for']}")
        if profile.get("aliases"):
            lines.append(f"- aliases: {', '.join(profile['aliases'])}")
        lines.append("")
        lines.append("Included tools:")
        lines.append("")
        lines.extend(f"- `{name}`" for name in profile["tool_names"])
        lines.append("")
    return "\n".join(lines)


def doctor_report() -> Dict[str, Any]:
    adapters = adapter_catalog(include_availability=True)
    builtins = [row for row in adapters if row["extra_group"] == "core"]
    optional_rows = [row for row in adapters if row["extra_group"] != "core"]
    available_optional = [row for row in optional_rows if row.get("available")]
    missing_optional = [row for row in optional_rows if not row.get("available")]
    installs: Dict[str, List[str]] = {}
    for row in install_matrix_json():
        installs.setdefault(row["extra_group"], [])
        installs[row["extra_group"]].append(row["install_command"])
    deduped_installs = {key: sorted(set(values)) for key, values in installs.items()}
    viz_ready = _viz_available()
    return {
        "package": "tscfbench",
        "core_ready": all(row.get("available", True) for row in builtins),
        "viz_ready": viz_ready,
        "built_in_backends": [row["id"] for row in builtins],
        "optional_available": [row["id"] for row in available_optional],
        "optional_missing": [row["id"] for row in missing_optional],
        "safe_first_run": {"guarantee": "The built-in quickstart path avoids optional dependencies and is designed to run cleanly before you install specialist backends.", "commands": ['python -m pip install -e ".[starter]"', 'python -m tscfbench quickstart', 'python -m tscfbench doctor']},
        "recommended_installs": {"starter": ['python -m pip install -e ".[starter]"'], "minimal": ['python -m pip install -e .'], "panel": [cmd for cmd in deduped_installs.get("research", []) if "pysyncon" in cmd or "SyntheticControlMethods" in cmd or "scpi_pkg" in cmd], "impact": [cmd for cmd in deduped_installs.get("research", []) if "tfp-causalimpact" in cmd or "cimpact" in cmd or "CausalPy" in cmd], "forecast": deduped_installs.get("forecast", []), "release_asset": ['python -m pip install tscfbench-1.8.0-py3-none-any.whl matplotlib'], "pypi_ready_after_publish": ['python -m pip install tscfbench[starter]']},
        "notes": [
            "Recommended first run: install the starter extra so PNG chart assets are guaranteed without adding the full research stack.",
            "Quickstart and report generation do not depend on undeclared markdown-table backends; the core package closes that path in clean environments.",
            "Minimal installs still work. If matplotlib is unavailable, tscfbench falls back to SVG visuals for quickstart and demos.",
            "Optional backends are for deeper comparison runs, not for the first-run experience.",
            "If you explicitly include optional backends and they are not installed, tscfbench should mark them as skipped optional dependencies rather than hard benchmark failures.",
            "For OpenAI tool calling, export the starter tool profile first, then promote to minimal or research only after the narrow path succeeds.",
            "If the `tscfbench` executable is not on PATH, `python -m tscfbench ...` should still work.",
            "The package metadata is PyPI-ready, but this repo snapshot cannot publish externally from the current environment.",
        ],
    }


def render_doctor_markdown() -> str:
    rep = doctor_report()
    lines: List[str] = ["# Environment doctor", "", "This report is meant to reduce confusion on first run.", "", f"- core_ready: {rep['core_ready']}", f"- viz_ready: {rep['viz_ready']}", f"- built_in_backends: {', '.join(rep['built_in_backends'])}", f"- optional_available: {', '.join(rep['optional_available']) if rep['optional_available'] else '(none)'}", f"- optional_missing: {', '.join(rep['optional_missing']) if rep['optional_missing'] else '(none)'}", "", "## Safe first run", "", rep['safe_first_run']['guarantee'], "", "```bash", *rep['safe_first_run']['commands'], "```", "", "## Notes", "", *[f"- {note}" for note in rep['notes']], ""]
    return "\n".join(lines)


def run_quickstart(output_dir: str | Path = "tscfbench_quickstart", *, data_source: str = "snapshot", include_external: bool = False, seed: int = 7, plot: bool = True) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    spec = CanonicalBenchmarkSpec(schema_version="1.8.0", name="canonical_quickstart", include_external=bool(include_external), data_source=data_source, seed=seed, stop_on_error=False)
    spec_path = out / 'canonical_quickstart.json'
    spec.to_json(spec_path)
    run = run_canonical_benchmark(spec)
    results_payload = {'summary': run.summary(), 'results': run.to_frame().to_dict(orient='records')}
    results_path = out / 'canonical_quickstart_results.json'
    report_path = out / 'canonical_quickstart_report.md'
    summary_path = out / 'summary.json'
    results_path.write_text(json.dumps(results_payload, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    report_path.write_text(render_canonical_markdown(run), encoding='utf-8')
    generated_files: List[str] = [str(spec_path), str(results_path), str(report_path)]
    visual_assets: Dict[str, str] = {}
    if plot:
        panel_spec = PanelExperimentSpec(dataset='german_reunification', model='simple_scm', seed=seed, intervention_t=1990, data_source=data_source, min_pre_periods=12, max_time_placebos=8)
        try:
            case = materialize_panel_case(panel_spec)
            panel_report = run_panel_experiment(panel_spec)
            visual_assets = write_panel_visual_bundle(case, panel_report, output_dir=out, stem='quickstart_germany', title='Germany reunification', ylabel=case.y_col, takeaway='One command turns a before/after question into a counterfactual chart, a report, and a share package you can actually post online.')
            generated_files.extend(visual_assets.values())
        except Exception:
            visual_assets = {}
    summary_payload = {'kind': 'quickstart_summary', 'summary': run.summary(), 'visual_assets': visual_assets, 'generated_files_count': len(generated_files), 'next_command': 'python -m tscfbench doctor'}
    summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    generated_files.append(str(summary_path))
    generated_files_path = out / 'generated_files.json'
    generated_payload = {'generated_files': generated_files, 'visual_assets': visual_assets, 'plotting_mode': 'png+svg' if _viz_available() else ('svg_fallback' if plot else 'none')}
    generated_files_path.write_text(json.dumps(generated_payload, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    generated_files.append(str(generated_files_path))
    next_command = 'python -m tscfbench doctor'
    next_steps = [next_command, 'python -m tscfbench demo climate-grid', 'python -m tscfbench demo hospital-surge', 'python -m tscfbench demo repo-breakout', 'python -m tscfbench demo detector-downtime', 'python -m tscfbench demo minimum-wage-employment', 'python -m tscfbench demo viral-attention', 'python -m tscfbench make-share-package --demo-id repo-breakout', 'python -m tscfbench export-openai-tools --profile starter -o openai_tools_starter.json']
    next_path = out / 'NEXT_STEPS.md'
    next_path.write_text("\n".join(['# Next steps', '', 'You have completed the narrow, built-in first run. From here, expand only as needed.', '', '```bash', *next_steps, '```', '']), encoding='utf-8')
    generated_files.append(str(next_path))
    return {'kind': 'quickstart_run', 'output_dir': str(out), 'spec_path': str(spec_path), 'results_path': str(results_path), 'report_path': str(report_path), 'summary_path': str(summary_path), 'generated_files_path': str(generated_files_path), 'next_steps_path': str(next_path), 'summary': run.summary(), 'generated_files': generated_files, 'next_command': next_command, 'visual_assets': visual_assets}


def feedback_response_items() -> List[Dict[str, Any]]:
    return [
        {'issue': 'The package needed a clearer answer to why it exists above estimator packages.', 'change': 'v1.8 keeps the strong headline and pushes a clearer workflow-vs-estimator decision story into the README, docs home, and showcase materials.'},
        {'issue': 'The repo needed stronger cross-disciplinary demos, especially beyond product and policy language.', 'change': 'v1.8 adds detector-downtime (physics), minimum-wage-employment (economics), and viral-attention (social science / public attention) as new flagship demos.'},
        {'issue': 'The narrow agent path was good, but it could still start narrower.', 'change': 'v1.8 adds a starter tool profile and keeps `python -m tscfbench ...` as the default command style across docs and examples.'},
        {'issue': 'The repo still lacked a lighter try-now surface and richer walkthrough notebooks.', 'change': 'v1.8 adds a hosted-gallery-ready docs page, a Colab-style quickstart notebook, and richer executed walkthrough notebooks with checked outputs.'},
    ]


def render_feedback_response_markdown() -> str:
    lines: List[str] = ['# Feedback-driven changes in v1.8', '', 'This release focuses on distribution readiness, cross-disciplinary demos, a narrower agent onboarding path, and richer teaching assets.', '']
    for item in feedback_response_items():
        lines.append(f"## {item['issue']}")
        lines.append('')
        lines.append(item['change'])
        lines.append('')
    return "\n".join(lines)

__all__ = ['doctor_report', 'essential_commands', 'feedback_response_items', 'render_doctor_markdown', 'render_essential_commands_markdown', 'render_feedback_response_markdown', 'render_tool_profiles_markdown', 'run_quickstart', 'tool_profile_notes']
