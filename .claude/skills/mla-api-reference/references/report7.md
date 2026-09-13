# /report/7 - Global Cattle Prices

Comparable cattle price series for Australia (NLRS) and the USA (Steiner
Consulting), all converted to AUD c/kg lwt. Short name `global-prices`. Fetcher
`fetchers/fetch_report7.py`. Default output `data/raw/report7_global_cattle_prices.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | `YYYY-MM-DD`; cross-year fine; toDate ≤ yesterday by default |
| `countryID` | **Required, exactly one per request**: `AUS` or `USA` |
| `page` | 100 rows per page |

CLI: `--countries CODE ...` (default both), `--list-countries`. Defaults: `--from`
1 January last year, `--to` yesterday.

## Series in the data

| Country | Indicator | Units | Currency |
|---|---|---|---|
| AUS | National Feeder Steer Indicator | c/kg lwt | AUD |
| AUS | National Heavy Steer Indicator | c/kg lwt | AUD |
| USA | CME Feeder Cattle Index | c/kg lwt | AUD |
| USA | Fed Steer, 5-Day Average | c/kg lwt | AUD |

## CSV columns

`indicator_date, species_id, country_code, indicator_desc, indicator_units, indicator_value, currency_code`

## Sample row

```
indicator_date,species_id,country_code,indicator_desc,indicator_units,indicator_value,currency_code
2026-01-05,Cattle,AUS,National Feeder Steer Indicator,c/kg lwt,449.84810000000000,AUD
```
