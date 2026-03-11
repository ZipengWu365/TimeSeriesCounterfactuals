"""Example: turn GitHub stars into an event-impact case."""

from tscfbench.datasets import load_github_star_history, make_event_impact_case


def main() -> None:
    outcome = load_github_star_history("openclaw", "openclaw", max_pages=20)
    peer_a = load_github_star_history("microsoft", "playwright", max_pages=20)
    peer_b = load_github_star_history("langchain-ai", "langchain", max_pages=20)

    case = make_event_impact_case(
        outcome.rename(columns={"stars_new": "value"})[["date", "value"]],
        {
            "playwright": peer_a.rename(columns={"stars_new": "value"})[["date", "value"]],
            "langchain": peer_b.rename(columns={"stars_new": "value"})[["date", "value"]],
        },
        intervention_t="2026-02-20",
        metadata={"demo": "github_stars"},
    )
    print(case.df.head())
    print(case.metadata)


if __name__ == "__main__":
    main()
