from tscfbench.datasets.synthetic import make_panel_latent_factor
from tscfbench.models.synthetic_control import SimpleSyntheticControl
from tscfbench.protocols import PanelProtocolConfig, benchmark_panel
from tscfbench.report import render_panel_markdown


case = make_panel_latent_factor(T=120, N=12, intervention_t=70, seed=7)
model = SimpleSyntheticControl()
report = benchmark_panel(
    case,
    model,
    config=PanelProtocolConfig(
        run_space_placebo=True,
        run_time_placebo=True,
        placebo_pre_rmspe_factor=5.0,
        min_pre_periods=12,
        max_time_placebos=8,
    ),
)

print(report.metrics)
print(render_panel_markdown(case, report))
