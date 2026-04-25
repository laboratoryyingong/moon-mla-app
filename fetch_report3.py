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


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


def _progress_bar(done: int, total: int, width: int = 25) -> str:
    if total <= 0:
        return ""
    filled = int(width * done / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = 100 * done / total
    return f"[{bar}] {pct:.0f}%"

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


def fetch_all(
    from_date: str,
    to_date: str,
    categories: list[str],
    contact_email: str,
    progress_callback=None,
) -> list[dict]:
    """
    Paginate through all results with adaptive rate control (AIMD).
    The API only accepts one category per request; when multiple categories are
    selected this function loops through them and concatenates the results.

    progress_callback(info: dict) — optional hook for UI integration.
      info["stage"] is one of:
        "category_start" | "page_done" | "waiting" | "rate_limited" | "complete"
      When None, progress is printed to stdout (CLI mode).
    """
    # API limitation: only one category per request — iterate when multiple given
    if len(categories) > 1:
        combined: list[dict] = []
        for idx, cat in enumerate(categories):
            if progress_callback:
                progress_callback({
                    "stage": "category_start",
                    "category": cat,
                    "category_index": idx + 1,
                    "total_categories": len(categories),
                })
            else:
                print(f"\n── Category {idx + 1}/{len(categories)}: {cat}", flush=True)
            combined.extend(fetch_all(from_date, to_date, [cat], contact_email, progress_callback))
        return combined

    all_rows = []
    page = 1
    delay = DELAY_MIN
    total = 0
    fetch_start = time.time()
    page_times: list[float] = []

    if progress_callback is None:
        print("  Fetching page 1 ...", flush=True)

    while True:
        url = build_url(from_date, to_date, categories, page)
        t0 = time.time()

        while True:  # inner retry loop for throttle responses
            try:
                payload = _make_request(url, contact_email)
                delay = max(DELAY_MIN, delay - DELAY_STEP)
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    delay = min(DELAY_MAX, delay * DELAY_MULT)
                    if progress_callback:
                        progress_callback({"stage": "rate_limited", "code": e.code, "delay": delay})
                    else:
                        print(f"  ⚠  Rate limited (HTTP {e.code}) — backing off to {delay:.1f}s", flush=True)
                    time.sleep(delay)
                else:
                    if progress_callback is None:
                        print(f"  ✗  HTTP {e.code} error", file=sys.stderr)
                    raise
            except urllib.error.URLError as e:
                if progress_callback is None:
                    print(f"  ✗  Network error: {e.reason}", file=sys.stderr)
                raise

        page_elapsed = time.time() - t0
        page_times.append(page_elapsed)

        rows = payload.get("data", [])
        total = payload.get("total number rows", 0)
        all_rows.extend(rows)

        total_pages = max(page, (total + PAGE_SIZE - 1) // PAGE_SIZE) if total else page
        elapsed = time.time() - fetch_start
        avg_page_time = sum(page_times) / len(page_times)
        remaining_pages = total_pages - page
        eta_sec = remaining_pages * (avg_page_time + delay) if remaining_pages > 0 else 0

        if progress_callback:
            progress_callback({
                "stage": "page_done",
                "page": page,
                "total_pages": total_pages,
                "rows_done": len(all_rows),
                "total_rows": total,
                "elapsed": elapsed,
                "eta": eta_sec,
                "delay": delay,
                "page_time": page_elapsed,
            })
        else:
            bar = _progress_bar(len(all_rows), total) if total else ""
            eta_str = f"  ETA {_fmt_duration(eta_sec)}" if remaining_pages > 0 else "  done"
            print(
                f"  Page {page}/{total_pages}  {bar}"
                f"  {len(all_rows)}/{total} rows"
                f"  {page_elapsed:.1f}s/page  delay={delay:.1f}s"
                f"  elapsed={_fmt_duration(elapsed)}{eta_str}",
                flush=True,
            )

        if len(rows) < PAGE_SIZE or len(all_rows) >= total:
            break

        page += 1
        if progress_callback:
            progress_callback({"stage": "waiting", "page": page, "wait_time": delay})
        else:
            print(f"  Waiting {delay:.1f}s before page {page} ...", flush=True)
        time.sleep(delay)

    total_elapsed = time.time() - fetch_start
    rows_per_sec = len(all_rows) / total_elapsed if total_elapsed > 0 else 0

    if progress_callback:
        progress_callback({
            "stage": "complete",
            "rows_done": len(all_rows),
            "elapsed": total_elapsed,
            "rows_per_sec": rows_per_sec,
            "pages": page,
        })
    else:
        print(
            f"\n  Fetch complete: {len(all_rows)} rows in {_fmt_duration(total_elapsed)}"
            f"  ({rows_per_sec:.1f} rows/s,  {page} page(s))",
            flush=True,
        )
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

    run_start = time.time()

    print("=" * 60)
    print("MLA Statistics API — /report/3 Australian Slaughter and Production")
    print("=" * 60)
    print(f"  Date range : {args.from_date} → {args.to_date}")
    cat_display = ", ".join(args.category) if args.category else "all categories"
    print(f"  Categories : {cat_display}")
    print(f"  Output     : {args.output}")
    print(f"  Contact    : {args.email}")
    print(f"  Started at : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print("Fetching data ...", flush=True)

    try:
        rows = fetch_all(args.from_date, args.to_date, args.category, args.email)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as e:
        print(f"\nFailed to fetch data: {e}", file=sys.stderr)
        sys.exit(1)

    print("-" * 60)
    print(f"Writing CSV ...", flush=True)
    save_csv(rows, args.output)

    total_elapsed = time.time() - run_start
    print(f"Total runtime: {_fmt_duration(total_elapsed)}")
    print("=" * 60)
    print("\nDisclaimer: All use of MLA data is subject to MLA's Market Report and")
    print("Information Terms of Use: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/")


if __name__ == "__main__":
    main()
