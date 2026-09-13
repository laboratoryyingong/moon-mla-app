---
name: mla-fetch
description: Download MLA Statistics API data with the `mla` CLI - picks the right report, filters and date range, runs the fetch, and explains the progress output. Use when the user asks to download, fetch, pull, get, grab or update MLA data such as cattle or lamb prices, slaughter numbers, exports, yardings, herd figures or US prices.
---

# Fetching MLA data with `mla`

Always run from the repository root. The command is `mla` if the package is
installed (`pip install -e .`), otherwise `python3 mla.py`. Both behave identically.

## Workflow

1. **Pick the report.** `mla list` prints the ten reports. If unsure which one holds
   the data, consult the `mla-api-reference` skill rather than guessing.
2. **Discover valid filter values before typing them.** Never invent a category,
   species or indicator name; the API silently returns zero rows for a wrong one.
   ```bash
   mla fetch 3 --list-categories
   mla fetch 2 --list-states      # and --list-categories
   mla fetch 4 --list-categories
   mla fetch 5 --list-indicators  # same IDs for report 6
   mla fetch 7 --list-countries
   mla fetch 10 --list-species
   ```
3. **Choose the date range.**
   - Dates are `--from YYYY-MM-DD --to YYYY-MM-DD`.
   - Report 2 (herd) is annual: use `--from-year YYYY --to-year YYYY` instead.
   - Reports 4, 5, 6, 7 and 10 reject today as the end date; the fetchers default
     to yesterday and clamp anything later, so leave `--to` off unless a specific
     cut-off is wanted.
   - Reports 5, 6 and 10 cannot cross a calendar year in one request; the fetcher
     splits the range per year automatically. Expect one progress block per year.
   - Omitting both dates gives each report's default (usually 1 January last year
     to yesterday/today; report 1 goes back three years).
4. **Run the fetch.** Output goes to `data/raw/reportN_<name>.csv` unless
   `--output FILE` is given. Parent folders are created automatically.
5. **Report back** the row count, the file path and the date range actually
   covered (first and last date in the CSV).

## Recipes

| Request | Command |
|---|---|
| Last 12 months of trade lamb prices | `mla fetch indicators --indicators 7 --from <12 months ago>` |
| All 18 national indicators this year | `mla fetch indicators --from <1 Jan this year>` |
| Heavy steer price at one saleyard | `mla fetch saleyard-indicators --indicators 4 --saleyard WAG --from ...` |
| Weekly cattle slaughter by state | `mla fetch nlrs-slaughter --species Cattle --from ...` |
| Lamb and sheep slaughter | `mla fetch 10 --species Lambs Sheep --from ...` |
| ABS quarterly slaughter, cattle only | `mla fetch slaughter --categories "Cattle (Excl. Calves)" --from 2020-01-01` |
| Beef exports since 2015 | `mla fetch exports --from 2015-01-01` |
| Herd numbers for NSW and QLD | `mla fetch herd --from-year 2016 --to-year 2022 --states NSW QLD` |
| Cattle yardings at Roma | `mla fetch yardings --categories Cattle --saleyard ROM --from ...` |
| AUS vs US cattle prices | `mla fetch global-prices --from ...` |
| US 90CL import price | `mla fetch us-imports --from ...` (no filter; all series returned) |
| Everything, one range | `mla fetch-all --from <date>` (see the `mla-refresh` skill) |

Quote names containing spaces or parentheses. Use full dates; do not pass
relative phrases to the CLI.

## Size warnings

- Report 6 is enormous unfiltered (all indicators × all saleyards × every day).
  Always pass `--indicators` and preferably `--saleyard`; a full year of one
  indicator is fine.
- Report 5 with all 18 indicators for one year takes a few minutes because each
  indicator is a separate paged request.
- Never run two fetches at the same time; the API rate-limits by client.

## Reading the progress output

```
Page 2/8  [██████░░░░░░░░░░░░░░░░░░░] 25%  200/800 rows  2.1s/page  delay=1.5s  elapsed=6s  ETA 18s
Waiting 1.5s before page 3 ...
⚠  Rate limited (HTTP 429) — backing off to 3.0s
Fetch complete: 800 rows in 28s  (28.6 rows/s,  8 page(s))
Saved 800 rows to /abs/path/data/raw/report3_slaughter_production.csv
```

- `delay` is the adaptive pause between pages; it doubles on 429/502/503/504 and
  decays back to 1.5 s. A backoff warning is normal and needs no action; only
  give up if the delay climbs past a minute repeatedly.
- `0 rows` with no error almost always means a wrong filter value or a date range
  outside the data (e.g. report 2 years with no ABS release).
- Any other HTTP error or a network error aborts the run with exit code 1.

## Options common to every report

`--from`, `--to` (or `--from-year`/`--to-year` for report 2), `--output FILE`,
`--email ADDRESS` (goes into the User-Agent as required by MLA's terms), and
`mla fetch <report> --help` for that report's full list.
