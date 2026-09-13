# /report/4 - Saleyard Yardings

Daily NLRS head counts yarded at physical saleyards, by category and sale type.
Short name `yardings`. Fetcher `fetchers/fetch_report4.py`. Default output
`data/raw/report4_saleyard_yardings.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | `YYYY-MM-DD`; cross-year fine; **toDate must be yesterday or earlier** (today returns HTTP 500) |
| `category` | **Required, exactly one per request** |
| `saleyardID` | Optional three-letter code |
| `page` | 100 rows per page |

CLI: `--categories` (default all three), `--saleyard ID`, `--list-categories`.
Defaults: `--from` 1 January last year, `--to` yesterday.

## Valid values

Categories: `Cattle`, `Lamb`, `Sheep` (note singular `Lamb`).

Saleyard codes (state): ADP SA, ARM NSW, BAL VIC, BAR VIC, BEN VIC, BLA QLD, CAS NSW,
CHT QLD, COR NSW, COW NSW, CTL NSW, DAL QLD, DEN NSW, DUB NSW, ECH VIC, ENO VIC,
FOR NSW, GME QLD, GRI NSW, GUN NSW, HAM VIC, HIN VIC, HOR VIC, INV NSW, KAT WA,
LEO VIC, MCO SA, MOS NSW, MOU SA, MTB WA, MTL VIC, MUC WA, NAR SA, NTS TAS, ONB VIC,
POW TAS, ROM QLD, SCO NSW, SHE VIC, SIN NSW, TAM NSW, WAG NSW, WAR QLD, WOD VIC, YAS NSW.

## CSV columns

| Column | Meaning |
|---|---|
| `result_date` | Sale date |
| `category_desc` | Cattle / Lamb / Sheep |
| `state_id` | NSW, VIC, QLD, SA, WA, TAS |
| `saleyard_id` | Three-letter saleyard code |
| `tranx_type_id` | `Prime` (slaughter sale) or `Store` (restocker sale) |
| `head_count` | Head yarded |

## Sample row

```
result_date,category_desc,state_id,saleyard_id,tranx_type_id,head_count
2025-05-20,Cattle,VIC,SHE,Prime,2400.0
```
