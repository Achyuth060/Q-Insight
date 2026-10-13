import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# DATASET PATH
# ============================================================

DATA_PATH = (
    Path(__file__).parent
    / "dataset"
    / "test_gokul_new2.csv"
)


# ============================================================
# LOAD AND PREPROCESS DATA
# ============================================================

def load_data():
    """
    Load and preprocess the real historical
    quantum-computing job dataset.
    """

    # --------------------------------------------------------
    # Check dataset
    # --------------------------------------------------------

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    # --------------------------------------------------------
    # Rename original dataset columns
    # --------------------------------------------------------

    rename_map = {
        "machine": "backend",
        "depth": "circuit_depth",
        "gateops": "gate_count",
        "run_time": "runtime_sec",
        "date": "created"
    }

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "queue_time",
        "runtime_sec",
        "shots",
        "width",
        "qubits",
        "circuit_depth",
        "gate_count"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Convert queue time to minutes
    #
    # queue_time is stored in seconds
    # wait_min is the ML target
    # --------------------------------------------------------

    if "queue_time" in df.columns:

        df["wait_min"] = (
            df["queue_time"] / 60.0
        )

    else:

        df["wait_min"] = np.nan

    # --------------------------------------------------------
    # Clean job status
    # --------------------------------------------------------

    if "status" in df.columns:

        df["status"] = (
            df["status"]
            .astype(str)

            # Remove JobStatus. prefix
            .str.replace(
                "JobStatus.",
                "",
                regex=False
            )

            # Remove single quotes
            .str.replace(
                "'",
                "",
                regex=False
            )

            # Remove double quotes
            .str.replace(
                '"',
                "",
                regex=False
            )

            # Standardize capitalization
            .str.upper()

            # Remove extra spaces
            .str.strip()
        )

        # ----------------------------------------------------
        # Standardize completed statuses
        # ----------------------------------------------------

        df["status"] = df["status"].replace({

            "DONE": "COMPLETED",

            "SUCCESS": "COMPLETED",

            "SUCCEEDED": "COMPLETED"

        })

    # --------------------------------------------------------
    # Create Job ID
    # --------------------------------------------------------

    if "job_id" not in df.columns:

        df["job_id"] = [
            f"JOB-{i + 1:05d}"
            for i in range(len(df))
        ]

    # --------------------------------------------------------
    # Clean backend names
    # --------------------------------------------------------

    if "backend" in df.columns:

        df["backend"] = (
            df["backend"]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------------
    # Convert created/date to datetime
    # --------------------------------------------------------

    if "created" in df.columns:

        df["created"] = pd.to_datetime(
            df["created"],
            errors="coerce",
            utc=True
        )

    # --------------------------------------------------------
    # Remove rows missing ML information
    # --------------------------------------------------------

    required_columns = [
        "qubits",
        "circuit_depth",
        "gate_count",
        "wait_min"
    ]

    df = df.dropna(
        subset=required_columns
    )

    # --------------------------------------------------------
    # Remove impossible values
    # --------------------------------------------------------

    df = df[
        (df["wait_min"] >= 0)
        &
        (df["qubits"] > 0)
        &
        (df["circuit_depth"] >= 0)
        &
        (df["gate_count"] >= 0)
    ]

    # --------------------------------------------------------
    # Reset dataframe index
    # --------------------------------------------------------

    df = df.reset_index(
        drop=True
    )

    return df


# ============================================================
# GET JOBS
# ============================================================

def get_jobs(limit=None):
    """
    Compatibility function used by the Streamlit application.

    Loads the real historical quantum-job dataset.
    """

    df = load_data()

    # --------------------------------------------------------
    # Use complete dataset by default
    # --------------------------------------------------------

    if limit is not None and limit > 0:

        return (
            df.head(limit),
            "DATASET"
        )

    return (
        df,
        "DATASET"
    )


# ============================================================
# DATASET SUMMARY
# ============================================================

def get_dataset_summary(df):
    """
    Return useful dataset statistics.
    """

    summary = {

        "total_jobs":
            len(df),

        "total_backends":
            (
                df["backend"].nunique()
                if "backend" in df.columns
                else 0
            ),

        "average_qubits":
            (
                df["qubits"].mean()
                if "qubits" in df.columns
                else 0
            ),

        "average_wait_min":
            (
                df["wait_min"].mean()
                if "wait_min" in df.columns
                else 0
            )
    }

    # --------------------------------------------------------
    # Completed jobs
    # --------------------------------------------------------

    if "status" in df.columns:

        summary["completed_jobs"] = int(
            (
                df["status"]
                .astype(str)
                .str.upper()
                == "COMPLETED"
            ).sum()
        )

    else:

        summary["completed_jobs"] = 0

    return summary