import pandas as pd

from tscfbench import PanelCase, PanelProtocolConfig, benchmark_panel
from tscfbench.models.synthetic_control import SimpleSyntheticControl


def main() -> None:
    df = pd.DataFrame(
        {
            "unit": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C"],
            "year": [1, 2, 3, 4] * 3,
            "outcome": [10, 11, 18, 20, 9, 10, 11, 12, 8, 9, 10, 11],
        }
    )
    case = PanelCase(df=df, unit_col="unit", time_col="year", y_col="outcome", treated_unit="A", intervention_t=3)
    report = benchmark_panel(case, SimpleSyntheticControl(), config=PanelProtocolConfig(run_space_placebo=True, run_time_placebo=False))
    print(report.metrics)


if __name__ == "__main__":
    main()
