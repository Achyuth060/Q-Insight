import os
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from dotenv import load_dotenv
from sklearn.ensemble import RandomForestRegressor

from data import get_jobs
from circuit import build_circuit, circuit_metrics, simulate


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="Q-Insight | IBM Quantum",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .small-muted {
        color: #777;
        font-size: 0.9rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f7ff, #ffffff);
        border: 1px solid #e5e0ff;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        font-weight: 700;
    }

    h1 {
        letter-spacing: -1px;
    }

    h2, h3 {
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }

    .insight-box {
        padding: 18px;
        border-radius: 12px;
        background: #f7f5ff;
        border-left: 5px solid #7c4dff;
        margin: 10px 0;
    }

    .project-card {
        padding: 20px;
        border-radius: 14px;
        background: linear-gradient(135deg, #f8f7ff, #ffffff);
        border: 1px solid #e5e0ff;
        margin-bottom: 15px;
    }

    .status-card {
        padding: 14px 18px;
        border-radius: 10px;
        background: #fafafa;
        border: 1px solid #eeeeee;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=60)
def load_data():
    """
    Load the complete real quantum-job dataset.
    """

    return get_jobs()


df, mode = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("⚛️ Q-Insight")

st.caption(
    "Quantum Computing Operations & Intelligence Platform  |  "
    "Job Monitoring • Backend Analytics • Circuit Intelligence"
)


# ============================================================
# MODE STATUS
# ============================================================

if mode == "IBM LIVE":

    st.success(
        "🟢 IBM QUANTUM CONNECTED — Live authenticated job data"
    )

else:

    st.info(
        "🔵 DATASET MODE — Q-Insight is analyzing historical "
        "quantum-computing job data from the selected research "
        "dataset. IBM Quantum live integration can be enabled "
        "when credentials are configured."
    )


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

pages = [
    "Overview",
    "Live Jobs",
    "Backend Analytics",
    "Historical Analytics",
    "Circuit Analyzer",
    "Predictive Insights"
]

page = st.sidebar.radio(
    "Navigation",
    pages
)

st.sidebar.markdown("---")

st.sidebar.caption("END-SEMESTER CAPSTONE")
st.sidebar.caption("Q-INSIGHT")
st.sidebar.caption("IBM Quantum Job Monitoring & Analytics")


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.header("Quantum Operations Overview")

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4, c5 = st.columns(5)

    total_jobs = len(df)

    completed_jobs = int(
        (
            df["status"]
            .astype(str)
            .str.upper()
            == "COMPLETED"
        ).sum()
    )

    queued_jobs = int(
        df["status"]
        .astype(str)
        .str.upper()
        .isin(
            ["QUEUED", "RUNNING"]
        ).sum()
    )

    backend_count = int(
        df["backend"].nunique()
    )

    avg_qubits = (
        df["qubits"].dropna().mean()
        if df["qubits"].notna().any()
        else None
    )

    c1.metric(
        "Total Jobs",
        total_jobs
    )

    c2.metric(
        "Completed",
        completed_jobs
    )

    c3.metric(
        "Queued / Running",
        queued_jobs
    )

    c4.metric(
        "Backends",
        backend_count
    )

    c5.metric(
        "Avg Qubits",
        f"{avg_qubits:.0f}"
        if avg_qubits is not None
        else "N/A"
    )

    # --------------------------------------------------------
    # JOB STATUS + BACKEND WORKLOAD
    # --------------------------------------------------------

    st.subheader("📊 Quantum Workload Overview")

    a, b = st.columns(2)

    with a:

        counts = (
            df["status"]
            .value_counts()
            .reset_index()
        )

        counts.columns = [
            "Status",
            "Jobs"
        ]

        fig_status = px.pie(
            counts,
            names="Status",
            values="Jobs",
            title="Job Status Distribution",
            hole=0.35
        )

        fig_status.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            )
        )

        st.plotly_chart(
            fig_status,
            width="stretch"
        )

    with b:

        back = (
            df["backend"]
            .value_counts()
            .reset_index()
        )

        back.columns = [
            "Backend",
            "Jobs"
        ]

        fig_backend = px.bar(
            back,
            x="Backend",
            y="Jobs",
            title="Jobs by Quantum Backend"
        )

        fig_backend.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            )
        )

        st.plotly_chart(
            fig_backend,
            width="stretch"
        )

    # --------------------------------------------------------
    # RECENT JOB ACTIVITY
    # --------------------------------------------------------

    st.subheader("🛰️ Recent Quantum Job Activity")

    recent_jobs = (
        df.sort_values(
            "created",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        recent_jobs,
        width="stretch",
        hide_index=True
    )

    # --------------------------------------------------------
    # QUANTUM OPERATIONS INSIGHTS
    # --------------------------------------------------------

    st.subheader("⚡ Quantum Operations Insights")

    completed_rate = (
        (
            df["status"]
            .astype(str)
            .str.upper()
            == "COMPLETED"
        ).mean() * 100
        if len(df) > 0
        else 0
    )

    avg_runtime = (
        df["runtime_sec"].dropna().mean()
        if df["runtime_sec"].notna().any()
        else 0
    )

    avg_depth = (
        df["circuit_depth"].dropna().mean()
        if df["circuit_depth"].notna().any()
        else 0
    )

    busiest_backend = (
        df["backend"].value_counts().idxmax()
        if not df.empty
        else "N/A"
    )

    i1, i2, i3, i4 = st.columns(4)

    with i1:

        st.metric(
            "Completion Rate",
            f"{completed_rate:.1f}%"
        )

    with i2:

        st.metric(
            "Avg Runtime",
            f"{avg_runtime:.2f} sec"
        )

    with i3:

        st.metric(
            "Avg Circuit Depth",
            f"{avg_depth:.1f}"
        )

    with i4:

        st.metric(
            "Busiest Backend",
            busiest_backend
        )

    st.markdown(
        f"""
        <div class="insight-box">
            <b>System Insight:</b>
            <b>{busiest_backend}</b> currently has the highest
            observed workload in the analyzed dataset.

            Q-Insight combines job-level information with backend
            and circuit characteristics to provide operational
            insights.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Presentation point: Q-Insight converts historical "
        "quantum execution records into operational KPIs, "
        "backend comparisons and analytical insights."
    )


# ============================================================
# LIVE / RECENT JOBS
# ============================================================

elif page == "Live Jobs":

    st.header("Quantum Job Records")

    st.caption(
        "Explore individual quantum jobs using backend, status, "
        "circuit and execution characteristics."
    )

    f1, f2, f3 = st.columns(3)

    status_options = (
        ["All"]
        + sorted(
            df["status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    backend_options = (
        ["All"]
        + sorted(
            df["backend"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    status = f1.selectbox(
        "Job Status",
        status_options
    )

    backend = f2.selectbox(
        "Quantum Backend",
        backend_options
    )

    search = f3.text_input(
        "Search Job ID",
        placeholder="Enter Job ID..."
    )

    view = df.copy()

    if status != "All":

        view = view[
            view["status"] == status
        ]

    if backend != "All":

        view = view[
            view["backend"] == backend
        ]

    if search:

        view = view[
            view["job_id"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.subheader(
        f"Quantum Jobs ({len(view)})"
    )

    st.dataframe(
        view.sort_values(
            "created",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )

    st.caption(
        f"Showing {len(view)} jobs from the historical quantum-job dataset."
    )


# ============================================================
# BACKEND ANALYTICS
# ============================================================

elif page == "Backend Analytics":

    st.header("Backend Performance & Workload")

    st.caption(
        "Compare quantum backends using workload, qubit, "
        "runtime and completion metrics."
    )

    g = (
        df.groupby(
            "backend",
            dropna=False
        )
        .agg(
            Jobs=("job_id", "count"),
            AvgQubits=("qubits", "mean"),
            AvgRuntime=("runtime_sec", "mean"),
            Completed=(
                "status",
                lambda x:
                (
                    x.astype(str).str.upper()
                    == "COMPLETED"
                ).sum()
            )
        )
        .reset_index()
    )

    g["Completion Rate %"] = (
        g["Completed"]
        / g["Jobs"]
        * 100
    ).round(1)

    g["AvgQubits"] = (
        g["AvgQubits"].round(2)
    )

    g["AvgRuntime"] = (
        g["AvgRuntime"].round(2)
    )

    st.dataframe(
        g,
        width="stretch",
        hide_index=True
    )

    a, b = st.columns(2)

    with a:

        fig_workload = px.bar(
            g,
            x="backend",
            y="Jobs",
            title="Backend Workload"
        )

        st.plotly_chart(
            fig_workload,
            width="stretch"
        )

    with b:

        fig_completion = px.bar(
            g,
            x="backend",
            y="Completion Rate %",
            title="Backend Completion Rate"
        )

        st.plotly_chart(
            fig_completion,
            width="stretch"
        )

    highest_workload = (
        g.loc[
            g["Jobs"].idxmax(),
            "backend"
        ]
    )

    best_completion = (
        g.loc[
            g["Completion Rate %"].idxmax(),
            "backend"
        ]
    )

    st.markdown(
        f"""
        <div class="insight-box">
            <b>Backend Insight:</b><br>
            • Highest observed workload:
            <b>{highest_workload}</b><br>
            • Highest completion rate:
            <b>{best_completion}</b>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HISTORICAL ANALYTICS
# ============================================================

elif page == "Historical Analytics":

    st.header("Historical Job Analytics")

    st.caption(
        "Analyze workload and execution behavior across "
        "the available historical quantum-job observations."
    )

    x = df.copy()

    x["created"] = pd.to_datetime(
        x["created"],
        errors="coerce",
        utc=True
    )

    x = x.dropna(
        subset=["created"]
    )

    x["date"] = x["created"].dt.date

    daily = (
        x.groupby("date")
        .size()
        .reset_index(name="Jobs")
    )

    st.plotly_chart(
        px.line(
            daily,
            x="date",
            y="Jobs",
            markers=True,
            title="Quantum Jobs Over Time"
        ),
        width="stretch"
    )

    runtime = x.dropna(
        subset=["runtime_sec"]
    )

    if not runtime.empty:

        st.plotly_chart(
            px.box(
                runtime,
                x="backend",
                y="runtime_sec",
                title="Runtime Distribution by Backend"
            ),
            width="stretch"
        )

    # --------------------------------------------------------
    # Historical summary
    # --------------------------------------------------------

    h1, h2, h3 = st.columns(3)

    h1.metric(
        "Observation Days",
        len(daily)
    )

    h2.metric(
        "Peak Daily Jobs",
        int(daily["Jobs"].max())
        if not daily.empty
        else 0
    )

    h3.metric(
        "Average Daily Jobs",
        f"{daily['Jobs'].mean():.1f}"
        if not daily.empty
        else "N/A"
    )

    st.caption(
        "The dataset provides historical observations that can "
        "be analyzed for workload, runtime and queue behavior."
    )


# ============================================================
# CIRCUIT ANALYZER
# ============================================================

elif page == "Circuit Analyzer":

    st.header("Quantum Circuit Analyzer")

    st.caption(
        "Inspect quantum circuit complexity and simulated "
        "measurement outcomes using Qiskit."
    )

    kind = st.selectbox(
        "Select Quantum Circuit",
        [
            "Bell State",
            "GHZ State",
            "Superposition",
            "Custom Demo"
        ]
    )

    if (
        kind == "GHZ State"
        or kind == "Superposition"
    ):

        n = st.slider(
            "Number of Qubits",
            2,
            8,
            3
        )

    else:

        n = 2

    qc = build_circuit(
        kind,
        n
    )

    metrics = circuit_metrics(
        qc
    )

    st.subheader(
        "Circuit Characteristics"
    )

    cols = st.columns(
        len(metrics)
    )

    for col, (k, v) in zip(
        cols,
        metrics.items()
    ):

        col.metric(
            k,
            v
        )

    st.subheader(
        "Quantum Circuit"
    )

    st.code(
        str(
            qc.draw(
                output="text"
            )
        ),
        language="text"
    )

    st.subheader(
        "Simulation Measurement Results"
    )

    try:

        counts = simulate(
            qc
        )

        result_df = pd.DataFrame(
            list(counts.items()),
            columns=[
                "Bitstring",
                "Counts"
            ]
        )

        fig_results = px.bar(
            result_df,
            x="Bitstring",
            y="Counts",
            title="Measurement Outcome Distribution"
        )

        st.plotly_chart(
            fig_results,
            width="stretch"
        )

        st.success(
            "Circuit simulation completed successfully."
        )

    except Exception:

        st.warning(
            "Local circuit simulation is unavailable. "
            "Install qiskit-aer using: pip install qiskit-aer"
        )

    st.info(
        "Viva point: circuit complexity can be described using "
        "qubit count, gate count, circuit depth and measurement outcomes."
    )


# ============================================================
# PREDICTIVE INSIGHTS
# ============================================================

elif page == "Predictive Insights":

    st.header("Queue-Time Intelligence")

    st.caption(
        "Estimate expected queue waiting time using historical "
        "quantum-job characteristics."
    )

    x = df.copy()

    train = x.dropna(
        subset=["wait_min"]
    ).copy()

    features = [
        "qubits",
        "circuit_depth",
        "gate_count"
    ]

    train = train.dropna(
        subset=features
    )

    if len(train) >= 15:

        X = train[features]

        y = train["wait_min"]

        model = RandomForestRegressor(
            n_estimators=120,
            random_state=42,
            max_depth=6
        )

        model.fit(
            X,
            y
        )

        c1, c2, c3 = st.columns(3)

        q = c1.number_input(
            "Number of Qubits",
            min_value=1,
            max_value=500,
            value=10
        )

        d = c2.number_input(
            "Circuit Depth",
            min_value=1,
            max_value=1000,
            value=20
        )

        g = c3.number_input(
            "Gate Count",
            min_value=1,
            max_value=5000,
            value=50
        )

        prediction_input = pd.DataFrame(
            [[q, d, g]],
            columns=features
        )

        pred = float(
            model.predict(
                prediction_input
            )[0]
        )

        st.subheader(
            "Prediction Result"
        )

        st.metric(
            "Estimated Queue Wait Time",
            f"{pred:.2f} minutes"
        )

        st.warning(
            "⚠️ This is a machine-learning estimate trained "
            "on historical quantum-job observations. "
            "It is NOT an IBM Quantum scheduler prediction."
        )

        imp = pd.DataFrame(
            {
                "Feature": features,
                "Importance":
                    model.feature_importances_
            }
        ).sort_values(
            "Importance",
            ascending=False
        )

        st.subheader(
            "Model Feature Importance"
        )

        fig_importance = px.bar(
            imp,
            x="Feature",
            y="Importance",
            title="Factors Influencing the Estimated Queue Wait Time"
        )

        st.plotly_chart(
            fig_importance,
            width="stretch"
        )

        st.markdown(
            """
            <div class="insight-box">
                <b>Model Interpretation:</b>
                The Random Forest model uses quantum-job
                characteristics such as qubit count, circuit
                depth and gate count to learn patterns from
                historical quantum-job observations.

                The target variable is queue waiting time,
                converted from the dataset's queue-time values
                into minutes.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "Not enough feature-complete historical records "
            "are available for a meaningful predictive model."
        )