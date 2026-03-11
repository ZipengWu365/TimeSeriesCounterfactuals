from __future__ import annotations

from pathlib import Path

from tscfbench.agent import export_openai_function_tools
from tscfbench.agent.tokens import estimate_json_tokens
from tscfbench.cli import build_parser
from tscfbench.demo_cases import demo_data_path, render_demo_gallery_markdown, run_demo
from tscfbench.csv_runner import run_csv_impact, run_csv_panel
from tscfbench.onramp import run_quickstart


def test_v140_cli_surface_includes_demo_and_csv_commands() -> None:
    parser = build_parser()
    subparsers_action = next(a for a in parser._actions if getattr(a, 'dest', None) == 'cmd')
    names = set(subparsers_action.choices)
    assert 'demo' in names
    assert 'demo-gallery' in names
    assert 'run-csv-panel' in names
    assert 'run-csv-impact' in names



def test_v140_quickstart_writes_visual_assets(tmp_path: Path) -> None:
    payload = run_quickstart(tmp_path / 'quickstart', plot=True)
    assert payload['summary']['errors'] == 0
    assert payload['next_command'] == 'python -m tscfbench doctor'
    assert payload['visual_assets']
    assert Path(payload['visual_assets']['treated_vs_counterfactual_png']).exists()
    assert Path(payload['visual_assets']['share_card_png']).exists()



def test_v140_demo_city_traffic_writes_share_card(tmp_path: Path) -> None:
    payload = run_demo('city-traffic', output_dir=tmp_path, plot=True)
    assert payload['kind'] == 'csv_panel_run'
    assert Path(payload['generated_files']['share_card_png']).exists()
    assert Path(payload['generated_files']['report_md']).exists()



def test_v140_csv_runners_accept_datetime_interventions(tmp_path: Path) -> None:
    panel_payload = run_csv_panel(
        demo_data_path('city-traffic'),
        unit_col='city',
        time_col='date',
        y_col='traffic_index',
        treated_unit='Harbor City',
        intervention_t='2024-03-06',
        output_dir=tmp_path / 'panel_demo',
    )
    impact_payload = run_csv_impact(
        demo_data_path('heatwave-health'),
        time_col='date',
        y_col='er_visits',
        x_cols=['nearby_city_er', 'temperature_proxy'],
        intervention_t='2024-07-14',
        output_dir=tmp_path / 'impact_demo',
    )
    assert '2024-03-06' in panel_payload['summary']['intervention_t']
    assert '2024-07-14' in impact_payload['summary']['intervention_t']



def test_v140_demo_gallery_is_visual_and_plain_language() -> None:
    gallery = render_demo_gallery_markdown()
    assert 'social-share card' in gallery
    assert 'python -m tscfbench demo city-traffic' in gallery
    assert '![City traffic intervention]' in gallery



def test_v140_tool_profiles_are_narrower() -> None:
    minimal = export_openai_function_tools(profile='minimal')
    research = export_openai_function_tools(profile='research')
    full = export_openai_function_tools(profile='full')
    minimal_est = estimate_json_tokens(minimal)
    research_est = estimate_json_tokens(research)
    full_est = estimate_json_tokens(full)
    assert minimal_est.approx_tokens < 3000
    assert research_est.approx_tokens < 5000
    assert minimal_est.approx_tokens < research_est.approx_tokens < full_est.approx_tokens
