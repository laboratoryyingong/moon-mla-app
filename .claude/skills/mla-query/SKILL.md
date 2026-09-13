---
name: mla-query
description: Answer analytical questions from the MLA data already downloaded under data/raw and data/processed using pandas, without calling the API - cattle, lamb and sheep prices, slaughter volumes, exports, herd numbers, saleyard yardings, US prices, trends, weekly or monthly averages and year-on-year change. Use for any question like "what was the trade lamb price last month", "how many cattle were slaughtered in Queensland", "beef exports to Japan this year", or anything about merged_weekly.csv.
---

# Answering questions from the MLA data on disk

Work from the repository root with pandas. Do **not** call the API from this
skill; if the data is missing or stale, say so and point to the `mla-refresh`
or `mla-fetch` skill.

## Step 1: check freshness first

Read the max date of the file you are about to use and tell the user if it is older
than the period they asked about. Files and their date columns:

| Question about | File | Date column | Key columns |
|---|---|---|---|
| Beef export volume by country | `data/raw/report1_red_meat_exports.csv` | `result_date` (month) | `country_desc`, `weight_amt` (kg) |
| Herd / flock size by state | `data/raw/report2_herd_flock.csv` | `financial_year` (`2018-19`) | `region_desc`, `subcategory_desc`, `metric_desc`, `estimate_value` |
| ABS quarterly slaughter or production | `data/raw/report3_slaughter_production.csv` | `report_date` (quarter) | `report_type`, `category`, `location_id`, `unit_of_measure`, `value_amt` |
| Saleyard yardings | `data/raw/report4_saleyard_yardings.csv` | `result_date` | `category_desc`, `state_id`, `saleyard_id`, `tranx_type_id`, `head_count` |
| National price indicators | `data/raw/report5_livestock_indicators.csv` | `calendar_date` | `indicator_id`, `indicator_desc`, `indicator_units`, `indicator_value`, `head_count` |
| Prices at one saleyard | `data/raw/report6_saleyard_indicators.csv` | `calendar_date` | as report 5 plus `saleyard_id` |
| AUS vs USA cattle prices (AUD) | `data/raw/report7_global_cattle_prices.csv` | `indicator_date` | `country_code`, `indicator_desc`, `indicator_value` |
| US domestic cattle prices | `data/raw/report8_us_cattle_prices.csv` | `indicator_date` | `indicator_name`, `indicator_value` (US c/lb) |
| US imported beef (90CL etc.) | `data/raw/report9_us_imported_meat_prices.csv` | `indicator_date` | `indicator_name`, `indicator_value` (US c/lb) |
| Weekly slaughter by state & species | `data/raw/report10_nlrs_slaughter.csv` | `result_date` (Friday) | `contributor_state_id`, `species_id`, `slaughter_count` |
| Prices and slaughter together, weekly | `data/processed/merged_weekly.csv` | `week_ending` (Friday) | see below |

Column meanings and valid values are in the `mla-api-reference` skill.

## Units and vocabulary

- Indicator prices are **c/kg cwt** (carcase weight) or **c/kg lwt** (live weight);
  divide by 100 for $/kg. Indicators 16 and 18 ("Online ...") are **$/head**.
- US series are **US c/lb**. Convert to AUD c/kg only if the user asks, and say
  which exchange rate you used.
- Report 3 `unit_of_measure`: `000` = thousand head (Slaughter rows), `Tonnes`
  (Production rows). `location_id = Australia` is the national total; do not add
  it to the states.
- Report 10 `slaughter_count` is head per week; zero rows are real data.
- `head_count` in reports 5/6 is the sample size behind the price, not slaughter.

## Species → indicator mapping (used by merged_weekly.csv)

| species_group | Indicator IDs |
|---|---|
| Cattle | 1, 2, 3, 4, 5, 12, 13, 14, 15, 17 |
| Lambs | 6, 7, 8, 9, 10, 16 |
| Sheep (mutton) | 11, 18 |
| Calves, Pigs, Goat, Deer | slaughter columns only |

`merged_weekly.csv` columns: `week_ending`, `species_group`, `national_slaughter`,
`slaughter_NSW … slaughter_WA`, then `ind_<id> <name> (<units>) price_avg` and
`ind_<id> <name> (<units>) heads_avg` for IDs 1-18. Column names embed the
description, so select them with `df.filter(like="ind_4 ")` or
`[c for c in df.columns if c.startswith("ind_4 ")]`. Legend:
`data/processed/indicator_lookup.csv`.

## Loading pattern

```python
import pandas as pd
df = pd.read_csv("data/raw/report5_livestock_indicators.csv", parse_dates=["calendar_date"])
```
`merged_weekly.csv` may have been re-saved from Excel with `D/M/YYYY` dates; use
`pd.to_datetime(df["week_ending"], dayfirst=True, format="mixed")`.
Filter with `df[df.calendar_date.between("2025-01-01", "2025-06-30")]`; resample
with `df.set_index("calendar_date").resample("W-FRI")["indicator_value"].mean()`
(weekly) or `"MS"` (monthly). Year-on-year: `s.pct_change(52)` on a weekly
series or `s.pct_change(12)` on monthly.

## Worked examples

**1. Weekly national cattle slaughter vs the National Heavy Steer Indicator**
```python
m = pd.read_csv("data/processed/merged_weekly.csv")
m["week_ending"] = pd.to_datetime(m["week_ending"], dayfirst=True, format="mixed")
c = m[m.species_group == "Cattle"].set_index("week_ending").sort_index()
price_col = [x for x in c.columns if x.startswith("ind_4 ") and x.endswith("price_avg")][0]
out = c[["national_slaughter", price_col]].rename(columns={price_col: "heavy_steer_c_kg_lwt"})
print(out.tail(8)); print(out.corr())
```

**2. Monthly beef exports to Japan, with year-on-year change**
```python
e = pd.read_csv("data/raw/report1_red_meat_exports.csv", parse_dates=["result_date"])
jp = e[e.country_desc == "Japan"].set_index("result_date")["weight_amt"].sort_index() / 1000  # tonnes
print(pd.DataFrame({"tonnes": jp, "yoy_%": jp.pct_change(12) * 100}).tail(12).round(1))
```

**3. US imported 90CL price trend (monthly average)**
```python
u = pd.read_csv("data/raw/report9_us_imported_meat_prices.csv", parse_dates=["indicator_date"])
s = u[u.indicator_name == "90CL Boneless Beef, NZ/Australia"].set_index("indicator_date")["indicator_value"]
print(s.resample("MS").mean().round(1).tail(12))   # US c/lb
```

## Presenting the answer

Lead with the number and its unit and period, then the source file and its last
date. Put series in a small table; keep prose free of long number lists. If the
question needs a date range beyond the file's coverage, say exactly what is
missing and give the `mla fetch` or `mla-refresh` command that would fill it.
