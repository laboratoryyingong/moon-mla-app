---
name: mla-add-report
description: Extend the project with a new MLA API endpoint (a new fetchers/fetch_reportN.py) or a new derived table under analysis/, following the repo's conventions and updating the CLI, docs and skills. Use when the user says add a new report, support /report/11, write a new fetcher, or wants a new analysis script alongside merge_reports.py.
---

# Adding a new report or analysis script

## A. New API endpoint → new fetcher

### 1. Probe first, code second
Use curl to learn the endpoint before writing Python:
```bash
curl -s 'https://api-mlastatistics.mla.com.au/report/N?fromDate=2025-01-01&toDate=2025-03-31&page=1' \
  -H 'Accept: application/json' -H 'User-Agent: MLA-Data-Fetcher/1.0 (contact: you@example.com)' | python3 -m json.tool | head -60
```
Establish: the row field names, `"total number rows"`, which filter parameters
exist and whether each accepts one value or many, whether a range crossing
31 December works, and whether `toDate` = today works. Test each with a real call.

### 2. Copy the closest existing fetcher
| Endpoint behaviour | Copy |
|---|---|
| Dates only, no filter | `fetchers/fetch_report8.py` |
| Optional filter, one value per request, no year limits | `fetchers/fetch_report3.py` |
| Required filter iterated per value, year splitting, yesterday cut-off | `fetchers/fetch_report10.py` (species) or `fetch_report5.py` (numeric IDs) |
| Extra optional dimension such as saleyardID | `fetchers/fetch_report6.py` |
| Keyed by year rather than dates | `fetchers/fetch_report2.py` |

Each fetcher is deliberately standalone (standard library only, no shared module).
Keep it that way.

### 3. Conventions the new file must keep
- Module docstring: what the report is, response fields, usage examples using
  `python fetchers/fetch_reportN.py ...`.
- Constants: `BASE_URL`, `ENDPOINT = "/report/N"`, `PAGE_SIZE = 100`,
  `REPO_ROOT = Path(__file__).resolve().parents[1]`,
  `DEFAULT_OUTPUT = REPO_ROOT / "data" / "raw" / "reportN_<snake_name>.csv"`,
  `DELAY_MIN/MAX/STEP/MULT` = 1.5 / 120 / 0.25 / 2.0, `VALID_<FILTER>` list or
  dict, `CSV_FIELDS` in output order.
- `build_url(...)`, `_make_request(url, contact_email)` with the standard headers
  and 30 s timeout, `_fetch_one(...)` with the AIMD retry loop on 429/502/503/504,
  `fetch_all(from_date, to_date, <filters>, contact_email, progress_callback=None)`,
  `save_csv(rows, output_path)` creating parent folders, `parse_args()`, `main()`.
- `progress_callback` stages: `category_start` (with `kind`, `category`,
  `category_index`, `total_categories`), `page_done`, `waiting`, `rate_limited`,
  `warning`, `complete`. `app.py` relies on these names.
- CLI flags: `--from/--to` (or `--from-year/--to-year`), `--<filter> VALUE ...`,
  `--list-<filter>`, `--output` defaulting to `str(DEFAULT_OUTPUT)`, `--email`.
  Validate filter values and exit 1 with a message pointing at `--list-<filter>`.
- If the endpoint rejects today, default `--to` to yesterday and clamp. If it
  rejects cross-year ranges, chunk per calendar year (see `_year_chunks` or the
  equivalent in report 10).

### 4. Register it
- `mla.py`: add one line to the `REPORTS` dict: `N: ("short-name", "Description", "Frequency")`.
  `mla fetch N`, `mla fetch short-name` and `fetch-all` then work without further changes.
- `README.md`: a row in "Tools Overview" and a full "Report N" section (description,
  Quick Start, Options table, valid values, Output Format, Examples); add any new
  quirk to "Known API limitations".
- `docs/CLI.md`: add the report to the `mla list` block and the filter table.
- Skills: create `.claude/skills/mla-api-reference/references/reportN.md` following
  the existing files, add it to the catalogue table and list in that skill's
  SKILL.md, and add a recipe row in `mla-fetch` and a file row in `mla-query`.

### 5. Verify
```bash
python3 fetchers/fetch_reportN.py --help
python3 fetchers/fetch_reportN.py --list-<filter>
python3 fetchers/fetch_reportN.py --from <recent> --to <recent>
mla fetch N --help && mla list | grep " N "
```
Check the CSV header equals `CSV_FIELDS` and the row count matches
"total number rows" from the probe.

## B. New derived table → new analysis script

- Put it in `analysis/<name>.py`, pandas allowed. Resolve inputs from
  `REPO_ROOT / "data" / "raw"` and outputs to `REPO_ROOT / "data" / "processed"`
  with `REPO_ROOT = Path(__file__).resolve().parents[1]`; create output folders.
- Give it `parse_args()` / `main()` like `analysis/merge_reports.py` so it can be
  wired into `mla.py` the same way `merge` is (add a `cmd_<name>` that calls
  `run_with_argv(module, "mla.py <name>", argv)` and register it in `PASSTHROUGH`
  plus a `sub.add_parser` line for `--help`).
- Document the output columns in README.md and add the file to the table in the
  `mla-query` skill.
