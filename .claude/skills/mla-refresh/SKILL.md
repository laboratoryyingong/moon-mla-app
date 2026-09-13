---
name: mla-refresh
description: Bring every MLA dataset in data/raw up to date with `mla fetch-all` and rebuild data/processed/merged_weekly.csv with `mla merge`, then report what date range each file now covers. Use when the user says update the data, refresh everything, pull the latest, rebuild the merged table, or asks a question whose answer needs data newer than what is on disk.
---

# Refreshing all MLA data

Run from the repository root. `mla` or `python3 mla.py` are equivalent.

## Standard refresh

```bash
mla fetch-all --from <1 January of last year>
mla merge
```

- `fetch-all` runs the ten reports **one after another**. Do not parallelise or
  launch a second fetch while it runs; the API rate-limits the client and the
  fetchers already pace themselves.
- Expect several minutes. Report 6 (per-saleyard indicators) dominates the run
  time; add `--skip 6` when the user does not need saleyard-level prices.
- `--from` is passed to every report; for report 2 only the year is used. Omit
  `--to` so each report uses its own safe default (yesterday or today).
- Each report overwrites its file in `data/raw/`. A failing report does not stop
  the others; the summary table at the end shows `ok` or `failed` per report and
  the exit code is 1 if anything failed. Re-run just the failures with `--only`.

## Quick refresh (only what `mla merge` needs)

```bash
mla fetch-all --only 5 10 --from <1 January of last year>
mla merge
```

## Refresh a single report

```bash
mla fetch <report> --from <date>
```
See the `mla-fetch` skill for report names and filters.

## What `mla merge` does

Joins `data/raw/report5_livestock_indicators.csv` (prices) with
`data/raw/report10_nlrs_slaughter.csv` (slaughter) into
`data/processed/merged_weekly.csv`, one row per week-ending Friday × species group,
plus `data/processed/indicator_lookup.csv` as a column legend. Requires pandas
(`pip install -e ".[analysis]"`). It prints a coverage summary per species.

## After the run: report coverage

Tell the user the date range now on disk for each file. One line of pandas does
it; the date column differs per report:

```bash
python3 - <<'EOF2'
import pandas as pd, glob, os
cols = {"report1":"result_date","report2":"financial_year","report3":"report_date",
        "report4":"result_date","report5":"calendar_date","report6":"calendar_date",
        "report7":"indicator_date","report8":"indicator_date","report9":"indicator_date",
        "report10":"result_date"}
for f in sorted(glob.glob("data/raw/report*.csv"), key=lambda p: int(os.path.basename(p).split("_")[0][6:])):
    key = os.path.basename(f).split("_")[0]
    s = pd.read_csv(f, usecols=[cols[key]])[cols[key]]
    print(f"{os.path.basename(f):40s} {len(s):>8,} rows  {s.min()} → {s.max()}")
m = pd.to_datetime(pd.read_csv("data/processed/merged_weekly.csv", usecols=["week_ending"])["week_ending"],
                   dayfirst=True, format="mixed")   # tolerates D/M/YYYY if the file was re-saved from Excel
print(f"{'merged_weekly.csv':40s} {len(m):>8,} rows  {m.min().date()} → {m.max().date()}")
EOF2
```

Also relay the `fetch-all` summary table (report, seconds, status) so the user
sees anything that failed.

## Staleness rule of thumb

Daily reports (4, 5, 6, 7) and the weekly ones (8, 9, 10) are worth refreshing if
the max date is more than a week old. Report 1 is monthly, report 3 quarterly,
report 2 annual; a refresh rarely changes them.
