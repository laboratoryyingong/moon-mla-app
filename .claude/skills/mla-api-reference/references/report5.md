# /report/5 - NLRS Livestock Indicators (national)

Daily national price indicators for cattle, lambs and sheep. Short name
`indicators`. Fetcher `fetchers/fetch_report5.py`. Default output
`data/raw/report5_livestock_indicators.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | `YYYY-MM-DD`; **must not cross a calendar year** (HTTP 500) - the fetcher splits per year; **toDate ≤ yesterday** |
| `indicatorID` | **Required, exactly one per request** (1-18) |
| `page` | 100 rows per page |

CLI: `--indicators ID ...` (default all 18), `--list-indicators`. Defaults:
`--from` 1 January last year, `--to` yesterday.

## The 18 indicators

| ID | Species | Indicator | Units |
|---|---|---|---|
| 1 | Cattle | Western Young Cattle Indicator | c/kg cwt |
| 2 | Cattle | National Restocker Yearling Steer Indicator | c/kg lwt |
| 3 | Cattle | National Feeder Steer Indicator | c/kg lwt |
| 4 | Cattle | National Heavy Steer Indicator | c/kg lwt |
| 5 | Cattle | National Heavy Dairy Cow Indicator | c/kg lwt |
| 6 | Sheep | National Light Lamb Indicator | c/kg cwt |
| 7 | Sheep | National Trade Lamb Indicator | c/kg cwt |
| 8 | Sheep | National Heavy Lamb Indicator | c/kg cwt |
| 9 | Sheep | National Merino Lamb Indicator | c/kg cwt |
| 10 | Sheep | National Restocker Lamb Indicator | c/kg cwt |
| 11 | Sheep | National Mutton Indicator | c/kg cwt |
| 12 | Cattle | National Restocker Yearling Heifer Indicator | c/kg lwt |
| 13 | Cattle | National Processor Cow Indicator | c/kg lwt |
| 14 | Cattle | National Young Cattle Indicator | c/kg lwt |
| 15 | Cattle | Online Young Cattle Indicator | c/kg lwt |
| 16 | Sheep | Online Lamb Indicator | $/head |
| 17 | Cattle | National Feeder Heifer Indicator | c/kg lwt |
| 18 | Sheep | Online Sheep Indicator | $/head |

The API labels IDs 6-11, 16 and 18 with `species_id = Sheep`; the merge script
regroups 6-10 and 16 as **Lambs** and 11 and 18 as **Sheep** (mutton).

## CSV columns

| Column | Meaning |
|---|---|
| `calendar_date` | Day |
| `species_id` | Cattle / Sheep |
| `indicator_id` | 1-18 |
| `indicator_desc` | Name from the table above |
| `indicator_units` | c/kg cwt, c/kg lwt or $/head |
| `head_count` | Number of head in the sample behind the price |
| `indicator_value` | The price |

## Sample row

```
calendar_date,species_id,indicator_id,indicator_desc,indicator_units,head_count,indicator_value
2025-04-01,Cattle,1,Western Young Cattle Indicator,c/kg cwt,920.0,595.6209516304
```
