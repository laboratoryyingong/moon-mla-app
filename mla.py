#!/usr/bin/env python3
"""
mla — unified command-line interface for the MLA Statistics API fetchers.

Usage:
    python3 mla.py list
    python3 mla.py fetch <report> [report-specific options]
    python3 mla.py fetch-all [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--email EMAIL] [--only ...] [--skip ...]
    python3 mla.py merge [merge options]
    python3 mla.py app

<report> is a report number (1-10) or a short name; run `mla.py list` to see both.
Every option after `fetch <report>` is passed straight to that report's fetcher,
so `mla.py fetch 3 --help` shows the full option list for /report/3.

Full documentation: docs/CLI.md
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# Report registry
# ---------------------------------------------------------------------------

REPORTS = {
    1:  ("exports",            "Australian Red Meat Exports — volume by country",        "Monthly"),
    2:  ("herd",               "Australian Herd and Flock Figures — ABS estimates",      "Annual"),
    3:  ("slaughter",          "Australian Slaughter and Production — ABS figures",      "Quarterly"),
    4:  ("yardings",           "Saleyard Yardings — NLRS head count by saleyard",        "Daily"),
    5:  ("indicators",         "NLRS Livestock Indicators — national price indices",    "Daily"),
    6:  ("saleyard-indicators","NLRS Livestock Indicators — by saleyard",                "Daily"),
    7:  ("global-prices",      "Global Cattle Prices — AUS (NLRS) + USA (Steiner)",      "Daily/Weekly"),
    8:  ("us-prices",          "US Domestic Cattle Prices — Steiner Consulting",         "Weekly"),
    9:  ("us-imports",         "US Imported Meat Prices — Steiner Consulting",           "Weekly"),
    10: ("nlrs-slaughter",     "NLRS Slaughter — head count by state × species",         "Weekly"),
}
NAME_TO_ID = {name: rid for rid, (name, _, _) in REPORTS.items()}


def resolve_report(token: str) -> int:
    """Accept '3', 'report3', '/report/3' or a short name like 'slaughter'."""
    t = token.strip().lower().lstrip("/")
    if t.startswith("report/"):
        t = t[len("report/"):]
    elif t.startswith("report"):
        t = t[len("report"):]
    if t.isdigit() and int(t) in REPORTS:
        return int(t)
    if t in NAME_TO_ID:
        return NAME_TO_ID[t]
    valid = ", ".join(f"{rid} ({name})" for rid, (name, _, _) in REPORTS.items())
    sys.exit(f"Unknown report '{token}'. Valid reports: {valid}")


def load_fetcher(report_id: int):
    return importlib.import_module(f"fetchers.fetch_report{report_id}")


def run_with_argv(module, prog: str, argv: list[str]) -> None:
    """Run module.main() as if invoked from the shell with the given argv."""
    saved = sys.argv
    sys.argv = [prog, *argv]
    try:
        module.main()
    finally:
        sys.argv = saved


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def cmd_list(_args) -> None:
    print(f"{'ID':>3}  {'Name':<20} {'Frequency':<13} Description")
    print("-" * 90)
    for rid, (name, desc, freq) in REPORTS.items():
        print(f"{rid:>3}  {name:<20} {freq:<13} {desc}")
    print()
    print("Fetch with:  mla.py fetch <ID|Name> [options]     e.g.  mla.py fetch 3 --from 2024-01-01")
    print("Options:     mla.py fetch <ID|Name> --help")


def cmd_fetch(argv: list[str]) -> None:
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit("usage: mla.py fetch <report> [options...]\n\n"
                 "<report> is a number (1-10) or a short name — run `mla.py list`.\n"
                 "Run `mla.py fetch <report> --help` to see that report's options.")
    rid = resolve_report(argv[0])
    run_with_argv(load_fetcher(rid), f"mla.py fetch {rid}", argv[1:])


def cmd_fetch_all(args) -> None:
    selected = [resolve_report(t) for t in args.only] if args.only else list(REPORTS)
    skipped  = {resolve_report(t) for t in args.skip}
    selected = [rid for rid in selected if rid not in skipped]

    common: list[str] = []
    if args.email:
        common += ["--email", args.email]

    results: list[tuple[int, str, float]] = []
    run_start = time.time()
    for idx, rid in enumerate(selected, 1):
        name = REPORTS[rid][0]
        module = load_fetcher(rid)

        argv = list(common)
        if rid == 2:  # /report/2 is keyed by year, not by date
            if args.from_date: argv += ["--from-year", args.from_date[:4]]
            if args.to_date:   argv += ["--to-year",   args.to_date[:4]]
        else:
            if args.from_date: argv += ["--from", args.from_date]
            if args.to_date:   argv += ["--to",   args.to_date]
        if args.output_dir:
            argv += ["--output", str(Path(args.output_dir) / module.DEFAULT_OUTPUT.name)]

        print(f"\n{'#' * 70}\n# [{idx}/{len(selected)}] report {rid} ({name})\n{'#' * 70}")
        t0 = time.time()
        try:
            run_with_argv(module, f"mla.py fetch {rid}", argv)
            status = "ok"
        except SystemExit as e:
            status = "ok" if e.code in (None, 0) else f"failed (exit {e.code})"
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            status = "interrupted"
            results.append((rid, status, time.time() - t0))
            break
        except Exception as e:  # keep going with the remaining reports
            status = f"failed ({type(e).__name__}: {e})"
        results.append((rid, status, time.time() - t0))

    print(f"\n{'=' * 70}\nfetch-all summary  ({_fmt(time.time() - run_start)} total)\n{'=' * 70}")
    for rid, status, secs in results:
        print(f"  report {rid:<3} {REPORTS[rid][0]:<20} {_fmt(secs):>7}   {status}")
    failed = [r for r in results if r[1] != "ok"]
    if failed:
        sys.exit(1)


def cmd_merge(argv: list[str]) -> None:
    module = importlib.import_module("analysis.merge_reports")
    run_with_argv(module, "mla.py merge", argv)


def cmd_app(_args) -> None:
    app = REPO_ROOT / "app.py"
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app)], check=False)
    except FileNotFoundError:
        sys.exit("streamlit is not installed. Run: pip install -r requirements.txt")


def _fmt(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m{s:02d}s"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mla.py",
        description="Command-line interface for downloading MLA Statistics API data.",
        epilog="Run `mla.py fetch <report> --help` for the options of a specific report.",
    )
    sub = p.add_subparsers(dest="command", required=True, metavar="<command>")

    s = sub.add_parser("list", help="List the available reports")
    s.set_defaults(func=cmd_list)

    # `fetch` and `merge` are dispatched before argparse (see main) so that every
    # option, including --help, reaches the underlying script untouched.
    sub.add_parser("fetch", help="Fetch one report: mla.py fetch <report> [options...]")

    s = sub.add_parser("fetch-all", help="Fetch every report for one date range")
    s.add_argument("--from", dest="from_date", metavar="YYYY-MM-DD",
                   help="Start date (year is used for /report/2). Omit to use each fetcher's default.")
    s.add_argument("--to", dest="to_date", metavar="YYYY-MM-DD",
                   help="End date. Omit to use each fetcher's default.")
    s.add_argument("--email", metavar="EMAIL", help="Contact email sent in the User-Agent header")
    s.add_argument("--output-dir", metavar="DIR",
                   help="Directory for the CSV files (default: data/raw/)")
    s.add_argument("--only", nargs="+", default=[], metavar="REPORT",
                   help="Run only these reports (numbers or names)")
    s.add_argument("--skip", nargs="+", default=[], metavar="REPORT",
                   help="Skip these reports (numbers or names)")
    s.set_defaults(func=cmd_fetch_all)

    sub.add_parser("merge", help="Merge /report/5 + /report/10 into a weekly table (requires pandas)")

    s = sub.add_parser("app", help="Launch the Streamlit web app")
    s.set_defaults(func=cmd_app)

    return p


PASSTHROUGH = {"fetch": cmd_fetch, "merge": cmd_merge}


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv and argv[0] in PASSTHROUGH:
        PASSTHROUGH[argv[0]](argv[1:])
        return
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
