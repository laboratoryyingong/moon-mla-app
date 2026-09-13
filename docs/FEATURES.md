# Feature Overview

## Two ways to use the tools

### 1. Local web app (recommended for interactive use)

```bash
pip install -r requirements.txt
streamlit run app.py        # or: mla app
```

The browser opens at `http://localhost:8501`.

### 2. Command line

```bash
mla list
mla fetch 10 --from 2024-01-01 --to 2024-12-31
mla fetch nlrs-slaughter --species Cattle Lambs
mla fetch 10 --output my_data.csv
```

Every fetcher can also be run directly, e.g. `python3 fetchers/fetch_report10.py --help`.
See [CLI.md](CLI.md) for the full command reference.

---

## Web app (app.py) — /report/10 NLRS Slaughter

| Feature | Description |
|---|---|
| Date pickers | Graphical From / To selection, default from 1 January last year to today |
| Species multiselect | Leave empty to fetch all seven species |
| Live progress bar | Current page / total pages, rows fetched, elapsed time, ETA |
| Live log panel | Timestamped log of every page, wait, and warning during the fetch |
| Rate-limit notice | On HTTP 429/503 the app shows a warning and backs off automatically |
| Summary metrics | Total rows, number of species, and date range after the fetch |
| Species chart | Horizontal bar chart of total slaughter by species |
| Data table | Full result preview with sorting and filtering |
| Download CSV | One-click download of the four output columns |
| Advanced settings | Collapsible panel to change the contact email sent in the User-Agent header |
| Last fetch log | The previous run's log stays available in a collapsed expander |

---

## CLI output (all fetchers)

| Output | Example |
|---|---|
| Run header | Date range, filters, output file, contact email, start time |
| Progress bar | `[███░░░░░░░░░░░░░░░░░░░░░░] 12%` |
| Per-page detail | `Page 2/8  100/800 rows  2.1s/page  delay=1.5s  elapsed=6s  ETA 18s` |
| Wait notice | `Waiting 1.5s before page 3 ...` |
| Rate limit | `⚠  Rate limited (HTTP 429) — backing off to 3.0s` |
| Fetch summary | `Fetch complete: 800 rows in 28s  (28.6 rows/s,  8 page(s))` |
| Total runtime | `Total runtime: 29s` |

---

## Species supported by /report/10

```
Cattle / Calves / Sheep / Lambs / Pigs / Goat / Deer
```

---

## Project layout

```
moon-mla-app/
├── mla.py                      # Unified CLI entry point
├── app.py                      # Streamlit web app (/report/10)
├── fetchers/                   # One fetch script per report + CLI entry point
│   └── fetch_report1.py … fetch_report10.py
├── analysis/merge_reports.py   # Weekly merge of report 5 + report 10
├── data/raw/                   # CSV output of the fetchers (default location)
├── data/processed/             # merged_weekly.csv, indicator_lookup.csv
├── assets/                     # TFI logo
├── docs/                       # Documentation
└── requirements.txt            # streamlit, pandas
```
