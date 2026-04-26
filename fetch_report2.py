#!/usr/bin/env python3
"""
MLA Statistics API - /report/2 Australian Herd and Flock Figures Fetcher

Annual herd and flock estimates at state × animal category level, sourced from
the Australian Bureau of Statistics (ABS) each financial year.

Data available from financial year 2015-16 to 2020-21 (approx).
The API accepts only one stateID and one category per request; this script
iterates over all (year × state × category) combinations automatically.

API Terms: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/
Contact:   insights@mla.com.au

Response fields:
    financial_year    — ABS financial year (e.g. "2020-21")
    region_desc       — state (NSW / SA / VIC / QLD / WA / TAS)
    subcategory_desc  — animal category (e.g. "Meat cattle", "Sheep and lambs")
    metric_desc       — metric within that category (e.g. "Total", "Calves less than 1 year")
    estimate_value    — head count estimate

Usage:
    python fetch_report2.py
    python fetch_report2.py --from-year 2015 --to-year 2021
    python fetch_report2.py --states NSW VIC QLD
    python fetch_report2.py --categories "Cattle" "Meat cattle" "Dairy cattle"
    python fetch_report2.py --list-states
    python fetch_report2.py --list-categories
    python fetch_report2.py --output my_herd.csv
"""

import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

import urllib.request
import urllib.parse
import urllib.error


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


BASE_URL  = "https://api-mlastatistics.mla.com.au"
ENDPOINT  = "/report/2"

DELAY_MIN  = 1.0
DELAY_MAX  = 120.0
DELAY_STEP = 0.25
DELAY_MULT = 2.0

VALID_STATES = ["NSW", "SA", "VIC", "QLD", "WA", "TAS"]

VALID_CATEGORIES = [
    "Cattle",
    "Dairy cattle",
    "Meat cattle",
    "Sheep and lambs",
    "Sheep and lambs - Lambs under 1 year",
    "Sheep and lambs - Breeding ewes 1 year or over",
    "Sheep and lambs - Marked lambs under 1 year",
]

CSV_FIELDS = ["financial_year", "region_desc", "subcategory_desc", "metric_desc", "estimate_value"]


def build_url(year: int, state: str, category: str | None) -> str:
    params = [
        ("year",    str(year)),
        ("stateID", state),
    ]
    if category is not None:
        params.append(("category", category))
    return f"{BASE_URL}{ENDPOINT}?{urllib.parse.urlencode(params)}"


def _make_request(url: str, contact_email: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"MLA-Data-Fetcher/1.0 (cattle/sheep producer internal use; contact: {contact_email})",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all(
    from_year: int,
    to_year: int,
    states: list[str],
    categories: list[str],
    contact_email: str,
    progress_callback=None,
) -> list[dict]:
    """
    Fetch /report/2 for every (year × state × category) combination.
    The API accepts only one stateID and one category per request — this
    function iterates over all combinations and concatenates the results.
    With no categories, fetches all data per (year × state) without a filter.

    progress_callback(info: dict) — optional hook for UI integration.
      info["stage"] is one of:
        "category_start" | "request_done" | "waiting" | "rate_limited" | "complete"
      When None, progress is printed to stdout (CLI mode).
    """
    years = list(range(from_year, to_year + 1))

    if categories:
        combinations = [(y, s, c) for y in years for s in states for c in categories]
    else:
        combinations = [(y, s, None) for y in years for s in states]

    total_requests = len(combinations)
    all_rows: list[dict] = []
    delay = DELAY_MIN
    fetch_start = time.time()

    for idx, (year, state, category) in enumerate(combinations):
        label = f"{year} / {state}" + (f" / {category}" if category else "")

        if progress_callback:
            progress_callback({
                "stage": "category_start",
                "category": label,
                "category_index": idx + 1,
                "total_categories": total_requests,
            })
        else:
            print(f"  [{idx + 1}/{total_requests}] {label} ...", end=" ", flush=True)

        url = build_url(year, state, category)
        t0 = time.time()

        while True:
            try:
                payload = _make_request(url, contact_email)
                delay = max(DELAY_MIN, delay - DELAY_STEP)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 502, 503, 504):
                    delay = min(DELAY_MAX, delay * DELAY_MULT)
                    if progress_callback:
                        progress_callback({"stage": "rate_limited", "code": e.code, "delay": delay})
                    else:
                        print(f"\n  ⚠  Rate limited (HTTP {e.code}) — backing off to {delay:.1f}s", flush=True)
                    time.sleep(delay)
                else:
                    if progress_callback is None:
                        print(f"✗  HTTP {e.code}", flush=True)
                    raise
            except urllib.error.URLError as e:
                if progress_callback is None:
                    print(f"✗  Network error: {e.reason}", flush=True)
                raise

        rows = payload.get("data", [])
        all_rows.extend(rows)
        elapsed = time.time() - t0
        total_elapsed = time.time() - fetch_start

        if progress_callback:
            progress_callback({
                "stage": "request_done",
                "category_index": idx + 1,
                "total_categories": total_requests,
                "rows_this_request": len(rows),
                "rows_done": len(all_rows),
                "elapsed": total_elapsed,
                "request_time": elapsed,
                "delay": delay,
            })
        else:
            print(f"{len(rows)} rows  ({elapsed:.1f}s)", flush=True)

        if idx < total_requests - 1:
            if progress_callback:
                progress_callback({"stage": "waiting", "next": combinations[idx + 1], "wait_time": delay})
            else:
                print(f"  Waiting {delay:.1f}s ...", flush=True)
            time.sleep(delay)

    total_elapsed = time.time() - fetch_start
    rows_per_sec = len(all_rows) / total_elapsed if total_elapsed > 0 else 0

    if progress_callback:
        progress_callback({
            "stage": "complete",
            "rows_done": len(all_rows),
            "elapsed": total_elapsed,
            "rows_per_sec": rows_per_sec,
            "requests": total_requests,
        })
    else:
        print(
            f"\n  Fetch complete: {len(all_rows)} rows in {_fmt_duration(total_elapsed)}"
            f"  ({rows_per_sec:.1f} rows/s,  {total_requests} request(s))",
            flush=True,
        )

    return all_rows


def save_csv(rows: list[dict], output_path: str) -> None:
    if not rows:
        print("No data to save.")
        return

    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {path.resolve()}")


def parse_args() -> argparse.Namespace:
    current_year = date.today().year

    parser = argparse.ArgumentParser(
        description="Fetch MLA /report/2 Australian Herd and Flock Figures"
    )
    parser.add_argument("--from-year", dest="from_year", type=int, default=2015,
                        metavar="YEAR", help="Start year (default: 2015)")
    parser.add_argument("--to-year", dest="to_year", type=int, default=current_year,
                        metavar="YEAR", help=f"End year (default: {current_year})")
    parser.add_argument("--states", nargs="+", choices=VALID_STATES, default=VALID_STATES,
                        metavar="STATE",
                        help="Filter by state (default: all). Choices: " + " ".join(VALID_STATES))
    parser.add_argument("--categories", nargs="+", default=[],
                        metavar="CATEGORY",
                        help="Filter by one or more categories (default: all). "
                             "Use --list-categories to see valid values.")
    parser.add_argument("--output", default="report2_herd_flock.csv",
                        help="Output CSV file (default: report2_herd_flock.csv)")
    parser.add_argument("--list-states", action="store_true",
                        help="Print valid state IDs and exit")
    parser.add_argument("--list-categories", action="store_true",
                        help="Print valid category names and exit")
    parser.add_argument("--email", default="moon.zhou@thomasfoods.com",
                        metavar="EMAIL",
                        help="Your contact email, included in the User-Agent header")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_states:
        print("Valid stateIDs for /report/2:")
        for s in VALID_STATES:
            print(f"  {s}")
        return

    if args.list_categories:
        print("Valid categories for /report/2:")
        for c in VALID_CATEGORIES:
            print(f"  {c}")
        return

    if args.categories:
        invalid = [c for c in args.categories if c not in VALID_CATEGORIES]
        if invalid:
            print(f"Unknown categories: {invalid}", file=sys.stderr)
            print("Run with --list-categories to see valid values.", file=sys.stderr)
            sys.exit(1)

    run_start = time.time()

    n_years = args.to_year - args.from_year + 1
    n_cats = len(args.categories) if args.categories else 1
    total_requests = n_years * len(args.states) * n_cats
    cat_label = ", ".join(args.categories) if args.categories else "all categories (no filter)"

    print("=" * 60)
    print("MLA Statistics API — /report/2 Australian Herd and Flock")
    print("=" * 60)
    print(f"  Years      : {args.from_year} → {args.to_year}")
    print(f"  States     : {', '.join(args.states)}")
    print(f"  Categories : {cat_label}")
    print(f"  Output     : {args.output}")
    print(f"  Contact    : {args.email}")
    print(f"  Started at : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print(f"Fetching {total_requests} requests ({n_years} years × {len(args.states)} states × {n_cats} categories) ...", flush=True)

    try:
        rows = fetch_all(args.from_year, args.to_year, args.states, args.categories, args.email)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
        print(f"\nFailed to fetch data: {e}", file=sys.stderr)
        sys.exit(1)

    print("-" * 60)
    print("Writing CSV ...", flush=True)
    save_csv(rows, args.output)

    total_elapsed = time.time() - run_start
    print(f"Total runtime: {_fmt_duration(total_elapsed)}")
    print("=" * 60)
    print("\nDisclaimer: All use of MLA data is subject to MLA's Market Report and")
    print("Information Terms of Use: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/")


if __name__ == "__main__":
    main()
