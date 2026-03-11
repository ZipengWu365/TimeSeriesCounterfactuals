"""Example: use FRED WTI/Brent data for a commodity event case."""

from tscfbench.datasets import load_fred_series, make_event_impact_case


def main() -> None:
    wti = load_fred_series("DCOILWTICO")
    brent = load_fred_series("DCOILBRENTEU")
    case = make_event_impact_case(
        wti,
        {"brent": brent},
        intervention_t="2025-11-01",
        metadata={"demo": "commodity_event"},
    )
    print(case.df.head())
    print(case.metadata)


if __name__ == "__main__":
    main()
