# MLA Statistics Data Fetcher

Command-line tools and a local web app for downloading Australian livestock data from the [MLA Statistics API](https://www.mla.com.au/prices-markets/statistics/api/).

---

## Tools Overview

| Tool | Endpoint | Data | Frequency |
|---|---|---|---|
| `fetch_report1.py` | `/report/1` | Australian Red Meat Exports — volume by country | Monthly |
| `fetch_report10.py` | `/report/10` | NLRS Slaughter — head count by state × species | Weekly (Fridays) |
| `fetch_report5.py` | `/report/5` | NLRS Livestock Indicators — price indices | Daily |
| `merge_reports.py` | — | Join report/5 + report/10 into a weekly analysis table | — |
| `app.py` | — | Local Streamlit web app for `/report/10` | — |

---

## Requirements

- Python 3.9+
- `fetch_report1.py`, `fetch_report10.py`, `fetch_report5.py` — standard library only, no pip required
- `merge_reports.py` — requires `pandas` (`pip install pandas`)
- `app.py` — requires `streamlit` and `pandas` (see [Web App](#web-app) section)

---

## Report 1 — Australian Red Meat Exports

Monthly export volumes for Australian beef and veal by destination country.
Data available from January 2000 to present. No cross-year limitations — any date range works.

### Quick Start

```bash
# Fetch last 3 years (default)
python3 fetch_report1.py

# Fetch a specific date range
python3 fetch_report1.py --from 2024-04-01 --to 2026-04-26

# Custom output file
python3 fetch_report1.py --from 2024-01-01 --to 2024-12-31 --output exports_2024.csv
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 three years ago | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--output FILE` | `report1_red_meat_exports.csv` | Output CSV path |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Countries

| Country / Region |
|---|
| Canada East Coast |
| Canada West Coast |
| China |
| Japan |
| Malaysia |
| Philippines |
| Saudi Arabia |
| South Korea |
| Taiwan |
| USA East Coast |
| USA West Coast |

### Output Format

```
result_date,country_desc,meat_type_group_desc,weight_amt
2024-01-01,China,Beef And Veal,14100058.80
2024-01-01,Japan,Beef And Veal,16331488.84
2024-01-01,South Korea,Beef And Veal,13500000.00
```

| Column | Description |
|---|---|
| `result_date` | Month start date (YYYY-MM-01) |
| `country_desc` | Destination country or region |
| `meat_type_group_desc` | Meat category (currently "Beef And Veal") |
| `weight_amt` | Export weight (kg) |

### Examples

```bash
# Full history from 2000
python3 fetch_report1.py --from 2000-01-01 --to 2026-04-26 --output exports_all.csv

# Recent 1 year
python3 fetch_report1.py --from 2025-04-01 --to 2026-04-26 --output exports_last_year.csv

# 2023–2024 comparison
python3 fetch_report1.py --from 2023-01-01 --to 2024-12-31 --output exports_2023_2024.csv
```

---

## Report 10 — NLRS Slaughter

Weekly slaughter survey from the National Livestock Reporting Service (NLRS).  
Data reported at **state × species** level, released each Friday.

### Quick Start

```bash
# Fetch last year's data for all species
python3 fetch_report10.py

# Fetch a specific date range (cross-year ranges are handled automatically)
python3 fetch_report10.py --from 2024-01-01 --to 2024-12-31

# Filter by species
python3 fetch_report10.py --from 2024-01-01 --to 2024-12-31 --species Cattle Lambs

# See all valid species names
python3 fetch_report10.py --list-species
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--species` | All species | Filter by one or more species (see below) |
| `--output FILE` | `report10_nlrs_slaughter.csv` | Output CSV path |
| `--list-species` | — | Print valid species names and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Species

| Species |
|---|
| `Cattle` |
| `Calves` |
| `Sheep` |
| `Lambs` |
| `Pigs` |
| `Goat` |
| `Deer` |

### Output Format

```
result_date,contributor_state_id,species_id,slaughter_count
2025-01-03,NSW,Cattle,45210
2025-01-03,QLD,Cattle,38900
2025-01-03,VIC,Lambs,112000
```

| Column | Description |
|---|---|
| `result_date` | Week ending date (YYYY-MM-DD) |
| `contributor_state_id` | State — NSW / QLD / SA / TAS / VIC / WA |
| `species_id` | Animal species |
| `slaughter_count` | Head count |

### Examples

```bash
# All cattle and lamb data for 2023 and 2024
python3 fetch_report10.py \
  --from 2023-01-01 \
  --to 2024-12-31 \
  --species Cattle Lambs

# Queensland only workaround — filter in pandas after downloading all states
python3 fetch_report10.py --from 2024-01-01 --to 2024-12-31 --output all_states.csv

# Custom output file
python3 fetch_report10.py \
  --from 2025-01-01 \
  --to 2025-12-31 \
  --output slaughter_2025.csv
```

---

## Report 5 — NLRS Livestock Indicators

Daily price indicators from the National Livestock Reporting Service.  
Updated once per day at 12am AEST.

### Quick Start

```bash
# Fetch all 18 indicators for the default date range (last year to today)
python3 fetch_report5.py

# Fetch specific date range
python3 fetch_report5.py --from 2024-01-01 --to 2024-12-31

# Fetch specific indicators only
python3 fetch_report5.py --indicators 1 4 7 14

# See all valid indicator IDs
python3 fetch_report5.py --list-indicators
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--indicators ID [ID ...]` | All (1–18) | One or more indicator IDs |
| `--output FILE` | `report5_livestock_indicators.csv` | Output CSV path |
| `--list-indicators` | — | Print all indicator IDs and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Indicators

| ID | Species | Indicator | Units |
|---|---|---|---|
| 1 | Cattle | Western Young Cattle Indicator | c/kg cwt |
| 2 | Cattle | National Restocker Yearling Steer Indicator | c/kg lwt |
| 3 | Cattle | National Feeder Steer Indicator | c/kg lwt |
| 4 | Cattle | National Heavy Steer Indicator | c/kg lwt |
| 5 | Cattle | National Heavy Dairy Cow Indicator | c/kg lwt |
| 6 | Sheep | National Light Lamb Indicator | c/kg cwt |
| 7 | Sheep | National Trade Lamb Indicator | c/kg cwt |
| 8 | Sheep | National Heavy Lamb Indicator | c/kg cwt |
| 9 | Sheep | National Merino Lamb Indicator | c/kg cwt |
| 10 | Sheep | National Restocker Lamb Indicator | c/kg cwt |
| 11 | Sheep | National Mutton Indicator | c/kg cwt |
| 12 | Cattle | National Restocker Yearling Heifer Indicator | c/kg lwt |
| 13 | Cattle | National Processor Cow Indicator | c/kg lwt |
| 14 | Cattle | National Young Cattle Indicator | c/kg lwt |
| 15 | Cattle | Online Young Cattle Indicator | c/kg lwt |
| 16 | Sheep | Online Lamb Indicator | $/head |
| 17 | Cattle | National Feeder Heifer Indicator | c/kg lwt |
| 18 | Sheep | Online Sheep Indicator | $/head |

### Output Format

```
calendar_date,species_id,indicator_id,indicator_desc,indicator_units,head_count,indicator_value
2025-01-06,Cattle,1,Western Young Cattle Indicator,c/kg cwt,214.0,476.99
2025-01-06,Sheep,7,National Trade Lamb Indicator,c/kg cwt,8820.0,891.23
```

| Column | Description |
|---|---|
| `calendar_date` | Date (YYYY-MM-DD) |
| `species_id` | `Cattle` or `Sheep` |
| `indicator_id` | Numeric indicator ID |
| `indicator_desc` | Full indicator name |
| `indicator_units` | `c/kg cwt`, `c/kg lwt`, or `$/head` |
| `head_count` | Number of animals in the sample |
| `indicator_value` | Price / value for that day |

### Examples

```bash
# All cattle price indicators for 2024
python3 fetch_report5.py \
  --from 2024-01-01 \
  --to 2024-12-31 \
  --indicators 1 2 3 4 5 12 13 14 15 17

# Lamb indicators only
python3 fetch_report5.py \
  --from 2024-01-01 \
  --to 2024-12-31 \
  --indicators 6 7 8 9 10 16 \
  --output lamb_indicators_2024.csv

# Single indicator — National Young Cattle Indicator (ID 14)
python3 fetch_report5.py --indicators 14 --output nyci.csv
```

---

## Merge Reports — Weekly Analysis Table

Joins `/report/5` price indicators with `/report/10` slaughter counts into a single wide table,
aggregated to **weekly (Friday) granularity** and broken down by species group.

Requires `pandas` (`pip install pandas`).

### Quick Start

```bash
# Step 1 — fetch the raw data (last 1 year)
python3 fetch_report10.py --from 2025-04-01 --to 2026-04-26
python3 fetch_report5.py  --from 2025-04-01 --to 2026-04-26

# Step 2 — merge into a weekly analysis table
python3 merge_reports.py
```

This produces two files:

| Output file | Description |
|---|---|
| `merged_weekly.csv` | Wide table — one row per (week_ending × species_group) |
| `indicator_lookup.csv` | Legend: indicator_id → description, units, applies_to |

### Options

| Flag | Default | Description |
|---|---|---|
| `--r5 FILE` | `report5_livestock_indicators.csv` | Path to report/5 CSV |
| `--r10 FILE` | `report10_nlrs_slaughter.csv` | Path to report/10 CSV |
| `--output FILE` | `merged_weekly.csv` | Output path for the merged table |
| `--lookup FILE` | `indicator_lookup.csv` | Output path for the indicator legend |

### Output Format

`merged_weekly.csv` — one row per week × species:

```
week_ending,species_group,national_slaughter,slaughter_NSW,...,ind_1 Western Young Cattle Indicator (c/kg cwt) price_avg,...
2025-01-03,Cattle,84110,45210,...,476.99,...
2025-01-03,Lambs,112000,,...,,...
```

| Column group | Description |
|---|---|
| `week_ending` | Friday date (YYYY-MM-DD) |
| `species_group` | Cattle / Lambs / Sheep / Calves / Pigs / Goat / Deer |
| `national_slaughter` | Total head count across all states |
| `slaughter_NSW` / `_QLD` / ... | Per-state head count |
| `ind_N ... price_avg` | Weekly average price for indicator N (columns ind_1 → ind_18) |
| `ind_N ... heads_avg` | Weekly average sample size for indicator N (columns ind_1 → ind_18) |

Column names embed the full indicator description and units, e.g.:
`ind_1 Western Young Cattle Indicator (c/kg cwt) price_avg`

### Species → Indicator Mapping

| Species group | Price indicators included |
|---|---|
| Cattle | 1, 2, 3, 4, 5, 12, 13, 14, 15, 17 (10 cattle indicators) |
| Lambs | 6, 7, 8, 9, 10, 16 (6 lamb indicators) |
| Sheep | 11, 18 (2 mutton/sheep indicators) |
| Calves / Pigs / Goat / Deer | Slaughter counts only — no price indicators |

### Examples

```bash
# Default run — uses report10_nlrs_slaughter.csv and report5_livestock_indicators.csv
python3 merge_reports.py

# Custom input files
python3 merge_reports.py \
  --r5 my_report5.csv \
  --r10 my_report10.csv \
  --output analysis_2024.csv

# Full 2-year workflow from scratch
python3 fetch_report10.py --from 2023-01-01 --to 2024-12-31
python3 fetch_report5.py  --from 2023-01-01 --to 2024-12-31
python3 merge_reports.py  --output merged_2023_2024.csv
```

---

## Web App

A local Streamlit app for `/report/10` with interactive date/species selection,
real-time progress log, chart, and CSV download.

### Setup (first time)

```bash
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser.

---

## API Details

| Item | Value |
|---|---|
| Base URL | `https://api-mlastatistics.mla.com.au` |
| Authentication | None required |
| Pagination | 100 rows per page (handled automatically) |
| Rate limiting | Adaptive — starts at 1.5s between pages, backs off on 429/503 |

**Known API limitations:**
- `/report/5` and `/report/10` return HTTP 500 for cross-year date ranges — both scripts split requests by calendar year automatically. `/report/1` has no such restriction.
- `/report/5` requires exactly one `indicatorID` per request — multiple indicators are fetched in separate requests and combined.
- `/report/10` requires exactly one `species` per request — same approach.

---

## Terms of Use

All data is subject to [MLA's Market Report and Information Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/).

API support: **insights@mla.com.au**
