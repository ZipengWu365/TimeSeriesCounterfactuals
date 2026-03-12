import pandas as pd

from tscfbench import run_panel_data


def main() -> None:
    df = pd.DataFrame(
        {
            "city": ["Harbor City", "Harbor City", "Harbor City", "North City", "North City", "North City", "South City", "South City", "South City"],
            "date": ["2024-03-04", "2024-03-05", "2024-03-06"] * 3,
            "traffic_index": [100.0, 101.5, 88.0, 97.2, 97.9, 98.5, 95.8, 96.1, 96.9],
        }
    )
    result = run_panel_data(
        df,
        unit_col="city",
        time_col="date",
        y_col="traffic_index",
        treated_unit="Harbor City",
        intervention_t="2024-03-06",
        output_dir="python_first_panel_demo",
        plot=False,
    )
    print(result["summary"])


if __name__ == "__main__":
    main()
