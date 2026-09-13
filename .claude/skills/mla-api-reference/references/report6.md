# /report/6 - NLRS Livestock Indicators by Saleyard

The same 18 indicators as report 5, broken down per saleyard. By far the largest
dataset (hundreds of thousands of rows per year); always narrow with
`--indicators` and/or `--saleyard`. Short name `saleyard-indicators`. Fetcher
`fetchers/fetch_report6.py`. Default output `data/raw/report6_saleyard_indicators.csv`.

## Query parameters

| Param | Notes |
|---|---|
| `fromDate`, `toDate` | Must not cross a calendar year (fetcher splits); toDate ≤ yesterday |
| `indicatorID` | **Required, exactly one per request** (1-18, same table as [report5.md](report5.md)) |
| `saleyardID` | Optional three-letter code |
| `page` | 100 rows per page |

CLI: `--indicators ID ...`, `--saleyard ID`, `--list-indicators`. Defaults:
`--from` 1 January last year, `--to` yesterday.

## Saleyard codes seen in the data

ADP, ARM, BAL, BAR, BEN, BLA, CAS, CHT, COR, COW, CTL, DAL, DEN, DUB, ECH, FOR, GME,
GRI, GUN, HAM, HOR, INV, KAT, LEO, MCO, MOS, MOU, MTB, MTL, MUC, NAR, POW, ROM, SCO,
SHE, SIN, TAM, WAG, WAR, WOD. State for each code is listed in [report4.md](report4.md).

## CSV columns

Same as report 5 plus `saleyard_id` after `species_id`:
`calendar_date, species_id, saleyard_id, indicator_id, indicator_desc, indicator_units, head_count, indicator_value`.

## Sample row

```
calendar_date,species_id,saleyard_id,indicator_id,indicator_desc,indicator_units,head_count,indicator_value
2026-01-05,Cattle,MUC,1,Western Young Cattle Indicator,c/kg cwt,377.0,740.5103
```
