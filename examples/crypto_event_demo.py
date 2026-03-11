"""Example: use CoinGecko market-chart data for an event-style impact case."""

from tscfbench.datasets import load_coingecko_market_chart, make_event_impact_case, to_log_returns


def main() -> None:
    btc = load_coingecko_market_chart("bitcoin")
    eth = load_coingecko_market_chart("ethereum")
    sol = load_coingecko_market_chart("solana")

    btc_r = to_log_returns(btc, value_col="price", out_col="value")[["date", "value"]].dropna()
    eth_r = to_log_returns(eth, value_col="price", out_col="value")[["date", "value"]].dropna()
    sol_r = to_log_returns(sol, value_col="price", out_col="value")[["date", "value"]].dropna()

    case = make_event_impact_case(
        btc_r,
        {"eth": eth_r, "sol": sol_r},
        intervention_t="2024-01-11",
        metadata={"demo": "crypto_event"},
    )
    print(case.df.head())
    print(case.metadata)


if __name__ == "__main__":
    main()
