# Public data sources for high-attention case studies

These sources are useful when you want a demo or benchmark case that feels timely, public-facing, and easy to explain.

## GitHub stargazer history

**Series type:** daily attention / adoption

**Loader:** load_github_star_history

**What you get**

- daily new stars
- daily cumulative stars
- repo metadata in frame attrs

**Good for**

- repo virality
- open-source launch studies
- attention spillover around announcements

**Notes**

- Uses the public GitHub stargazers endpoint with timestamp-aware media type.
- Great for high-attention open-source case studies such as OpenClaw-like repo surges.

## GH Archive watch-event history

**Series type:** hourly or daily GitHub attention

**Loader:** GH Archive / external preprocessing

**What you get**

- public GitHub event stream
- watch events at scale
- cross-repo comparison candidates

**Good for**

- ecosystem-level star studies
- fake-star filtering research
- broad repo panels

**Notes**

- Useful when the native GitHub API is too rate-limited or when you want many repos at once.

## CoinGecko market chart

**Series type:** crypto price / market cap / volume

**Loader:** load_coingecko_market_chart

**What you get**

- historical prices
- market caps
- 24h volume

**Good for**

- crypto event studies
- listing news
- policy or ETF windows
- attention/price co-movement

**Notes**

- Daily data is a natural fit for event windows and quasi-experimental impact analysis.

## FRED commodity series

**Series type:** macro and commodity daily levels

**Loader:** load_fred_series

**What you get**

- date/value pairs
- named public series such as WTI and Brent

**Good for**

- oil shock studies
- macro controls
- commodity event windows

**Notes**

- WTI and Brent are especially useful because they naturally form treated/control pairs or spread-style controls.

## LBMA gold via DBnomics-compatible CSV

**Series type:** daily gold price levels

**Loader:** load_csv_like_price_series

**What you get**

- daily gold prices
- multi-currency series when available

**Good for**

- gold shock studies
- safe-haven behavior
- attention versus commodity price comparisons

**Notes**

- For tutorials, a CSV download or mirrored source is often the simplest path.
