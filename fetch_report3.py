#!/usr/bin/env python3
"""
MLA Statistics API - /report/3 Australian Slaughter and Production Fetcher

API Terms: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/
Contact:   insights@mla.com.au

Usage:
    python fetch_report3.py
    python fetch_report3.py --from 2020-01-01 --to 2024-12-31
    python fetch_report3.py --from 2023-01-01 --to 2023-12-31 --category "Cattle (Excl. Calves)" Lambs
    python fetch_report3.py --output my_data.csv
"""

import argparse
import csv
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://api-mlastatistics.mla.com.au"
ENDPOINT = "/report/3"
PAGE_SIZE = 100   # API returns max 100 rows per page

# Adaptive rate limiter constants (AIMD — same principle as TCP congestion control)
DELAY_MIN  = 1.5   # floor: fastest we'll ever go (seconds)
DELAY_MAX  = 120.0 # ceiling: slowest we'll go after repeated throttling
DELAY_STEP = 0.25  # additive decrease per successful request (slow recovery)
DELAY_MULT = 2.0   # multiplicative increase on 429 (fast back-off)

VALID_CATEGORIES = [
    "Total Red Meat",
    "Calves",
    "Cattle (Excl. Calves)",
    "Cows And Heifers",
    "Bulls, Bullocks And Steers",
    "Sheep",
    "Lambs",
    "Chickens",
    "Pigs",
]


def build_url(from_date: str, to_date: str, categories: list[str], page: int) -> str:
    params = [
        ("fromDate", from_date),
        ("toDate", to_date),
        ("page", str(page)),
    ]
    for cat in categories:
        params.append(("category", cat))
    return f"{BASE_URL}{ENDPOINT}?{urllib.parse.urlencode(params)}"


def _make_request(url: str, contact_email: str) -> dict:
    """Single HTTP GET — raises HTTPError on non-2xx, including 429."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"MLA-Data-Fetcher/1.0 (cattle/sheep producer internal use; contact: {contact_email})",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_all(from_date: str, to_date: str, categories: list[str], contact_email: str) -> list[dict]:
    """
    Paginate through all results with adaptive rate control (AIMD):
      - Each successful request nudges the delay down toward DELAY_MIN.
      - A 429 or 503 doubles the delay and retries — no crash, no fixed wait.
    """
    all_rows = []
    page = 1
    delay = DELAY_MIN  # current inter-request delay, adjusted dynamically

    while True:
        url = build_url(from_date, to_date, categories, page)

        while True:  # inner retry loop for throttle responses
            try:
                payload = _make_request(url, contact_email)
                # Success — slowly recover toward the minimum delay
                delay = max(DELAY_MIN, delay - DELAY_STEP)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    delay = min(DELAY_MAX, delay * DELAY_MULT)
                    print(f"  Rate limited (HTTP {e.code}) — slowing down, next delay: {delay:.1f}s")
                    time.sleep(delay)
                else:
                    print(f"  HTTP {e.code} error", file=sys.stderr)
                    raise
            except urllib.error.URLError as e:
                print(f"  Network error: {e.reason}", file=sys.stderr)
                raise

        rows = payload.get("data", [])
        total = payload.get("total number rows", 0)
        all_rows.extend(rows)

        print(f"  Page {page}: {len(rows)} rows (total: {len(all_rows)}/{total}, delay: {delay:.1f}s)")

        if len(rows) < PAGE_SIZE or len(all_rows) >= total:
            break

        page += 1
        time.sleep(delay)

    return all_rows


def save_csv(rows: list[dict], output_path: str) -> None:
    if not rows:
        print("No data to save.")
        return

    fieldnames = ["report_date", "report_type", "category", "location_id", "unit_of_measure", "value_amt"]
    path = Path(output_path)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {path.resolve()}")


def parse_args() -> argparse.Namespace:
    today = date.today()
    default_to = today.isoformat()
    default_from = date(today.year - 5, 1, 1).isoformat()

    parser = argparse.ArgumentParser(
        description="Fetch MLA /report/3 Australian Slaughter and Production data"
    )
    parser.add_argument("--from", dest="from_date", default=default_from,
                        metavar="YYYY-MM-DD", help=f"Start date (default: {default_from})")
    parser.add_argument("--to", dest="to_date", default=default_to,
                        metavar="YYYY-MM-DD", help=f"End date (default: {default_to})")
    parser.add_argument("--category", nargs="+", choices=VALID_CATEGORIES, default=[],
                        metavar="CATEGORY",
                        help="Filter by category (default: all). Choices:\n" +
                             "\n".join(f"  {c}" for c in VALID_CATEGORIES))
    parser.add_argument("--output", default="report3_slaughter_production.csv",
                        help="Output CSV file (default: report3_slaughter_production.csv)")
    parser.add_argument("--list-categories", action="store_true",
                        help="Print valid category names and exit")
    parser.add_argument("--email", default="moon.zhou@thomasfoods.com",
                        metavar="EMAIL",
                        help="Your contact email, included in the User-Agent header (default: moon.zhou@thomasfoods.com)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_categories:
        print("Valid categories for /report/3:")
        for c in VALID_CATEGORIES:
            print(f"  {c}")
        return

    print("MLA Statistics API — /report/3 Australian Slaughter and Production")
    print(f"  Date range : {args.from_date} → {args.to_date}")
    print(f"  Categories : {args.category if args.category else 'all'}")
    print(f"  Output     : {args.output}")
    print()

    try:
        rows = fetch_all(args.from_date, args.to_date, args.category, args.email)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
        print(f"\nFailed to fetch data: {e}", file=sys.stderr)
        sys.exit(1)

    save_csv(rows, args.output)

    print("\nDisclaimer: All use of MLA data is subject to MLA's Market Report and")
    print("Information Terms of Use: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/")


if __name__ == "__main__":
    main()
