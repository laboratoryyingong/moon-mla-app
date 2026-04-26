#!/usr/bin/env python3
"""
MLA Statistics API - /report/6 Australian Livestock Indicators (By Saleyard) Fetcher

NLRS Livestock Indicators broken down at the saleyard level. Data is collected
by the National Livestock Reporting Service on a daily basis and updated once
per day at 12am AEST.

Unlike /report/5 (national indicators), this endpoint provides the per-saleyard
contribution to each indicator, with the same 18 indicator IDs.

API Terms: https://www.mla.com.au/general/Terms-and-conditions/data-and-information/
Contact:   insights@mla.com.au

Response fields:
    calendar_date    — date (YYYY-MM-DD), daily
    species_id       — Cattle | Sheep
    saleyard_id      — saleyard code (e.g. "WAG", "WOD")
    indicator_id     — numeric indicator ID (same set as /report/5)
    indicator_desc   — full indicator name
    indicator_units  — c/kg cwt | c/kg lwt | $/head
    head_count       — number of animals at that saleyard
    indicator_value  — price / value for that day at that saleyard

Valid indicatorIDs (same as /report/5):
     1  Cattle  Western Young Cattle Indicator              c/kg cwt
     2  Cattle  National Restocker Yearling Steer Indicator c/kg lwt
     3  Cattle  National Feeder Steer Indicator             c/kg lwt
     4  Cattle  National Heavy Steer Indicator              c/kg lwt
     5  Cattle  National Heavy Dairy Cow Indicator          c/kg lwt
     6  Sheep   National Light Lamb Indicator               c/kg cwt
     7  Sheep   National Trade Lamb Indicator               c/kg cwt
     8  Sheep   National Heavy Lamb Indicator               c/kg cwt
     9  Sheep   National Merino Lamb Indicator              c/kg cwt
    10  Sheep   National Restocker Lamb Indicator           c/kg cwt
    11  Sheep   National Mutton Indicator                   c/kg cwt
    12  Cattle  National Restocker Yearling Heifer Indicator c/kg lwt
    13  Cattle  National Processor Cow Indicator            c/kg lwt
    14  Cattle  National Young Cattle Indicator             c/kg lwt
    15  Cattle  Online Young Cattle Indicator               c/kg lwt
    16  Sheep   Online Lamb Indicator                       $/head
    17  Cattle  National Feeder Heifer Indicator            c/kg lwt
    18  Sheep   Online Sheep Indicator                      $/head

Usage:
    python fetch_report6.py
    python fetch_report6.py --from 2024-01-01 --to 2024-12-31
    python fetch_report6.py --indicators 1 2 3
    python fetch_report6.py --saleyard WAG
    python fetch_report6.py --output my_saleyard_indicators.csv
    python fetch_report6.py --list-indicators
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


def _year_chunks(from_date: str, to_date: str) -> list[tuple[str, str]]:
    """Split date range into per-calendar-year chunks (API returns HTTP 500 on cross-year queries)."""
    start = date.fromisoformat(from_date)
    end   = date.fromisoformat(to_date)
    chunks = []
    cur = start
    while cur <= end:
        year_end = date(cur.year, 12, 31)
        chunk_end = min(year_end, end)
        chunks.append((cur.isoformat(), chunk_end.isoformat()))
        cur = date(cur.year + 1, 1, 1)
    return chunks


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
ENDPOINT  = "/report/6"
PAGE_SIZE = 100

DELAY_MIN  = 1.5
DELAY_MAX  = 120.0
DELAY_STEP = 0.25
DELAY_MULT = 2.0

VALID_INDICATORS = {
    1:  ("Cattle", "Western Young Cattle Indicator",               "c/kg cwt"),
    2:  ("Cattle", "National Restocker Yearling Steer Indicator",  "c/kg lwt"),
    3:  ("Cattle", "National Feeder Steer Indicator",              "c/kg lwt"),
    4:  ("Cattle", "National Heavy Steer Indicator",               "c/kg lwt"),
    5:  ("Cattle", "National Heavy Dairy Cow Indicator",           "c/kg lwt"),
    6:  ("Sheep",  "National Light Lamb Indicator",                "c/kg cwt"),
    7:  ("Sheep",  "National Trade Lamb Indicator",                "c/kg cwt"),
    8:  ("Sheep",  "National Heavy Lamb Indicator",                "c/kg cwt"),
    9:  ("Sheep",  "National Merino Lamb Indicator",               "c/kg cwt"),
    10: ("Sheep",  "National Restocker Lamb Indicator",            "c/kg cwt"),
    11: ("Sheep",  "National Mutton Indicator",                    "c/kg cwt"),
    12: ("Cattle", "National Restocker Yearling Heifer Indicator", "c/kg lwt"),
    13: ("Cattle", "National Processor Cow Indicator",             "c/kg lwt"),
    14: ("Cattle", "National Young Cattle Indicator",              "c/kg lwt"),
    15: ("Cattle", "Online Young Cattle Indicator",                "c/kg lwt"),
    16: ("Sheep",  "Online Lamb Indicator",                        "$/head"),
    17: ("Cattle", "National Feeder Heifer Indicator",             "c/kg lwt"),
    18: ("Sheep",  "Online Sheep Indicator",                       "$/head"),
}

CSV_FIELDS = [
    "calendar_date",
    "species_id",
    "saleyard_id",
    "indicator_id",
    "indicator_desc",
    "indicator_units",
    "head_count",
    "indicator_value",
]


def build_url(from_date: str, to_date: str, indicator_id: int, page: int, saleyard_id: str | None) -> str:
    params = [
        ("fromDate",    from_date),
        ("toDate",      to_date),
        ("indicatorID", str(indicator_id)),
        ("page",        str(page)),
    ]
    if saleyard_id:
        params.append(("saleyardID", saleyard_id))
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
    indicator_id: int,
    saleyard_id: str | None,
    contact_email: str,
    progress_callback,
) -> list[dict]:
    """Paginate through all results for a single indicator."""
    all_rows = []
    page = 1
    delay = DELAY_MIN
    fetch_start = time.time()
    page_times: list[float] = []

    if progress_callback is None:
        desc = VALID_INDICATORS.get(indicator_id, ("", f"Indicator {indicator_id}", ""))[1]
        print(f"  Fetching [{indicator_id}] {desc} ...", flush=True)

    while True:
        url = build_url(from_date, to_date, indicator_id, page, saleyard_id)
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
    indicator_ids: list[int],
    saleyard_id: str | None,
    contact_email: str,
    progress_callback=None,
) -> list[dict]:
    """
    Paginate through all /report/6 results with adaptive rate control (AIMD).
    Iterates over indicator_ids one at a time (API only accepts one indicatorID
    per request; multiple values silently return only the last one).
    Cross-year date ranges are split by calendar year automatically (the API
    returns HTTP 500 for cross-year queries).

    progress_callback(info: dict) — optional hook for UI integration.
      info["stage"] is one of:
        "category_start" | "page_done" | "waiting" | "rate_limited" | "complete"
      When None, progress is printed to stdout (CLI mode).
    """
    # Split cross-year ranges into per-calendar-year chunks
    chunks = _year_chunks(from_date, to_date)
    if len(chunks) > 1:
        combined: list[dict] = []
        for idx, (chunk_from, chunk_to) in enumerate(chunks):
            if progress_callback:
                progress_callback({
                    "stage": "category_start",
                    "kind": "year",
                    "category": chunk_from[:4],
                    "category_index": idx + 1,
                    "total_categories": len(chunks),
                })
            else:
                print(f"\n── Year chunk {idx + 1}/{len(chunks)}: {chunk_from} → {chunk_to}", flush=True)
            try:
                combined.extend(fetch_all(chunk_from, chunk_to, indicator_ids, saleyard_id, contact_email, progress_callback))
            except urllib.error.HTTPError as e:
                if e.code == 500:
                    msg = f"No data for {chunk_from[:4]} (HTTP 500) — skipping"
                    if progress_callback:
                        progress_callback({"stage": "warning", "message": msg})
                    else:
                        print(f"  ⚠  {msg}", flush=True)
                else:
                    raise
        return combined

    fetch_start = time.time()
    combined: list[dict] = []

    for idx, ind_id in enumerate(indicator_ids):
        desc = VALID_INDICATORS.get(ind_id, ("", f"Indicator {ind_id}", ""))[1]
        if progress_callback:
            progress_callback({
                "stage": "category_start",
                "kind": "indicator",
                "category": f"{ind_id}: {desc}",
                "category_index": idx + 1,
                "total_categories": len(indicator_ids),
            })
        else:
            print(f"\n── Indicator {idx + 1}/{len(indicator_ids)}: [{ind_id}] {desc}", flush=True)
        combined.extend(_fetch_one(from_date, to_date, ind_id, saleyard_id, contact_email, progress_callback))

    total_elapsed = time.time() - fetch_start
    rows_per_sec = len(combined) / total_elapsed if total_elapsed > 0 else 0

    if progress_callback:
        progress_callback({
            "stage": "complete",
            "rows_done": len(combined),
            "elapsed": total_elapsed,
            "rows_per_sec": rows_per_sec,
        })
    else:
        print(
            f"\n  Fetch complete: {len(combined)} rows in {_fmt_duration(total_elapsed)}"
            f"  ({rows_per_sec:.1f} rows/s)",
            flush=True,
        )

    return combined


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
    default_to   = (today - timedelta(days=1)).isoformat()
    default_from = date(today.year - 1, 1, 1).isoformat()
    all_ids      = sorted(VALID_INDICATORS.keys())

    parser = argparse.ArgumentParser(
        description="Fetch MLA /report/6 Australian Livestock Indicators (By Saleyard) data"
    )
    parser.add_argument("--from", dest="from_date", default=default_from,
                        metavar="YYYY-MM-DD", help=f"Start date (default: {default_from})")
    parser.add_argument("--to", dest="to_date", default=default_to,
                        metavar="YYYY-MM-DD", help=f"End date (default: {default_to})")
    parser.add_argument("--indicators", nargs="+", type=int, default=all_ids,
                        metavar="ID",
                        help="Indicator IDs to fetch (default: all 1-18). Use --list-indicators to see options.")
    parser.add_argument("--saleyard", dest="saleyard_id", default=None,
                        metavar="ID",
                        help="Filter by saleyard ID (e.g. WAG, WOD). Default: all saleyards.")
    parser.add_argument("--output", default="report6_saleyard_indicators.csv",
                        help="Output CSV file (default: report6_saleyard_indicators.csv)")
    parser.add_argument("--list-indicators", action="store_true",
                        help="Print valid indicator IDs and exit")
    parser.add_argument("--email", default="moon.zhou@thomasfoods.com",
                        metavar="EMAIL",
                        help="Your contact email, included in the User-Agent header")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_indicators:
        print("Valid indicators for /report/6:")
        print(f"  {'ID':>3}  {'Species':6}  {'Units':10}  Description")
        print(f"  {'─'*3}  {'─'*6}  {'─'*10}  {'─'*45}")
        for ind_id, (species, desc, units) in sorted(VALID_INDICATORS.items()):
            print(f"  {ind_id:>3}  {species:6}  {units:10}  {desc}")
        return

    invalid = [i for i in args.indicators if i not in VALID_INDICATORS]
    if invalid:
        print(f"Error: unknown indicator ID(s): {invalid}", file=sys.stderr)
        print("Run with --list-indicators to see valid options.", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    if args.to_date >= today:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        print(f"⚠  --to {args.to_date} includes today — capping to {yesterday} (API does not accept today's date)", flush=True)
        args.to_date = yesterday

    run_start = time.time()

    print("=" * 60)
    print("MLA Statistics API — /report/6 Livestock Indicators (By Saleyard)")
    print("=" * 60)
    print(f"  Date range  : {args.from_date} → {args.to_date}")
    print(f"  Indicators  : {args.indicators}")
    saleyard_display = args.saleyard_id if args.saleyard_id else "all saleyards"
    print(f"  Saleyard    : {saleyard_display}")
    print(f"  Output      : {args.output}")
    print(f"  Contact     : {args.email}")
    print(f"  Started at  : {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print("Fetching data ...", flush=True)

    try:
        rows = fetch_all(args.from_date, args.to_date, args.indicators, args.saleyard_id, args.email)
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
