#!/usr/bin/env python3
"""
Merge /report/5 (price indicators) + /report/10 (slaughter counts) into one analysis table.

Output
------
merged_weekly.csv       — main wide table, one row per (week_ending × species_group)
indicator_lookup.csv    — column legend: indicator_id → desc, units, species_group

Column layout of merged_weekly.csv
-----------------------------------
week_ending             — Friday date (YYYY-MM-DD)
species_group           — Cattle | Lambs | Sheep | Calves | Pigs | Goat | Deer
national_slaughter      — total head count (all states)
slaughter_NSW/QLD/...   — per-state head counts
ind_1_price_avg         — weekly average of indicator_value  (price, in indicator units)
...
ind_18_price_avg
ind_1_heads_avg         — weekly average of head_count in the indicator sample
...
ind_18_heads_avg

Species → indicator mapping
    Cattle  → indicators 1,2,3,4,5,12,13,14,15,17  (10 cattle indicators)
    Lambs   → indicators 6,7,8,9,10,16              (lamb-specific)
    Sheep   → indicators 11,18                       (mutton/sheep-specific)
    Calves / Pigs / Goat / Deer → slaughter only, no price indicators

Usage
-----
    python merge_reports.py
    python merge_reports.py --r5 my_r5.csv --r10 my_r10.csv --output custom.csv
"""

import argparse
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Species groupings
# ---------------------------------------------------------------------------

CATTLE_SPECIES = {"Cattle"}
LAMB_SPECIES   = {"Lambs"}
SHEEP_SPECIES  = {"Sheep"}

CATTLE_INDICATORS = [1, 2, 3, 4, 5, 12, 13, 14, 15, 17]
LAMB_INDICATORS   = [6, 7, 8, 9, 10, 16]
SHEEP_INDICATORS  = [11, 18]

INDICATOR_META = {
    1:  ("c/kg cwt", "Western Young Cattle Indicator"),
    2:  ("c/kg lwt", "National Restocker Yearling Steer Indicator"),
    3:  ("c/kg lwt", "National Feeder Steer Indicator"),
    4:  ("c/kg lwt", "National Heavy Steer Indicator"),
    5:  ("c/kg lwt", "National Heavy Dairy Cow Indicator"),
    6:  ("c/kg cwt", "National Light Lamb Indicator"),
    7:  ("c/kg cwt", "National Trade Lamb Indicator"),
    8:  ("c/kg cwt", "National Heavy Lamb Indicator"),
    9:  ("c/kg cwt", "National Merino Lamb Indicator"),
    10: ("c/kg cwt", "National Restocker Lamb Indicator"),
    11: ("c/kg cwt", "National Mutton Indicator"),
    12: ("c/kg lwt", "National Restocker Yearling Heifer Indicator"),
    13: ("c/kg lwt", "National Processor Cow Indicator"),
    14: ("c/kg lwt", "National Young Cattle Indicator"),
    15: ("c/kg lwt", "Online Young Cattle Indicator"),
    16: ("$/head",   "Online Lamb Indicator"),
    17: ("c/kg lwt", "National Feeder Heifer Indicator"),
    18: ("$/head",   "Online Sheep Indicator"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def weekly_pivot(r5: pd.DataFrame, indicator_ids: list[int]) -> pd.DataFrame:
    """
    Aggregate r5 daily rows to weekly (week-ending Friday) for the given
    indicator IDs, then pivot so each indicator becomes two columns:
        ind_{id}_price_avg   — mean of indicator_value for the week
        ind_{id}_heads_avg   — mean of head_count for the week
    """
    subset = r5[r5["indicator_id"].isin(indicator_ids)].copy()
    if subset.empty:
        return pd.DataFrame(columns=["week_ending"])

    weekly = (
        subset
        .groupby([
            pd.Grouper(key="calendar_date", freq="W-FRI"),
            "indicator_id",
        ])
        .agg(
            price_avg=("indicator_value", "mean"),
            heads_avg=("head_count",      "mean"),
        )
        .reset_index()
        .rename(columns={"calendar_date": "week_ending"})
    )

    price = weekly.pivot(index="week_ending", columns="indicator_id", values="price_avg")
    heads = weekly.pivot(index="week_ending", columns="indicator_id", values="heads_avg")
    price.columns = [f"ind_{c}_price_avg" for c in price.columns]
    heads.columns = [f"ind_{c}_heads_avg" for c in heads.columns]

    return pd.concat([price, heads], axis=1).reset_index()


def state_pivot(r10: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot r10 contributor_state_id into columns:
        national_slaughter, slaughter_NSW, slaughter_QLD, ...
    One row per (week_ending, species_id).
    """
    national = (
        r10.groupby(["result_date", "species_id"])["slaughter_count"]
        .sum()
        .reset_index()
        .rename(columns={"result_date": "week_ending", "slaughter_count": "national_slaughter"})
    )

    states = (
        r10.pivot_table(
            index=["result_date", "species_id"],
            columns="contributor_state_id",
            values="slaughter_count",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename(columns={"result_date": "week_ending"})
    )
    state_cols = [c for c in states.columns if c not in ("week_ending", "species_id")]
    states = states.rename(columns={c: f"slaughter_{c}" for c in state_cols})

    return national.merge(states, on=["week_ending", "species_id"])


# ---------------------------------------------------------------------------
# Main merge
# ---------------------------------------------------------------------------

def merge(r5_path: str, r10_path: str) -> pd.DataFrame:
    r5  = pd.read_csv(r5_path,  parse_dates=["calendar_date"])
    r10 = pd.read_csv(r10_path, parse_dates=["result_date"])

    # r5: weekly indicator tables per species group
    cattle_ind = weekly_pivot(r5, CATTLE_INDICATORS)
    lamb_ind   = weekly_pivot(r5, LAMB_INDICATORS)
    sheep_ind  = weekly_pivot(r5, SHEEP_INDICATORS)

    # r10: national total + per-state breakdown
    r10_wide = state_pivot(r10)

    # Join by species group
    frames = []
    for species, ind_table in [
        (CATTLE_SPECIES, cattle_ind),
        (LAMB_SPECIES,   lamb_ind),
        (SHEEP_SPECIES,  sheep_ind),
    ]:
        chunk = r10_wide[r10_wide["species_id"].isin(species)].copy()
        if not chunk.empty and not ind_table.empty:
            chunk = chunk.merge(ind_table, on="week_ending", how="left")
        frames.append(chunk)

    # Species without price indicators (Calves, Pigs, Goat, Deer)
    other_species = ~r10_wide["species_id"].isin(CATTLE_SPECIES | LAMB_SPECIES | SHEEP_SPECIES)
    frames.append(r10_wide[other_species].copy())

    merged = (
        pd.concat(frames, ignore_index=True)
        .rename(columns={"species_id": "species_group"})
        .sort_values(["week_ending", "species_group"])
        .reset_index(drop=True)
    )

    # Re-order columns: fixed prefix → all price cols (1→18) → all heads cols (1→18)
    prefix_cols = [
        "week_ending", "species_group", "national_slaughter",
        "slaughter_NSW", "slaughter_QLD", "slaughter_SA",
        "slaughter_TAS", "slaughter_VIC", "slaughter_WA",
    ]
    all_ids = sorted(INDICATOR_META.keys())
    price_cols = [f"ind_{i}_price_avg" for i in all_ids if f"ind_{i}_price_avg" in merged.columns]
    heads_cols = [f"ind_{i}_heads_avg" for i in all_ids if f"ind_{i}_heads_avg" in merged.columns]
    merged = merged[prefix_cols + price_cols + heads_cols]

    # Rename ind_N_price_avg / ind_N_heads_avg to include desc and units
    rename_map = {}
    for ind_id, (units, desc) in INDICATOR_META.items():
        old_price = f"ind_{ind_id}_price_avg"
        old_heads = f"ind_{ind_id}_heads_avg"
        label = f"ind_{ind_id} {desc} ({units})"
        if old_price in merged.columns:
            rename_map[old_price] = f"{label} price_avg"
        if old_heads in merged.columns:
            rename_map[old_heads] = f"{label} heads_avg"
    merged = merged.rename(columns=rename_map)

    return merged


def indicator_lookup() -> pd.DataFrame:
    rows = []
    for ind_id, (units, desc) in INDICATOR_META.items():
        if ind_id in CATTLE_INDICATORS:
            applies_to = "Cattle"
        elif ind_id in LAMB_INDICATORS:
            applies_to = "Lambs"
        else:
            applies_to = "Sheep"
        rows.append({
            "indicator_id":    ind_id,
            "price_col":       f"ind_{ind_id}_price_avg",
            "heads_col":       f"ind_{ind_id}_heads_avg",
            "indicator_desc":  desc,
            "indicator_units": units,
            "applies_to":      applies_to,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Merge report/5 + report/10 into a weekly analysis table")
    p.add_argument("--r5",     default="report5_livestock_indicators.csv")
    p.add_argument("--r10",    default="report10_nlrs_slaughter.csv")
    p.add_argument("--output", default="merged_weekly.csv")
    p.add_argument("--lookup", default="indicator_lookup.csv")
    return p.parse_args()


def main():
    args = parse_args()

    print(f"Loading {args.r5} ...")
    print(f"Loading {args.r10} ...")
    df = merge(args.r5, args.r10)

    out = Path(args.output)
    df.to_csv(out, index=False)
    print(f"Saved {len(df):,} rows → {out.resolve()}")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}")

    lk = indicator_lookup()
    lk.to_csv(args.lookup, index=False)
    print(f"Saved indicator lookup → {Path(args.lookup).resolve()}")

    print()
    print("=== Coverage by species ===")
    price_cols = [c for c in df.columns if c.endswith("_price_avg")]
    rows = []
    for sp, grp in df.groupby("species_group"):
        filled = sum(1 for c in price_cols if grp[c].notna().any())
        rows.append({
            "species_group":             sp,
            "weeks":                     grp["week_ending"].nunique(),
            "national_slaughter_total":  int(grp["national_slaughter"].sum()),
            "price_indicator_cols":      filled,
        })
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
