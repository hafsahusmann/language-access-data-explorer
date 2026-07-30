"""
Language Access Data Explorer — demo
Internal navigation tool for the 911 dispatch / language access research team.

This version runs on DUMMY, RANDOMLY GENERATED data so the team can see the
shape of the tool before real (de-identified) data is available. Swap the
`load_data()` function for a real Google Sheets read once the data dictionary
and de-identified dataset are ready (see README.md).
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Page setup + brand colors
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Language Access Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

PURPLE = "#865391"
LAVENDER = "#b98cc4"
CORAL = "#D85A30"
TEAL = "#1D9E75"

st.markdown(
    f"""
    <style>
    .main-header {{
        background-color: {PURPLE};
        padding: 1.1rem 1.5rem;
        border-radius: 6px;
        color: white;
        margin-bottom: 1.2rem;
    }}
    .main-header h1 {{
        color: white;
        font-size: 1.5rem;
        margin: 0;
    }}
    .stat-card {{
        background-color: {LAVENDER};
        border-radius: 8px;
        padding: 0.9rem 1rem;
        text-align: center;
        color: white;
    }}
    .stat-card .value {{
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .stat-card .label {{
        font-size: 0.8rem;
        opacity: 0.9;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header"><h1>Language Access Data Explorer</h1></div>',
    unsafe_allow_html=True,
)
st.caption("⚠️ Demo build — all data below is randomly generated, not real call data.")


# ---------------------------------------------------------------------------
# Dummy data generator — swap this out for the real data source later
# ---------------------------------------------------------------------------
@st.cache_data
def load_data(n=1200, seed=42):
    rng = np.random.default_rng(seed)

    centers = ["Valley Communications", "SECOMM", "Verdugo", "NORCOM"]
    center_weights = [0.28, 0.24, 0.22, 0.26]

    languages = ["Spanish", "Mandarin", "Vietnamese", "Somali", "Amharic",
                 "Russian", "Korean", "Arabic", "Tagalog", None]
    lang_weights = [0.30, 0.12, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05, 0.07]

    # rough zip pools per center so filters feel plausible
    zip_pools = {
        "Valley Communications": ["98032", "98002", "98042", "98058", "98003"],
        "SECOMM": ["98118", "98168", "98188", "98198", "98146"],
        "Verdugo": ["91201", "91205", "91214", "91208", "91011"],
        "NORCOM": ["98033", "98052", "98004", "98007", "98074"],
    }

    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=int(d)) for d in rng.integers(0, 210, n)]

    call_center = rng.choice(centers, size=n, p=center_weights)
    interpreter_used = rng.random(n) < 0.46
    language = rng.choice(languages, size=n, p=lang_weights)
    language = np.where(interpreter_used, language, None)

    zip_code = [rng.choice(zip_pools[c]) for c in call_center]
    connect_time = np.where(
        interpreter_used,
        rng.gamma(shape=3.0, scale=25, size=n) + 20,   # interpreter calls take longer to connect
        rng.gamma(shape=2.0, scale=12, size=n) + 5,
    ).round(0)

    hour = rng.integers(0, 24, n)
    time_of_day = pd.cut(
        hour, bins=[-1, 5, 11, 17, 21, 24],
        labels=["Overnight (12–6a)", "Morning (6a–12p)", "Afternoon (12–6p)",
                "Evening (6–9p)", "Late Night (9p–12a)"],
    )

    df = pd.DataFrame({
        "call_id": [f"{10000+i}" for i in range(n)],
        "call_center": call_center,
        "call_date": dates,
        "interpreter_used": interpreter_used,
        "language": language,
        "zip_code": zip_code,
        "time_of_day": time_of_day,
        "connect_time_sec": connect_time.astype(int),
    })
    df["call_date"] = pd.to_datetime(df["call_date"])
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

centers_sel = st.sidebar.multiselect(
    "Call Center", options=sorted(df["call_center"].unique()),
    default=sorted(df["call_center"].unique()),
)

min_date, max_date = df["call_date"].min().date(), df["call_date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date,
)

interp_choice = st.sidebar.radio(
    "Interpreter Used?", options=["All", "Yes", "No"], horizontal=True,
)

zip_options = sorted(df["zip_code"].unique())
zip_sel = st.sidebar.multiselect("Zip Code Area", options=zip_options, default=[])

lang_options = sorted([l for l in df["language"].dropna().unique()])
lang_sel = st.sidebar.multiselect("Language", options=lang_options, default=[])

tod_options = list(df["time_of_day"].cat.categories)
tod_sel = st.sidebar.multiselect("Time of Day", options=tod_options, default=[])

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
filtered = df[df["call_center"].isin(centers_sel)]

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["call_date"].dt.date >= start) & (filtered["call_date"].dt.date <= end)
    ]

if interp_choice == "Yes":
    filtered = filtered[filtered["interpreter_used"]]
elif interp_choice == "No":
    filtered = filtered[~filtered["interpreter_used"]]

if zip_sel:
    filtered = filtered[filtered["zip_code"].isin(zip_sel)]

if lang_sel:
    filtered = filtered[filtered["language"].isin(lang_sel)]

if tod_sel:
    filtered = filtered[filtered["time_of_day"].isin(tod_sel)]

# ---------------------------------------------------------------------------
# Stat cards
# ---------------------------------------------------------------------------
total_calls = len(filtered)
pct_interp = (filtered["interpreter_used"].mean() * 100) if total_calls else 0
avg_connect = filtered["connect_time_sec"].mean() if total_calls else 0

c1, c2, c3 = st.columns(3)
for col, value, label in zip(
    [c1, c2, c3],
    [f"{total_calls:,}", f"{pct_interp:.0f}%", f"{avg_connect/60:.1f} min"],
    ["Total Calls", "Interpreter Use", "Avg Connect Time"],
):
    col.markdown(
        f'<div class="stat-card"><div class="value">{value}</div>'
        f'<div class="label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Interpreter Use by Call Center")
    if total_calls:
        summary = (
            filtered.groupby(["call_center", "interpreter_used"])
            .size().reset_index(name="count")
        )
        summary["Interpreter"] = summary["interpreter_used"].map({True: "Used", False: "Not used"})
        fig1 = px.bar(
            summary, x="call_center", y="count", color="Interpreter", barmode="group",
            color_discrete_map={"Used": CORAL, "Not used": TEAL},
            labels={"call_center": "", "count": "Calls"},
        )
        fig1.update_layout(legend_title="", margin=dict(t=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No calls match the current filters.")

with chart_col2:
    st.subheader("Calls per Week")
    if total_calls:
        weekly = (
            filtered.set_index("call_date")
            .resample("W")["call_id"].count()
            .reset_index(name="calls")
        )
        fig2 = px.line(weekly, x="call_date", y="calls", labels={"call_date": "", "calls": "Calls"})
        fig2.update_traces(line_color=PURPLE)
        fig2.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No calls match the current filters.")

st.subheader("Top Zip Code Areas by Volume")
if total_calls:
    zip_summary = (
        filtered.groupby(["zip_code", "interpreter_used"])
        .size().reset_index(name="count")
    )
    zip_summary["Interpreter"] = zip_summary["interpreter_used"].map({True: "Used", False: "Not used"})
    top_zips = filtered["zip_code"].value_counts().nlargest(10).index
    zip_summary = zip_summary[zip_summary["zip_code"].isin(top_zips)]
    fig3 = px.bar(
        zip_summary, x="zip_code", y="count", color="Interpreter", barmode="stack",
        color_discrete_map={"Used": CORAL, "Not used": TEAL},
        labels={"zip_code": "", "count": "Calls"},
    )
    fig3.update_layout(legend_title="", margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No calls match the current filters.")

# ---------------------------------------------------------------------------
# Data table + download
# ---------------------------------------------------------------------------
st.subheader("Filtered Data")
st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=300)

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_call_data.csv",
    mime="text/csv",
)
