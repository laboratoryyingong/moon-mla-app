# /report/1 - Australian Red Meat Exports

Monthly export volume of Australian beef and veal by destination, from January 2000.
Short name `exports`. Fetcher `fetchers/fetch_report1.py`. Default output
`data/raw/report1_red_meat_exports.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | `YYYY-MM-DD`; any range works, today accepted |
| `page` | 100 rows per page |

No filter parameters. CLI defaults: `--from` 1 January three years ago, `--to` today.

## CSV columns

| Column | Meaning |
|---|---|
| `result_date` | First day of the month (`YYYY-MM-01`) |
| `country_desc` | Destination market |
| `meat_type_group_desc` | Currently always `Beef And Veal` |
| `weight_amt` | Export weight in kilograms |

## Destinations seen in the data

Canada East Coast, Canada West Coast, China, Japan, Malaysia, Philippines,
Saudi Arabia, South Korea, Taiwan, Usa East Coast, Usa West Coast.

## Sample row

```
result_date,country_desc,meat_type_group_desc,weight_amt
2026-01-01,Canada East Coast,Beef And Veal,1760803.4898
```
