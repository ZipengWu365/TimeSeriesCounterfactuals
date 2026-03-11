# High-traffic public cases

These cases are chosen because they are both methodologically usable and public-facing enough to attract attention when you show the package.

## OpenClaw GitHub stars around major ecosystem events

**Theme:** attention / open-source virality

**Why it has attention:** A fast-growing AI-agent repository with security news, ecosystem integrations, and large public visibility is exactly the kind of case that draws clicks, discussion, and reproducible benchmarking interest.

**Counterfactual question:** How much additional GitHub-star growth arrived after a specific event window relative to a counterfactual built from peer repos or pre-trend dynamics?

**Treated series:** Daily new or cumulative stars for openclaw/openclaw.

**Candidate controls**

- Peer agent repos with similar audiences but no event on the same day.
- A synthetic control built from multiple comparable repos.
- Search-interest proxies or broader GitHub AI-agent category activity when available.

**Recommended workflow:** Use the GitHub star-history loader, aggregate to daily counts, then run an impact-style or panel-style event study around launches, integrations, or security incidents.

**Best environment:** notebook + CLI report

**Data sources:** github_stars_api, gharchive_watch_events

**Notes**

- This is one of the most naturally viral demo cases because the outcome variable is public attention itself.
- Be careful about fake-star contamination if you study broad repo panels rather than one well-known repo.

## Predict or explain GitHub repo breakout trajectories

**Theme:** attention / platform dynamics

**Why it has attention:** People love seeing which repos broke out, when they broke out, and whether a launch or endorsement actually changed the slope.

**Counterfactual question:** What would star growth have looked like without the launch event, ranking spike, or major influencer amplification?

**Treated series:** Daily stars for one focal repo.

**Candidate controls**

- Repos in the same topic/language band.
- Repos launched in the same quarter but without the focal event.
- A donor pool built from several non-treated peers.

**Recommended workflow:** Build a repo panel from GitHub stars or GH Archive watch events, then use synthetic control or DiD-style comparisons around announcement dates.

**Best environment:** CLI + shared server

**Data sources:** github_stars_api, gharchive_watch_events

**Notes**

- This is a strong fit if you want media-friendly charts and a benchmark that travels well on social media.

## Crypto price and volume around major events

**Theme:** markets / public attention

**Why it has attention:** Crypto already has a built-in audience, and event windows translate naturally into counterfactual questions.

**Counterfactual question:** How would price, volume, or market cap have evolved without the event window?

**Treated series:** Daily price or log-return series for a focal coin such as BTC or ETH.

**Candidate controls**

- Peer assets in the same category.
- Market-wide crypto index proxies.
- Volume or dominance controls depending on the event type.

**Recommended workflow:** Fetch CoinGecko market-chart data, transform prices into returns when appropriate, and run an event-style ImpactCase with peer controls.

**Best environment:** notebook + markdown report

**Data sources:** coingecko_market_chart

**Notes**

- For methodological credibility, returns or spreads are often better outcomes than raw price levels.
- This case is useful both for research and for attracting broader user attention to the package.

## Gold, WTI, and Brent around macro or geopolitical shocks

**Theme:** commodities / macro events

**Why it has attention:** Commodity events are easy to explain to a broad audience and already have a large data and media ecosystem.

**Counterfactual question:** How far did gold or oil deviate from a control-based counterfactual around the shock window?

**Treated series:** Daily gold, WTI, or Brent price series.

**Candidate controls**

- Use Brent as a control for WTI, or vice versa.
- Use gold together with dollar or oil controls depending on the shock.
- Use broader macro controls when you want a richer counterfactual model.

**Recommended workflow:** Load commodity series from FRED or CSV mirrors, align series on date, and build event windows around the macro shock of interest.

**Best environment:** notebook, teaching, public write-up

**Data sources:** fred_series, lbma_gold

**Notes**

- This is a strong demonstration case when you want the package to feel relevant beyond the GitHub/AI crowd.
