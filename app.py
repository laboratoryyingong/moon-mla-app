#!/usr/bin/env python3
"""
MLA Report 10 — Local Streamlit App
Run with:  streamlit run app.py
"""

import base64
import time as _time
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from fetch_report10 import VALID_SPECIES, _fmt_duration, _progress_bar, fetch_all


def _svg_logo(path: str, width: int = 220) -> None:
    svg = Path(path).read_bytes()
    b64 = base64.b64encode(svg).decode()
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{b64}" width="{width}">',
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="Thomas Food MLA Query Tools — NLRS Slaughter",
    page_icon="🥩",
    layout="centered",
)

_svg_logo("TFI-Logo-Positive.svg", width=220)
st.title("MLA Query Tools")
st.subheader("NLRS Australian Slaughter Data — /report/10")
st.caption(
    "Data sourced from the [MLA Statistics API](https://api-mlastatistics.mla.com.au). "
    "Use subject to [MLA Terms of Use](https://www.mla.com.au/general/Terms-and-conditions/data-and-information/)."
)

st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
today = date.today()
default_from = date(today.year - 1, 1, 1)

col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From date", value=default_from, max_value=today, format="DD/MM/YYYY")
with col2:
    to_date = st.date_input("To date", value=today, max_value=today, format="DD/MM/YYYY")

species = st.multiselect(
    "Species",
    options=VALID_SPECIES,
    default=[],
    placeholder="Leave empty to fetch all species",
)

with st.expander("Advanced settings"):
    email = st.text_input(
        "Contact email (sent in User-Agent header)",
        value="moon.zhou@thomasfoods.com",
    )

fetch_btn = st.button("Fetch Data", type="primary", use_container_width=True)

# ── Fetch ─────────────────────────────────────────────────────────────────────
if fetch_btn:
    if from_date > to_date:
        st.error("'From' date must be before 'To' date.")
        st.stop()

    st.session_state.pop("df", None)
    st.session_state.pop("log_lines", None)

    progress_bar = st.progress(0.0, text="Starting...")

    st.caption("Log")
    log_area = st.empty()
    log_lines: list[str] = []

    sp_display = ", ".join(species) if species else "all species"
    log_lines.append(f"[{_time.strftime('%H:%M:%S')}] Starting fetch")
    log_lines.append(f"[{_time.strftime('%H:%M:%S')}] Date range : {from_date} → {to_date}")
    log_lines.append(f"[{_time.strftime('%H:%M:%S')}] Species    : {sp_display}")
    log_area.code("\n".join(log_lines), language=None)

    def on_progress(info: dict) -> None:
        stage = info["stage"]
        ts = _time.strftime("%H:%M:%S")

        if stage == "category_start":
            kind_label = "Year" if info.get("kind") == "year" else "Species"
            log_lines.append(
                f"[{ts}] ── {kind_label} {info['category_index']}/{info['total_categories']}: {info['category']}"
            )
            log_area.code("\n".join(log_lines), language=None)

        elif stage == "page_done":
            pct = info["rows_done"] / info["total_rows"] if info["total_rows"] else 0.0
            progress_bar.progress(
                min(pct, 1.0),
                text=(
                    f"Page {info['page']}/{info['total_pages']}  —  "
                    f"{info['rows_done']:,} / {info['total_rows']:,} rows  |  "
                    f"elapsed {_fmt_duration(info['elapsed'])}  |  "
                    f"ETA {_fmt_duration(info['eta'])}"
                ),
            )
            bar = _progress_bar(info["rows_done"], info["total_rows"])
            eta_str = f"ETA {_fmt_duration(info['eta'])}" if info["eta"] > 0 else "done"
            line = (
                f"[{ts}] Page {info['page']}/{info['total_pages']}  {bar}"
                f"  {info['rows_done']:,}/{info['total_rows']:,} rows"
                f"  {info['page_time']:.1f}s/page  delay={info['delay']:.1f}s"
                f"  elapsed={_fmt_duration(info['elapsed'])}  {eta_str}"
            )
            log_lines.append(line)

        elif stage == "waiting":
            log_lines.append(f"[{ts}] Waiting {info['wait_time']:.1f}s before page {info['page']} ...")

        elif stage == "warning":
            log_lines.append(f"[{ts}] ⚠  {info['message']}")

        elif stage == "rate_limited":
            log_lines.append(f"[{ts}] ⚠  Rate limited (HTTP {info['code']}) — backing off to {info['delay']:.1f}s")

        elif stage == "complete":
            progress_bar.progress(1.0, text="Done!")
            line = (
                f"[{ts}] Fetch complete: {info['rows_done']:,} rows"
                f"  in {_fmt_duration(info['elapsed'])}"
                f"  ({info['rows_per_sec']:.1f} rows/s,  {info['pages']} page(s))"
            )
            log_lines.append(line)

        log_area.code("\n".join(log_lines), language=None)

    try:
        rows = fetch_all(
            from_date.isoformat(),
            to_date.isoformat(),
            species,
            email,
            progress_callback=on_progress,
        )
        st.session_state["df"] = pd.DataFrame(rows)
        st.session_state["log_lines"] = log_lines
        st.success(f"Fetched {len(rows):,} rows successfully.")
    except Exception as e:
        log_lines.append(f"[{_time.strftime('%H:%M:%S')}] ✗  Error: {e}")
        log_area.code("\n".join(log_lines), language=None)
        st.error(f"Failed to fetch data: {e}")

# ── Saved log (shown after fetch completes) ───────────────────────────────────
if "log_lines" in st.session_state and not fetch_btn:
    with st.expander("Last fetch log", expanded=False):
        st.code("\n".join(st.session_state["log_lines"]), language=None)

# ── Results ───────────────────────────────────────────────────────────────────
if "df" in st.session_state:
    df: pd.DataFrame = st.session_state["df"]

    st.divider()
    st.subheader(f"Results — {len(df):,} rows")

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total rows", f"{len(df):,}")
    if "species_id" in df.columns:
        m2.metric("Species", df["species_id"].nunique())
    if "result_date" in df.columns:
        with m3:
            st.markdown("**Date range**")
            st.write(f"{df['result_date'].min()}  →  {df['result_date'].max()}")

    # Species breakdown chart
    if "species_id" in df.columns and "slaughter_count" in df.columns:
        import altair as alt
        with st.expander("Species breakdown", expanded=True):
            chart_df = (
                df.assign(slaughter_count=pd.to_numeric(df["slaughter_count"], errors="coerce"))
                .groupby("species_id")["slaughter_count"]
                .sum()
                .reset_index()
                .rename(columns={"slaughter_count": "Total slaughter", "species_id": "Species"})
                .sort_values("Total slaughter", ascending=False)
            )
            chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    y=alt.Y("Species:N", sort="-x", title=None),
                    x=alt.X("Total slaughter:Q", axis=alt.Axis(format=",.0f"), title="Total slaughter (head)"),
                    tooltip=[
                        alt.Tooltip("Species:N"),
                        alt.Tooltip("Total slaughter:Q", format=",.0f"),
                    ],
                )
                .properties(height=max(200, len(chart_df) * 60), padding={"left": 10, "right": 10, "top": 20, "bottom": 20})
            )
            st.altair_chart(chart, use_container_width=True)

    # Data table
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Download
    csv_bytes = df[["result_date", "contributor_state_id", "species_id", "slaughter_count"]].to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="report10_nlrs_slaughter.csv",
        mime="text/csv",
        use_container_width=True,
    )
