
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent

HISTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "quality_metrics_history.csv"
)

st.set_page_config(
    page_title="Olist Data Quality Monitoring",
    page_icon="📊",
    layout="wide",
)

st.title("Olist Data Quality Monitoring")
st.caption("Historical monitoring of the Olist data pipeline")


# --------------------------------------------------
# 2. Load historical metrics
# --------------------------------------------------

@st.cache_data
def load_data():
    if not HISTORY_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(HISTORY_PATH)

    if df.empty:
        return df

    df["run_timestamp"] = pd.to_datetime(
        df["run_timestamp"],
        errors="coerce",
        utc=True,
    )

    df = df.dropna(subset=["run_timestamp"])
    df = df.sort_values("run_timestamp")

    return df


df = load_data()


# --------------------------------------------------
# 3. Check data availability
# --------------------------------------------------

if df.empty:
    st.warning(
        "No historical metrics found. "
        "Run the data quality pipeline first."
    )
    st.stop()


# --------------------------------------------------
# 4. Latest run summary
# --------------------------------------------------

latest = df.iloc[-1]

st.subheader("Latest pipeline quality report")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total checks",
    int(latest["total_checks"]),
)

col2.metric(
    "Passed checks",
    int(latest["pass_checks"]),
)

col3.metric(
    "Checks requiring review",
    int(latest["review_checks"]),
)

col4.metric(
    "Failed checks",
    int(latest["fail_checks"]),
)

st.caption(
    f"Last recorded run: "
    f"{latest['run_timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}"
)


# --------------------------------------------------
# 5. Quality status evolution
# --------------------------------------------------

st.divider()
st.subheader("Quality checks evolution")

status_columns = [
    "pass_checks",
    "review_checks",
    "fail_checks",
]

available_status_columns = [
    column for column in status_columns
    if column in df.columns
]

status_df = df[
    ["run_timestamp"] + available_status_columns
].melt(
    id_vars="run_timestamp",
    var_name="status",
    value_name="number_of_checks",
)

fig_status = px.line(
    status_df,
    x="run_timestamp",
    y="number_of_checks",
    color="status",
    markers=True,
    title="PASS / REVIEW / FAIL over time",
)

st.plotly_chart(fig_status, use_container_width=True)


# --------------------------------------------------
# 6. Quality metrics evolution
# --------------------------------------------------

st.divider()
st.subheader("Detailed quality metrics")

metric_columns = [
    "non_positive_payments",
    "product_weight_g_missing",
    "product_weight_g_zero",
    "product_length_cm_missing",
    "product_height_cm_missing",
    "product_width_cm_missing",
    "duplicate_review_ids",
    "null_review_ids",
    "unmatched_categories",
]

available_metrics = [
    column for column in metric_columns
    if column in df.columns
]

if available_metrics:
    selected_metric = st.selectbox(
        "Select a metric",
        available_metrics,
    )

    fig_metric = px.line(
        df,
        x="run_timestamp",
        y=selected_metric,
        markers=True,
        title=f"Evolution of {selected_metric}",
    )

    st.plotly_chart(fig_metric, use_container_width=True)


# --------------------------------------------------
# 7. Historical data table
# --------------------------------------------------

st.divider()
st.subheader("Historical quality metrics")

st.dataframe(
    df.sort_values("run_timestamp", ascending=False),
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# 8. Refresh
# --------------------------------------------------

if st.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()
