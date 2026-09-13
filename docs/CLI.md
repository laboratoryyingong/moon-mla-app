# `mla` — Command-Line Interface

`mla` is a single entry point for every tool in this repository: it downloads any of
the ten MLA Statistics API reports, runs all of them in one go, builds the weekly
analysis table, and launches the web app.

It needs only the Python standard library. `pandas` is required for `merge`, and
`streamlit` for `app`.

---

## Installation

Two ways to run it. They behave identically.

**Option A — run the script directly (no install):**

```bash
python3 mla.py list
```

**Option B — install the `mla` command (recommended):**

```bash
pip install -e .              # core CLI, standard library only
pip install -e ".[analysis]"  # + pandas, for `mla merge`
pip install -e ".[app]"       # + streamlit and pandas, for `mla app`
```

After installing, `mla` is available on your PATH from any directory:

```bash
mla list
```

The rest of this document uses `mla`. Substitute `python3 mla.py` if you did not install it.

---

## Commands at a glance

| Command | What it does |
|---|---|
| `mla list` | Show the ten reports with their ID, short name, and update frequency |
| `mla fetch <report> [options]` | Download one report to CSV |
| `mla fetch-all [options]` | Download every report for one date range |
| `mla merge [options]` | Join `/report/5` and `/report/10` into a weekly analysis table |
| `mla app` | Launch the Streamlit web app |
| `mla --help` | Top-level help |

---

## `mla list`

Prints the report catalogue. Use either the **ID** or the **short name** in every other command.

```
 ID  Name                 Frequency     Description
------------------------------------------------------------------------------------------
  1  exports              Monthly       Australian Red Meat Exports — volume by country
  2  herd                 Annual        Australian Herd and Flock Figures — ABS estimates
  3  slaughter            Quarterly     Australian Slaughter and Production — ABS figures
  4  yardings             Daily         Saleyard Yardings — NLRS head count by saleyard
  5  indicators           Daily         NLRS Livestock Indicators — national price indices
  6  saleyard-indicators  Daily         NLRS Livestock Indicators — by saleyard
  7  global-prices        Daily/Weekly  Global Cattle Prices — AUS (NLRS) + USA (Steiner)
  8  us-prices            Weekly        US Domestic Cattle Prices — Steiner Consulting
  9  us-imports           Weekly        US Imported Meat Prices — Steiner Consulting
 10  nlrs-slaughter       Weekly        NLRS Slaughter — head count by state × species
```

---

## `mla fetch <report> [options]`

Downloads one report and writes it to CSV.

`<report>` accepts any of these forms: `3`, `report3`, `/report/3`, or the short name `slaughter`.

Everything after `<report>` is passed **unchanged** to that report's fetcher, so each
report keeps its own option set. To see the options for a given report:

```bash
mla fetch 3 --help
mla fetch nlrs-slaughter --help
```

### Options common to every report

| Option | Description |
|---|---|
| `--from YYYY-MM-DD` | Start date. Each report has a sensible default (usually 1 January of last year). |
| `--to YYYY-MM-DD` | End date. Defaults to today or yesterday depending on the report. |
| `--output FILE` | Output CSV path. Default: `data/raw/reportN_<name>.csv` under the repository root. Parent folders are created automatically. |
| `--email EMAIL` | Contact email sent in the `User-Agent` header, as requested by MLA's terms of use. |

> `/report/2` (herd) is an annual dataset and uses `--from-year YYYY` / `--to-year YYYY` instead of `--from` / `--to`.

### Report-specific filters

| Report | Filter option | List valid values with |
|---|---|---|
| 2 `herd` | `--states NSW VIC ...`, `--categories "Cattle" ...` | `--list-states`, `--list-categories` |
| 3 `slaughter` | `--categories "Cattle (Excl. Calves)" Lambs ...` | `--list-categories` |
| 4 `yardings` | `--categories Cattle Lamb Sheep`, `--saleyard ID` | `--list-categories` |
| 5 `indicators` | `--indicators 1 2 3 ...` | `--list-indicators` |
| 6 `saleyard-indicators` | `--indicators 1 2 ...`, `--saleyard ID` | `--list-indicators` |
| 7 `global-prices` | `--countries AUS USA` | `--list-countries` |
| 10 `nlrs-slaughter` | `--species Cattle Lambs ...` | `--list-species` |

Reports 1, 8 and 9 have no filters beyond the date range.

### Examples

```bash
# Default date range, default output location
mla fetch exports

# Explicit range
mla fetch 3 --from 2020-01-01 --to 2024-12-31

# Filter by category and write somewhere else
mla fetch slaughter --categories "Cattle (Excl. Calves)" Lambs --output ~/Desktop/slaughter.csv

# Annual report — uses years, not dates
mla fetch herd --from-year 2018 --to-year 2021 --states NSW VIC QLD

# Discover valid filter values
mla fetch indicators --list-indicators
mla fetch 10 --list-species
```

### What you see while it runs

Each fetcher prints a header, a live progress bar with rows fetched, seconds per page
and an ETA, then a summary. If the API answers with HTTP 429 or 503 the fetcher
slows down automatically and prints a warning; no action is needed.

```
============================================================
MLA Statistics API — /report/3 Australian Slaughter & Production
============================================================
  Date range : 2020-01-01 → 2024-12-31
  Categories : all categories
  Output     : data/raw/report3_slaughter_production.csv
  ...
Page 2/8  [██████░░░░░░░░░░░░░░░░░░░] 25%  200/800 rows  2.1s/page  delay=1.5s  elapsed=6s  ETA 18s
...
Saved 800 rows to /path/to/data/raw/report3_slaughter_production.csv
Total runtime: 29s
```

---

## `mla fetch-all [options]`

Runs every report in sequence for one date range. Reports run one after another
(never in parallel) to stay well within the API's rate limits. A failure in one
report does not stop the others; a summary table is printed at the end and the exit
code is `1` if anything failed.

| Option | Description |
|---|---|
| `--from YYYY-MM-DD` | Start date passed to every report. For `/report/2` only the year is used. Omit to use each report's own default. |
| `--to YYYY-MM-DD` | End date. Same rules as `--from`. |
| `--email EMAIL` | Contact email for the `User-Agent` header. |
| `--output-dir DIR` | Folder for the CSV files. Default: `data/raw/`. File names are the same as for `mla fetch`. |
| `--only REPORT ...` | Run only the listed reports (IDs or names). |
| `--skip REPORT ...` | Skip the listed reports. |

### Examples

```bash
# Everything, last year to date, into data/raw/
mla fetch-all --from 2025-01-01

# Only the two inputs that `mla merge` needs
mla fetch-all --only indicators nlrs-slaughter --from 2024-01-01 --to 2024-12-31

# Everything except the large per-saleyard dataset, into a dated folder
mla fetch-all --skip 6 --from 2025-01-01 --output-dir exports/2025-09-13
```

Summary printed at the end:

```
======================================================================
fetch-all summary  (3m12s total)
======================================================================
  report 1   exports                   7s   ok
  report 2   herd                     41s   ok
  report 3   slaughter                12s   ok
  ...
  report 10  nlrs-slaughter           19s   ok
```

---

## `mla merge [options]`

Joins the `/report/5` price indicators with the `/report/10` slaughter counts into a
weekly (Friday-ending) wide table, one row per week × species group. Requires `pandas`.

| Option | Default | Description |
|---|---|---|
| `--r5 FILE` | `data/raw/report5_livestock_indicators.csv` | Input: report/5 CSV |
| `--r10 FILE` | `data/raw/report10_nlrs_slaughter.csv` | Input: report/10 CSV |
| `--output FILE` | `data/processed/merged_weekly.csv` | Output: merged table |
| `--lookup FILE` | `data/processed/indicator_lookup.csv` | Output: column legend |

```bash
# Typical workflow
mla fetch-all --only 5 10 --from 2024-01-01
mla merge

# Custom inputs and output
mla merge --r5 my_r5.csv --r10 my_r10.csv --output analysis_2024.csv
```

The column layout and the species → indicator mapping are documented in
[README.md — Merge Reports](../README.md#merge-reports).

---

## `mla app`

Starts the Streamlit web app (`app.py`) and opens it at `http://localhost:8501`.
Equivalent to `streamlit run app.py`. Requires `streamlit` and `pandas`.

```bash
mla app
```

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Invalid arguments, unknown report, network/API failure, or at least one report failed in `fetch-all` |

---

## How it works

`mla.py` is a thin dispatcher. It does not reimplement any fetching logic:

- `fetch <report>` imports `fetchers/fetch_reportN.py` and calls its `main()` with the
  remaining arguments, exactly as if you had run that script directly.
- `fetch-all` does the same in a loop, translating the shared `--from` / `--to` into
  each report's own flags.
- `merge` calls `analysis/merge_reports.py`; `app` runs `streamlit run app.py`.

This means the individual scripts still work on their own
(`python3 fetchers/fetch_report3.py --help`), and adding a new report only requires
a new `fetchers/fetch_reportN.py` plus one line in the `REPORTS` table in `mla.py`.

---

## Terms of use

All data is provided by Meat & Livestock Australia and is subject to the
[MLA Market Reports and Information Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/).
Always pass a real contact address with `--email` so MLA can reach you if needed.
