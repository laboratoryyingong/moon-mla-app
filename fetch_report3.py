#!/usr/bin/env python3
"""
MLA Statistics API - /report/3 Australian Slaughter and Production Fetcher

Quarterly slaughter and production figures at animal category × location level,
sourced from the Australian Bureau of Statistics (ABS).  Data available from
March 2000 to present.

API Terms: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/
Contact:   insights@mla.com.au

Response fields:
    report_date       — quarter end date (YYYY-MM-01, quarterly)
    report_type       — "Slaughter" or "Production"
    category          — animal category
    location_id       — state or "Australia" (national total)
    unit_of_measure   — "000" (thousands of head) or "Tonnes"
    value_amt         — the measured value

Usage:
    python fetch_report3.py
    python fetch_report3.py --from 2022-01-01 --to 2024-12-31
    python fetch_report3.py --categories Cattle Lambs Sheep
    python fetch_report3.py --list-categories
    python fetch_report3.py --output my_data.csv
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


def _progress_bar(done: int, total: int, width: int = 25) -> str:
    if total <= 0:
        return ""
    filled = int(width * done / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = 100 * done / total
    return f"[{bar}] {pct:.0f}%"


BASE_URL  = "https://api-mlastatistics.mla.com.au"
ENDPOINT  = "/report/3"
PAGE_SIZE = 100

DELAY_MIN  = 1.5
DELAY_MAX  = 120.0
DELAY_STEP = 0.25
DELAY_MULT = 2.0

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

CSV_FIELDS = ["report_date", "report_type", "category", "location_id", "unit_of_measure", "value_amt"]


def build_url(from_date: str, to_date: str, category: str | None, page: int) -> str:
    params = [
        ("fromDate", from_date),
        ("toDate",   to_date),
        ("page",     str(page)),
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


def _fetch_one(
    from_date: str,
    to_date: str,
    category: str | None,
    contact_email: str,
    progress_callback,
    label: str,
) -> list[dict]:
    """Paginate through results for a single category (or all if category is None)."""
    all_rows = []
    page = 1
    delay = DELAY_MIN
    fetch_start = time.time()
    page_times: list[float] = []

    if progress_callback is None:
        print(f"  Fetching {label} ...", flush=True)

    while True:
        url = build_url(from_date, to_date, category, page)
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

    return all_rows


def fetch_all(
    from_date: str,
    to_date: str,
    categories: list[str],
    contact_email: str,
    progress_callback=None,
) -> list[dict]:
    """
    Paginate through all /report/3 results with adaptive rate control (AIMD).
    The API only accepts one category per request; when multiple categories are
    selected this function loops through them and concatenates the results.
    With no categories specified, a single unfilitered request fetches everything.

    progress_callback(info: dict) — optional hook for UI integration.
      info["stage"] is one of:
        "category_start" | "page_done" | "waiting" | "rate_limited" | "complete"
      When None, progress is printed to stdout (CLI mode).
    """
    fetch_start = time.time()

    if len(categories) > 1:
        combined: list[dict] = []
        for idx, cat in enumerate(categories):
            if progress_callback:
                progress_callback({
                    "stage": "category_start",
                    "kind": "category",
                    "category": cat,
                    "category_index": idx + 1,
                    "total_categories": len(categories),
                })
            else:
                print(f"\n── Category {idx + 1}/{len(categories)}: {cat}", flush=True)
            combined.extend(_fetch_one(from_date, to_date, cat, contact_email, progress_callback, cat))
        all_rows = combined
    elif len(categories) == 1:
        if progress_callback:
            progress_callback({
                "stage": "category_start",
                "kind": "category",
                "category": categories[0],
                "category_index": 1,
                "total_categories": 1,
            })
        all_rows = _fetch_one(from_date, to_date, categories[0], contact_email, progress_callback, categories[0])
    else:
        # No filter — fetch all categories in one stream
        all_rows = _fetch_one(from_date, to_date, None, contact_email, progress_callback, "all categories")

    total_elapsed = time.time() - fetch_start
    rows_per_sec = len(all_rows) / total_elapsed if total_elapsed > 0 else 0

    if progress_callback:
        progress_callback({
            "stage": "complete",
            "rows_done": len(all_rows),
            "elapsed": total_elapsed,
            "rows_per_sec": rows_per_sec,
        })
    else:
        print(
            f"\n  Fetch complete: {len(all_rows)} rows in {_fmt_duration(total_elapsed)}"
            f"  ({rows_per_sec:.1f} rows/s)",
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
    today = date.today()
    default_to   = today.isoformat()
    default_from = date(today.year - 1, 1, 1).isoformat()

    parser = argparse.ArgumentParser(
        description="Fetch MLA /report/3 Australian Slaughter and Production data"
    )
    parser.add_argument("--from", dest="from_date", default=default_from,
                        metavar="YYYY-MM-DD", help=f"Start date (default: {default_from})")
    parser.add_argument("--to", dest="to_date", default=default_to,
                        metavar="YYYY-MM-DD", help=f"End date (default: {default_to})")
    parser.add_argument("--categories", nargs="+", default=[],
                        metavar="CATEGORY",
                        help="Filter by one or more categories (default: all). "
                             "Use --list-categories to see valid values.")
    parser.add_argument("--output", default="report3_slaughter_production.csv",
                        help="Output CSV file (default: report3_slaughter_production.csv)")
    parser.add_argument("--list-categories", action="store_true",
                        help="Print valid category names and exit")
    parser.add_argument("--email", default="moon.zhou@thomasfoods.com",
                        metavar="EMAIL",
                        help="Your contact email, included in the User-Agent header")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_categories:
        print("Valid categories for /report/3:")
        for c in VALID_CATEGORIES:
            print(f"  {c}")
        return

    # Validate categories
    if args.categories:
        invalid = [c for c in args.categories if c not in VALID_CATEGORIES]
        if invalid:
            print(f"Unknown categories: {invalid}", file=sys.stderr)
            print("Run with --list-categories to see valid values.", file=sys.stderr)
            sys.exit(1)

    run_start = time.time()

    print("=" * 60)
    print("MLA Statistics API — /report/3 Australian Slaughter & Production")
    print("=" * 60)
    print(f"  Date range : {args.from_date} → {args.to_date}")
    cat_display = ", ".join(args.categories) if args.categories else "all categories"
    print(f"  Categories : {cat_display}")
    print(f"  Output     : {args.output}")
    print(f"  Contact    : {args.email}")
    print(f"  Started at : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print("Fetching data ...", flush=True)

    try:
        rows = fetch_all(args.from_date, args.to_date, args.categories, args.email)
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
