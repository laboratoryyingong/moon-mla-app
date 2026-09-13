# /report/8 - US Domestic Cattle Prices

Weekly US cattle and cow prices from Steiner Consulting, in US cents per pound.
Short name `us-prices`. Fetcher `fetchers/fetch_report8.py`. Default output
`data/raw/report8_us_cattle_prices.csv`.

## Query parameters

`fromDate`, `toDate` (`YYYY-MM-DD`, today accepted, cross-year fine) and `page`.
No filters; every series comes back together. Defaults: `--from` 1 January last
year, `--to` today.

## Series in the data

| Indicator | Units |
|---|---|
| CME Feeder Cattle Index | US c/lb lwt |
| Fed Steer, 5-Day Average | US c/lb lwt |
| Bonner Cows, 85% lean | US c/lb cwt |
| Breaker Cows, Carcass Price, 75% lean | US c/lb cwt |
| Cutter Cow, Carcass Price, 90% Lean | US c/lb cwt |
| Cutter Cow Carcass Cutout | US c/lb cwt |

## CSV columns

`indicator_name, indicator_date, indicator_units, indicator_value`

## Sample row

```
indicator_name,indicator_date,indicator_units,indicator_value
CME Feeder Cattle Index,2026-01-01,US c/lb lwt,350.22
```
Names containing commas are quoted in the CSV, e.g. `"Bonner Cows, 85% lean"`.
