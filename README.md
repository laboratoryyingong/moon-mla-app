# MLA Statistics Data Fetcher

Command-line tools and a local web app for downloading Australian livestock data from the [MLA Statistics API](https://www.mla.com.au/prices-markets/statistics/api/).

---

## Tools Overview

| Tool | Endpoint | Data | Frequency |
|---|---|---|---|
| `fetch_report1.py` | `/report/1` | Australian Red Meat Exports — volume by country | Monthly |
| `fetch_report2.py` | `/report/2` | Australian Herd and Flock Figures — ABS estimates by state | Annual (financial year) |
| `fetch_report3.py` | `/report/3` | Australian Slaughter and Production — ABS figures by category | Quarterly |
| `fetch_report4.py` | `/report/4` | Australian Saleyard Yardings — NLRS head count by saleyard × category | Daily |
| `fetch_report5.py` | `/report/5` | NLRS Livestock Indicators — national price indices | Daily |
| `fetch_report6.py` | `/report/6` | NLRS Livestock Indicators (By Saleyard) — price indices per saleyard | Daily |
| `fetch_report7.py` | `/report/7` | Global Cattle Prices — NLRS (AUS) + US Steiner Consulting (USA) | Daily / Weekly |
| `fetch_report8.py` | `/report/8` | US Domestic Cattle Prices — US Steiner Consulting | Weekly |
| `fetch_report9.py` | `/report/9` | US Imported Meat Prices — US Steiner Consulting | Weekly |
| `fetch_report10.py` | `/report/10` | NLRS Slaughter — head count by state × species | Weekly (Fridays) |
| `merge_reports.py` | — | Join report/5 + report/10 into a weekly analysis table | — |
| `app.py` | — | Local Streamlit web app for `/report/10` | — |

---

## Requirements

- Python 3.9+
- `fetch_report1.py`, `fetch_report2.py`, `fetch_report3.py`, `fetch_report4.py`, `fetch_report5.py`, `fetch_report6.py`, `fetch_report7.py`, `fetch_report8.py`, `fetch_report9.py`, `fetch_report10.py` — standard library only, no pip required
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

## Report 2 — Australian Herd and Flock Figures

Annual herd and flock estimates sourced from the Australian Bureau of Statistics (ABS),
reported at **state × animal category** level. Each financial year is one data release.

Data available approximately from 2015-16 to 2020-21. Years with no ABS release return zero rows.

The API accepts only one `stateID` and one `category` per request — the script iterates over
all `(year × state × category)` combinations automatically.

### Quick Start

```bash
# Fetch all available years, all states, all categories (default)
python3 fetch_report2.py

# Fetch specific years
python3 fetch_report2.py --from-year 2018 --to-year 2021

# Specific states only
python3 fetch_report2.py --from-year 2018 --to-year 2021 --states NSW VIC QLD

# Specific categories only
python3 fetch_report2.py --from-year 2018 --to-year 2021 --categories "Cattle" "Meat cattle"

# See all valid values
python3 fetch_report2.py --list-states
python3 fetch_report2.py --list-categories
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from-year YEAR` | `2015` | Start year (integer) |
| `--to-year YEAR` | Current year | End year (integer) |
| `--states` | All 6 states | Filter by one or more states (see below) |
| `--categories` | All categories | Filter by one or more categories (see below) |
| `--output FILE` | `report2_herd_flock.csv` | Output CSV path |
| `--list-states` | — | Print valid state IDs and exit |
| `--list-categories` | — | Print valid category names and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available States

| State |
|---|
| `NSW` |
| `SA` |
| `VIC` |
| `QLD` |
| `WA` |
| `TAS` |

### Available Categories

| Category |
|---|
| `Cattle` |
| `Dairy cattle` |
| `Meat cattle` |
| `Sheep and lambs` |
| `Sheep and lambs - Lambs under 1 year` |
| `Sheep and lambs - Breeding ewes 1 year or over` |
| `Sheep and lambs - Marked lambs under 1 year` |

### Output Format

```
financial_year,region_desc,subcategory_desc,metric_desc,estimate_value
2020-21,NSW,Meat cattle,Total,3602632.66
2020-21,NSW,Sheep and lambs,Total,25481234.50
2020-21,VIC,Dairy cattle,Cows in milk and dry,938210.00
```

| Column | Description |
|---|---|
| `financial_year` | ABS financial year (e.g. `2020-21`) |
| `region_desc` | State |
| `subcategory_desc` | Animal category — matches the `category` filter values |
| `metric_desc` | Metric within category (Total / Calves less than 1 year / …) |
| `estimate_value` | Head count estimate |

### Examples

```bash
# All available data, all states and categories
python3 fetch_report2.py --from-year 2015 --to-year 2021 --output herd_flock_all.csv

# Cattle only, all states
python3 fetch_report2.py \
  --from-year 2015 --to-year 2021 \
  --categories "Cattle" "Dairy cattle" "Meat cattle" \
  --output cattle_herd.csv

# Sheep and lambs for QLD and NSW only
python3 fetch_report2.py \
  --from-year 2015 --to-year 2021 \
  --states NSW QLD \
  --categories "Sheep and lambs" "Sheep and lambs - Lambs under 1 year" \
  --output sheep_nsw_qld.csv
```

---

## Report 3 — Australian Slaughter and Production

Quarterly slaughter and production figures at **animal category × location** level,
sourced from the Australian Bureau of Statistics (ABS). Data available from March 2000 to present.

No cross-year limitations — any date range works. The API accepts one category per request;
when multiple categories are selected the script iterates and combines results automatically.

### Quick Start

```bash
# Fetch last year, all categories (default)
python3 fetch_report3.py

# Fetch a specific date range
python3 fetch_report3.py --from 2022-01-01 --to 2024-12-31

# Fetch specific categories only
python3 fetch_report3.py --categories Cattle Lambs Sheep

# See all valid category names
python3 fetch_report3.py --list-categories
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--categories` | All categories | Filter by one or more categories (see below) |
| `--output FILE` | `report3_slaughter_production.csv` | Output CSV path |
| `--list-categories` | — | Print valid category names and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Categories

| Category |
|---|
| `Total Red Meat` |
| `Calves` |
| `Cattle (Excl. Calves)` |
| `Cows And Heifers` |
| `Bulls, Bullocks And Steers` |
| `Sheep` |
| `Lambs` |
| `Chickens` |
| `Pigs` |

### Output Format

```
report_date,report_type,category,location_id,unit_of_measure,value_amt
2024-03-01,Slaughter,Lambs,Victoria,000,4521.2000
2024-03-01,Production,Lambs,Victoria,Tonnes,18430.5000
2024-03-01,Slaughter,Cattle (Excl. Calves),Australia,000,712.4000
```

| Column | Description |
|---|---|
| `report_date` | Quarter end date (YYYY-MM-01, quarterly) |
| `report_type` | `Slaughter` or `Production` |
| `category` | Animal category |
| `location_id` | State name or `Australia` (national total) |
| `unit_of_measure` | `000` (thousands of head) or `Tonnes` |
| `value_amt` | The measured value |

### Examples

```bash
# Full history from 2000, all categories
python3 fetch_report3.py --from 2000-01-01 --to 2026-04-26 --output r3_all.csv

# Recent 1 year
python3 fetch_report3.py --from 2025-04-01 --to 2026-04-26

# Cattle and sheep only for 2023–2024
python3 fetch_report3.py \
  --from 2023-01-01 \
  --to 2024-12-31 \
  --categories "Cattle (Excl. Calves)" "Cows And Heifers" "Bulls, Bullocks And Steers" Sheep Lambs \
  --output cattle_sheep_2023_2024.csv
```

---

## Report 4 — Australian Saleyard Yardings

Daily saleyard yardings at the **saleyard × category** level, collected by the National Livestock
Reporting Service (NLRS) and updated once per day at 12am AEST.

No cross-year limitations — any date range works. The API requires one category per request;
when multiple categories are selected the script iterates and combines results automatically.

### Quick Start

```bash
# Fetch last year, all categories (default)
python3 fetch_report4.py

# Fetch a specific date range
python3 fetch_report4.py --from 2024-01-01 --to 2024-12-31

# Fetch specific categories only
python3 fetch_report4.py --categories Cattle Lamb

# Filter by saleyard
python3 fetch_report4.py --saleyard WAG

# See all valid category names
python3 fetch_report4.py --list-categories
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--categories` | All categories | Filter by one or more categories (see below) |
| `--saleyard ID` | All saleyards | Filter by saleyard ID (e.g. `WAG`, `WOD`) |
| `--output FILE` | `report4_saleyard_yardings.csv` | Output CSV path |
| `--list-categories` | — | Print valid category names and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Categories

| Category |
|---|
| `Cattle` |
| `Lamb` |
| `Sheep` |

### Output Format

```
result_date,category_desc,state_id,saleyard_id,tranx_type_id,head_count
2025-01-10,Cattle,VIC,WOD,Store,3500.0
2025-01-06,Cattle,NSW,WAG,Prime,2435.0
2025-01-06,Lamb,NSW,WAG,Prime,8210.0
```

| Column | Description |
|---|---|
| `result_date` | Date (YYYY-MM-DD) |
| `category_desc` | Animal category (`Cattle` / `Lamb` / `Sheep`) |
| `state_id` | State — NSW / QLD / SA / TAS / VIC / WA |
| `saleyard_id` | Saleyard code (e.g. `WAG` = Wagga Wagga, `WOD` = Wodonga) |
| `tranx_type_id` | Transaction type (`Prime` or `Store`) |
| `head_count` | Number of animals yarded |

### Examples

```bash
# Full history from 2000, all categories
python3 fetch_report4.py --from 2000-01-01 --to 2026-04-26 --output yardings_all.csv

# Cattle only for 2024
python3 fetch_report4.py --from 2024-01-01 --to 2024-12-31 --categories Cattle --output cattle_yardings_2024.csv

# One specific saleyard (Wagga Wagga), all categories
python3 fetch_report4.py --saleyard WAG --output yardings_wag.csv

# Compare lamb yardings 2023 vs 2024
python3 fetch_report4.py \
  --from 2023-01-01 \
  --to 2024-12-31 \
  --categories Lamb \
  --output lamb_yardings_2023_2024.csv
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

## Report 6 — NLRS Livestock Indicators (By Saleyard)

Daily NLRS livestock price indicators broken down at the **saleyard** level.
Same 18 indicator IDs as `/report/5`, but each row shows the contribution from
an individual saleyard rather than the national aggregate.

Updated once per day at 12am AEST. Cross-year date ranges are handled automatically by splitting
into per-calendar-year requests (the API returns HTTP 500 for cross-year queries).
The API accepts one `indicatorID` per request; the script iterates and combines results automatically.

### Quick Start

```bash
# Fetch all 18 indicators for the default date range (last year to today)
python3 fetch_report6.py

# Fetch a specific date range
python3 fetch_report6.py --from 2024-01-01 --to 2024-12-31

# Fetch specific indicators only
python3 fetch_report6.py --indicators 1 4 7

# Filter by a specific saleyard
python3 fetch_report6.py --saleyard WAG

# See all valid indicator IDs
python3 fetch_report6.py --list-indicators
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--indicators ID [ID ...]` | All (1–18) | One or more indicator IDs |
| `--saleyard ID` | All saleyards | Filter by saleyard ID (e.g. `WAG`, `WOD`) |
| `--output FILE` | `report6_saleyard_indicators.csv` | Output CSV path |
| `--list-indicators` | — | Print all indicator IDs and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Indicators

Same 18 indicators as `/report/5`:

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
calendar_date,species_id,saleyard_id,indicator_id,indicator_desc,indicator_units,head_count,indicator_value
2025-01-06,Cattle,MUC,1,Western Young Cattle Indicator,c/kg cwt,214.0,476.9894
2025-01-07,Cattle,MTB,1,Western Young Cattle Indicator,c/kg cwt,2245.0,665.0496
2025-01-06,Sheep,WAG,7,National Trade Lamb Indicator,c/kg cwt,8820.0,891.2300
```

| Column | Description |
|---|---|
| `calendar_date` | Date (YYYY-MM-DD) |
| `species_id` | `Cattle` or `Sheep` |
| `saleyard_id` | Saleyard code contributing to the indicator |
| `indicator_id` | Numeric indicator ID |
| `indicator_desc` | Full indicator name |
| `indicator_units` | `c/kg cwt`, `c/kg lwt`, or `$/head` |
| `head_count` | Number of animals at that saleyard |
| `indicator_value` | Price / value for that day at that saleyard |

### Examples

```bash
# All cattle indicators at saleyard level for 2024
python3 fetch_report6.py \
  --from 2024-01-01 \
  --to 2024-12-31 \
  --indicators 1 2 3 4 5 12 13 14 15 17 \
  --output cattle_saleyard_2024.csv

# National Trade Lamb Indicator (ID 7) across all saleyards
python3 fetch_report6.py --indicators 7 --output lamb_trade_by_saleyard.csv

# One specific saleyard (Wagga Wagga), all indicators
python3 fetch_report6.py --saleyard WAG --output wag_indicators.csv
```

---

## Report 7 — Global Cattle Prices

Global livestock price indicators from two sources:
- **AUS** — National Livestock Reporting Service (NLRS), updated daily at 12am AEST
- **USA** — US Steiner Consulting indicators, updated weekly (Tuesday)

No cross-year limitations — any date range works. The API requires one `countryID` per request;
the script iterates both countries and combines results automatically.

### Quick Start

```bash
# Fetch last year, both countries (default)
python3 fetch_report7.py

# Fetch a specific date range
python3 fetch_report7.py --from 2024-01-01 --to 2024-12-31

# Australian indicators only
python3 fetch_report7.py --countries AUS

# US indicators only
python3 fetch_report7.py --countries USA

# See valid country IDs
python3 fetch_report7.py --list-countries
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--countries` | AUS USA | Country IDs to fetch (see below) |
| `--output FILE` | `report7_global_cattle_prices.csv` | Output CSV path |
| `--list-countries` | — | Print valid country IDs and exit |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Country IDs

| Country | Source | Update Frequency | Indicators |
|---|---|---|---|
| `AUS` | NLRS | Daily (12am AEST) | Multiple cattle price indicators (same set as /report/5) |
| `USA` | US Steiner Consulting | Weekly (Tuesday) | Fed Steer 5-Day Average, CME Feeder Cattle Index |

### Output Format

```
indicator_date,species_id,country_code,indicator_desc,indicator_units,indicator_value,currency_code
2025-01-06,Cattle,AUS,National Feeder Steer Indicator,c/kg lwt,391.36320000000000,AUD
2025-01-06,Cattle,AUS,National Heavy Steer Indicator,c/kg lwt,356.71030000000000,AUD
2025-01-07,Cattle,USA,Fed Steer 5-Day Average,$/cwt,198.50,USD
```

| Column | Description |
|---|---|
| `indicator_date` | Date (YYYY-MM-DD) |
| `species_id` | Animal species (e.g. `Cattle`) |
| `country_code` | `AUS` or `USA` |
| `indicator_desc` | Indicator name |
| `indicator_units` | Unit of measure (e.g. `c/kg lwt`, `$/cwt`) |
| `indicator_value` | Price value |
| `currency_code` | `AUD` (AUS) or `USD` (USA) |

### Examples

```bash
# Full history, both countries
python3 fetch_report7.py --from 2000-01-01 --to 2026-04-26 --output global_cattle_all.csv

# Australian indicators for 2024
python3 fetch_report7.py --from 2024-01-01 --to 2024-12-31 --countries AUS --output aus_cattle_2024.csv

# US indicators for comparison
python3 fetch_report7.py --from 2024-01-01 --to 2024-12-31 --countries USA --output usa_cattle_2024.csv
```

---

## Report 8 — US Domestic Cattle Prices

Weekly US cattle and beef price indicators sourced from **US Steiner Consulting**.
Data is updated every Tuesday.

No cross-year limitations — any date range works, including today's date.
No category or country filter is required; all indicators are returned in a single paginated response.

### Quick Start

```bash
# Fetch last year's data (default)
python3 fetch_report8.py

# Fetch a specific date range
python3 fetch_report8.py --from 2024-01-01 --to 2024-12-31

# Custom output file
python3 fetch_report8.py --from 2024-01-01 --to 2024-12-31 --output us_prices_2024.csv
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--output FILE` | `report8_us_cattle_prices.csv` | Output CSV path |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Indicators

| Indicator | Units |
|---|---|
| CME Feeder Cattle Index | US c/lb lwt |
| Fed Steer, 5-Day Average | US c/lb lwt |
| Breaker Cows, Carcass Price, 75% lean | US c/lb cwt |
| Cutter Cow, Carcass Price, 90% Lean | US c/lb cwt |
| Cutter Cow Carcass Cutout | US c/lb cwt |
| Bonner Cows, 85% lean | US c/lb cwt |

### Output Format

```
indicator_name,indicator_date,indicator_units,indicator_value
CME Feeder Cattle Index,2025-01-02,US c/lb lwt,265.76
Fed Steer, 5-Day Average,2025-01-03,US c/lb lwt,195.74
Breaker Cows, Carcass Price, 75% lean,2025-01-03,US c/lb cwt,228.00
```

| Column | Description |
|---|---|
| `indicator_name` | Price indicator name |
| `indicator_date` | Date (YYYY-MM-DD) |
| `indicator_units` | Unit of measure (`US c/lb lwt` or `US c/lb cwt`) |
| `indicator_value` | Price value in USD |

### Examples

```bash
# Full history
python3 fetch_report8.py --from 2020-01-01 --output us_cattle_all.csv

# Compare 2023 vs 2024
python3 fetch_report8.py --from 2023-01-01 --to 2024-12-31 --output us_cattle_2023_2024.csv

# Recent data only
python3 fetch_report8.py --from 2025-01-01 --output us_cattle_2025.csv
```

---

## Report 9 — US Imported Meat Prices

Weekly US imported beef price indicators sourced from **US Steiner Consulting**.
Data is updated every Tuesday.

No cross-year limitations — any date range works, including today's date.
No category or country filter is required; all indicators are returned in a single paginated response.

### Quick Start

```bash
# Fetch last year's data (default)
python3 fetch_report9.py

# Fetch a specific date range
python3 fetch_report9.py --from 2024-01-01 --to 2024-12-31

# Custom output file
python3 fetch_report9.py --from 2024-01-01 --to 2024-12-31 --output us_imported_meat_2024.csv
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--from YYYY-MM-DD` | Jan 1 of last year | Start date |
| `--to YYYY-MM-DD` | Today | End date |
| `--output FILE` | `report9_us_imported_meat_prices.csv` | Output CSV path |
| `--email EMAIL` | `moon.zhou@thomasfoods.com` | Contact email sent in User-Agent header |

### Available Indicators

| Indicator | Units |
|---|---|
| Cap Off Insides | US c/lb |
| 85CL Trim | US c/lb |
| 85CL Cow Fores | US c/lb |
| 90CL Boneless Beef, NZ | US c/lb |
| 90CL Boneless Beef, NZ/Australia | US c/lb |
| 90CL Shank | US c/lb |
| 80CL Trim | US c/lb |
| Steer Knuckles | US c/lb |
| 95CL Bull Meat, West Coast | US c/lb |
| 75CL Trim | US c/lb |
| 95CL Bull Meat, East Coast | US c/lb |
| Steer Flats | US c/lb |

### Output Format

```
indicator_name,indicator_date,indicator_units,indicator_value
Cap Off Insides,2025-01-03,US c/lb,365.00
90CL Boneless Beef, NZ,2025-01-03,US c/lb,297.50
95CL Bull Meat, East Coast,2025-01-03,US c/lb,316.00
```

| Column | Description |
|---|---|
| `indicator_name` | Price indicator name |
| `indicator_date` | Date (YYYY-MM-DD) |
| `indicator_units` | Unit of measure (`US c/lb`) |
| `indicator_value` | Price value in USD |

### Examples

```bash
# Full history
python3 fetch_report9.py --from 2020-01-01 --output us_imported_meat_all.csv

# Compare 2023 vs 2024
python3 fetch_report9.py --from 2023-01-01 --to 2024-12-31 --output us_imported_meat_2023_2024.csv

# Recent data only
python3 fetch_report9.py --from 2025-01-01 --output us_imported_meat_2025.csv
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
- `/report/5`, `/report/6`, and `/report/10` return HTTP 500 for cross-year date ranges — all three scripts split requests by calendar year automatically. `/report/1`, `/report/3`, `/report/4`, `/report/7`, `/report/8`, and `/report/9` have no such restriction.
- `/report/4`, `/report/5`, `/report/6`, and `/report/10` reject `toDate = today` with HTTP 500 — their default end date is yesterday. `/report/1`, `/report/3`, `/report/7`, `/report/8`, and `/report/9` accept today's date.
- `/report/4` requires exactly one `category` per request — multiple categories are fetched in separate requests and combined.
- `/report/5` and `/report/6` require exactly one `indicatorID` per request — multiple indicators are fetched in separate requests and combined.
- `/report/7` requires exactly one `countryID` per request — both AUS and USA are fetched in separate requests and combined.
- `/report/8` has no per-request filter — all indicators are returned together.
- `/report/9` has no per-request filter — all indicators are returned together.
- `/report/10` requires exactly one `species` per request — same approach.

---

## Terms of Use

All data is subject to [MLA's Market Report and Information Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/).

API support: **insights@mla.com.au**
