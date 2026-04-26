# MLA Statistics Data Fetcher

Command-line tools and a local web app for downloading Australian livestock data from the [MLA Statistics API](https://www.mla.com.au/prices-markets/statistics/api/).

---

## Tools Overview

| Tool | Endpoint | Data | Frequency |
|---|---|---|---|
| `fetch_report10.py` | `/report/10` | NLRS Slaughter — head count by state × species | Weekly (Fridays) |
| `fetch_report5.py` | `/report/5` | NLRS Livestock Indicators — price indices | Daily |
| `app.py` | — | Local Streamlit web app for `/report/10` | — |

---

## Requirements

- Python 3.9+
- `fetch_report10.py` and `fetch_report5.py` — standard library only, no pip required
- `app.py` — requires `streamlit` and `pandas` (see [Web App](#web-app) section)

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

## Web App

A local Streamlit app for `/report/10` with interactive date/species selection,
real-time progress log, chart, and CSV download.

### Setup (first time)

```bash
pip install -r requirements.txt
```

Or on macOS, double-click **启动APP.command** — it installs dependencies and starts the app automatically.

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
- Cross-year date ranges return HTTP 500 — both scripts split requests by calendar year automatically.
- `/report/5` requires exactly one `indicatorID` per request — multiple indicators are fetched in separate requests and combined.
- `/report/10` requires exactly one `species` per request — same approach.

---

## Terms of Use

All data is subject to [MLA's Market Report and Information Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/).

API support: **insights@mla.com.au**
