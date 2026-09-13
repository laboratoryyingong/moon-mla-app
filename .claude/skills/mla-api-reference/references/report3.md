# /report/3 - Australian Slaughter and Production (ABS)

Quarterly ABS slaughter and production figures by animal category and state, from
March 2000. Short name `slaughter`. Fetcher `fetchers/fetch_report3.py`. Default
output `data/raw/report3_slaughter_production.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | `YYYY-MM-DD`; cross-year ranges fine, today accepted |
| `category` | Optional; one per request. Omit to get every category in one stream |
| `page` | 100 rows per page |

CLI: `--categories NAME ...`, `--list-categories`. Defaults: `--from` 1 January
last year, `--to` today.

## Valid categories

`Total Red Meat`, `Calves`, `Cattle (Excl. Calves)`, `Cows And Heifers`,
`Bulls, Bullocks And Steers`, `Sheep`, `Lambs`, `Chickens`, `Pigs`

## CSV columns

| Column | Meaning |
|---|---|
| `report_date` | Quarter start month (`YYYY-MM-01`: 03, 06, 09, 12) |
| `report_type` | `Slaughter` or `Production` |
| `category` | Animal category |
| `location_id` | State name in full, or `Australia` for the national total |
| `unit_of_measure` | `000` (thousand head) for Slaughter rows, `Tonnes` for Production rows |
| `value_amt` | The figure |

Locations: Australia, New South Wales, Victoria, Queensland, South Australia,
Western Australia, Tasmania, Northern Territory, Australian Capital Territory.

## Sample rows

```
report_date,report_type,category,location_id,unit_of_measure,value_amt
2025-06-01,Slaughter,Sheep,New South Wales,000,931.0000
2025-06-01,Production,Sheep,New South Wales,Tonnes,24426.0000
```
