# /report/2 - Australian Herd and Flock Figures

Annual ABS livestock estimates by state, one release per financial year. Roughly
2015-16 to 2021-22 have data; other years return zero rows (not an error).
Short name `herd`. Fetcher `fetchers/fetch_report2.py`. Default output
`data/raw/report2_herd_flock.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `year` | Integer; **exactly one per request** |
| `stateID` | **Exactly one per request** |
| `category` | Optional; exactly one per request when used |

No `fromDate`/`toDate`. The fetcher iterates year × state × category. CLI:
`--from-year` (default 2015), `--to-year` (default current year), `--states`,
`--categories`, `--list-states`, `--list-categories`.

## Valid values

States: `NSW`, `SA`, `VIC`, `QLD`, `WA`, `TAS`

Categories:
- `Cattle`
- `Dairy cattle`
- `Meat cattle`
- `Sheep and lambs`
- `Sheep and lambs - Lambs under 1 year`
- `Sheep and lambs - Breeding ewes 1 year or over`
- `Sheep and lambs - Marked lambs under 1 year`

## CSV columns

| Column | Meaning |
|---|---|
| `financial_year` | e.g. `2018-19` |
| `region_desc` | State code |
| `subcategory_desc` | The category (see above) |
| `metric_desc` | Sub-metric, e.g. `Calves less than 1 year`, `Cows in milk and dry`, `Total cattle`, `Total` |
| `estimate_value` | Head count |

## Sample row

```
financial_year,region_desc,subcategory_desc,metric_desc,estimate_value
2018-19,NSW,Dairy cattle,Cows in milk and dry,148550.0000
```
