from pathlib import Path

from tscfbench import AgentResearchTaskSpec, TokenBudget, build_panel_agent_bundle


spec = AgentResearchTaskSpec(
    dataset="synthetic_latent_factor",
    model="simple_scm",
    seed=7,
    intervention_t=70,
    n_units=12,
    n_periods=120,
    token_budget=TokenBudget(input_limit=5000, reserve_for_output=1000, reserve_for_instructions=800),
)

bundle = build_panel_agent_bundle(spec, output_dir=Path("bundle_dir"))
print(bundle)
