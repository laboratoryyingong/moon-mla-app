# /report/10 - NLRS Slaughter

Weekly slaughter head counts reported to NLRS by processors, by contributing state
and species. Published for the week ending Friday. Short name `nlrs-slaughter`.
Fetcher `fetchers/fetch_report10.py` (also imported by `app.py`). Default output
`data/raw/report10_nlrs_slaughter.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | **Must not cross a calendar year** (fetcher splits per year); **toDate ≤ yesterday** (today returns HTTP 500; the fetcher clamps) |
| `species` | Optional; **one per request**. Omit to get all species in one stream |
| `page` | 100 rows per page |

CLI: `--species NAME ...`, `--list-species`. Defaults: `--from` 1 January last
year, `--to` yesterday.

## Valid species

`Cattle`, `Calves`, `Sheep`, `Lambs`, `Pigs`, `Goat`, `Deer`

## CSV columns

| Column | Meaning |
|---|---|
| `result_date` | Week-ending Friday |
| `contributor_state_id` | NSW, VIC, QLD, SA, WA, TAS |
| `species_id` | One of the species above |
| `slaughter_count` | Head slaughtered that week; zero rows are real (e.g. Deer) |

## Sample row

```
result_date,contributor_state_id,species_id,slaughter_count
2025-01-03,QLD,Cattle,73128
```
