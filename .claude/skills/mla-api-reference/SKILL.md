---
name: mla-api-reference
description: Authoritative reference for the MLA Statistics API as used in this repo - which of the ten reports holds which data, endpoint parameters, one-filter-per-request rules, year-split and yesterday-cutoff quirks, CSV columns and valid filter values. Use whenever someone asks what MLA data exists, which endpoint or report to use, what a column or unit means, or which species / category / indicator / state / saleyard values are valid.
---

# MLA Statistics API reference

Base URL `https://api-mlastatistics.mla.com.au`, endpoints `/report/1` … `/report/10`.
No authentication. Every request sends `Accept: application/json` and a User-Agent
of the form `MLA-Data-Fetcher/1.0 (... contact: <email>)`.

**Response shape**: `{"data": [row, ...], "total number rows": N}` with 100 rows per
page (`page=1,2,...`). The fetchers stop when a page has fewer than 100 rows or the
running count reaches the total.

**Rate limiting**: the API answers HTTP 429/502/503/504 when pushed. The fetchers use
AIMD pacing: 1.5 s between pages, double the delay on those codes (cap 120 s), and
shave 0.25 s off after each good page. Never run fetchers in parallel.

## Report catalogue

| ID | Short name | Data | Frequency | Filter param (one value per request) | Quirks |
|---|---|---|---|---|---|
| 1 | `exports` | Red meat export volume by destination country | Monthly | none | data from Jan 2000; today OK |
| 2 | `herd` | ABS herd and flock estimates by state | Annual (financial year) | `year` + `stateID`, optional `category` | keyed by year, not dates |
| 3 | `slaughter` | ABS slaughter (000 head) and production (tonnes) by category and state | Quarterly | `category` (optional; unfiltered = all) | data from Mar 2000; today OK |
| 4 | `yardings` | NLRS saleyard yardings (head) by saleyard, category, Prime/Store | Daily | `category` (required) + optional `saleyardID` | toDate must be ≤ yesterday |
| 5 | `indicators` | NLRS national livestock price indicators (18 series) | Daily | `indicatorID` (required) | split by calendar year; toDate ≤ yesterday |
| 6 | `saleyard-indicators` | Same 18 indicators per saleyard | Daily | `indicatorID` (required) + optional `saleyardID` | as report 5; very large dataset |
| 7 | `global-prices` | Cattle price series for AUS (NLRS) and USA (Steiner), in AUD | Daily / weekly | `countryID` (required) | toDate ≤ yesterday |
| 8 | `us-prices` | US domestic cattle prices (Steiner) | Weekly | none | today OK |
| 9 | `us-imports` | US imported beef prices, e.g. 90CL (Steiner) | Weekly | none | today OK |
| 10 | `nlrs-slaughter` | NLRS weekly slaughter head count by state and species | Weekly (Fridays) | `species` (optional; unfiltered = all) | split by calendar year; toDate ≤ yesterday |

"Split by calendar year" means the endpoint returns HTTP 500 for a date range that
crosses 31 December; the fetchers chunk the range per year automatically.
"toDate ≤ yesterday" means the endpoint returns HTTP 500 when `toDate` is today; the
fetchers default to yesterday and clamp later dates.

Date parameters are `fromDate` / `toDate` in `YYYY-MM-DD`. Report 2 uses `year` (integer).

## Per-report details

One file per report with query parameters, CSV columns and units, every valid filter
value, a sample row and the default output path:

- [report1.md](references/report1.md) Red Meat Exports
- [report2.md](references/report2.md) Herd and Flock
- [report3.md](references/report3.md) Slaughter and Production (ABS)
- [report4.md](references/report4.md) Saleyard Yardings
- [report5.md](references/report5.md) Livestock Indicators (national) - includes the 18-indicator table
- [report6.md](references/report6.md) Livestock Indicators by Saleyard - includes the saleyard code list
- [report7.md](references/report7.md) Global Cattle Prices
- [report8.md](references/report8.md) US Domestic Cattle Prices
- [report9.md](references/report9.md) US Imported Meat Prices
- [report10.md](references/report10.md) NLRS Slaughter

## Units glossary

- `c/kg cwt` - Australian cents per kilogram carcase weight (dressed weight)
- `c/kg lwt` - Australian cents per kilogram live weight
- `$/head` - Australian dollars per animal (the two "Online" indicators)
- `US c/lb` - US cents per pound; `cwt` / `lwt` as above
- `000` - thousands of head (report 3 slaughter rows); `Tonnes` - carcase weight (report 3 production rows)
- `90CL`, `85CL` … - chemical lean percentage of manufacturing beef (report 9)

## Where the code lives

- Fetchers: `fetchers/fetch_reportN.py` (module constants `VALID_*`, `CSV_FIELDS`, `DEFAULT_OUTPUT`)
- CLI: `mla.py` (`mla list`, `mla fetch <report> --list-*` print the valid values live)
- Human docs: `README.md` (one section per report), `docs/CLI.md`
- Downloaded data: `data/raw/reportN_*.csv`; merged table `data/processed/merged_weekly.csv`
