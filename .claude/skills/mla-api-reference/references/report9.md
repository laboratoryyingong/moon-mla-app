# /report/9 - US Imported Meat Prices

Weekly US import prices for manufacturing beef and selected cuts from Steiner
Consulting, in US cents per pound. The 90CL series are the benchmark for
Australian lean trim exports. Short name `us-imports`. Fetcher
`fetchers/fetch_report9.py`. Default output `data/raw/report9_us_imported_meat_prices.csv`.

## Query parameters

`fromDate`, `toDate` (`YYYY-MM-DD`, today accepted, cross-year fine) and `page`.
No filters. Defaults: `--from` 1 January last year, `--to` today.

## Series in the data (all `US c/lb`)

75CL Trim; 80CL Trim; 85CL Trim; 85CL Cow Fores; 90CL Boneless Beef, NZ;
90CL Boneless Beef, NZ/Australia; 90CL Shank; 95CL Bull Meat, East Coast;
95CL Bull Meat, West Coast; Cap Off Insides; Steer Flats; Steer Knuckles.

`NNCL` = chemical lean percentage (lean meat share of the trim).

## CSV columns

`indicator_name, indicator_date, indicator_units, indicator_value`

## Sample row

```
indicator_name,indicator_date,indicator_units,indicator_value
"90CL Boneless Beef, NZ/Australia",2025-01-03,US c/lb,297.50
```
