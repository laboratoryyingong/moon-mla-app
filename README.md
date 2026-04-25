# MLA Statistics Data Fetcher

A command-line tool for downloading Australian Slaughter and Production data from the [MLA Statistics API](https://www.mla.com.au/prices-markets/statistics/api/).

---

## Requirements

- Python 3.9+
- No external dependencies — uses the standard library only

---

## Quick Start

```bash
# Fetch the last 5 years of all categories
python3 fetch_report3.py

# Fetch a specific date range
python3 fetch_report3.py --from 2020-01-01 --to 2024-12-31

# Save to a custom file name
python3 fetch_report3.py --from 2023-01-01 --to 2023-12-31 --output slaughter_2023.csv
```

---

## Usage

```
python3 fetch_report3.py [--from YYYY-MM-DD] [--to YYYY-MM-DD]
                         [--category CATEGORY [CATEGORY ...]]
                         [--output FILE]
                         [--list-categories]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | 5 years ago (Jan 1) | Start date of the data range |
| `--to YYYY-MM-DD` | Today | End date of the data range |
| `--category` | All categories | Filter by one or more animal categories (see below) |
| `--output FILE` | `report3_slaughter_production.csv` | Output CSV file path |
| `--list-categories` | — | Print all valid category names and exit |

### Available Categories

| Category | Description |
|---|---|
| `Total Red Meat` | Aggregate of all red meat |
| `Calves` | Calves (young cattle) |
| `Cattle (Excl. Calves)` | All cattle excluding calves |
| `Cows And Heifers` | Female cattle |
| `Bulls, Bullocks And Steers` | Male cattle (entire and castrated) |
| `Sheep` | Adult sheep |
| `Lambs` | Lambs (young sheep) |
| `Chickens` | Poultry |
| `Pigs` | Pigs |

> Run `python3 fetch_report3.py --list-categories` to print all category names at any time.

---

## Examples

```bash
# All cattle-related categories for 2022–2024
python3 fetch_report3.py \
  --from 2022-01-01 \
  --to 2024-12-31 \
  --category "Cattle (Excl. Calves)" "Cows And Heifers" "Bulls, Bullocks And Steers"

# Lamb and sheep data for a single year
python3 fetch_report3.py \
  --from 2023-01-01 \
  --to 2023-12-31 \
  --category Lambs Sheep \
  --output lambs_sheep_2023.csv

# Full historical pull (all categories, all time)
python3 fetch_report3.py --from 2000-01-01 --output full_history.csv
```

---

## Output Format

The script saves a CSV file with the following columns:

| Column | Example | Description |
|---|---|---|
| `report_date` | `2024-03-01` | Quarter start date (ABS data is quarterly) |
| `report_type` | `Slaughter` / `Production` | Type of metric |
| `category` | `Lambs` | Animal category |
| `location_id` | `Australia` / `Queensland` | National or state level |
| `unit_of_measure` | `Tonnes` / `000` | Unit (`000` = thousands of head) |
| `value_amt` | `132888.0000` | Recorded value |

### Sample Output

```
report_date,report_type,category,location_id,unit_of_measure,value_amt
2024-03-01,Production,Lambs,Australia,Tonnes,132888.0000
2024-03-01,Slaughter,Cattle (Excl. Calves),Australia,000,1806.6000
2024-03-01,Slaughter,Sheep,Tasmania,000,61.5000
```

---

## API Details

| Item | Value |
|---|---|
| API base URL | `https://api-mlastatistics.mla.com.au` |
| Endpoint | `GET /report/3` |
| Authentication | None required |
| Data source | Australian Bureau of Statistics (ABS), quarterly |
| Pagination | 100 rows per page (handled automatically) |
| Rate limiting | No official limit, but abuse leads to throttling or blacklisting |

The script requests pages at **1.5-second intervals** to stay well within acceptable usage. Do not reduce this delay if running scheduled or repeated pulls.

---

## Terms of Use

All data retrieved from this API is subject to [MLA's Market Report and Information Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/).

For API support, contact: **insights@mla.com.au**
