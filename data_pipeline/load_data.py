"""
Loads the raw Kaggle CSV and performs an initial sanity inspection
before any cleaning happens. Always look at raw data before touching
it — you want to know what you're dealing with first.
"""

import pandas as pd
from loguru import logger

from data_pipeline.config import RAW_DATA_PATH, RAW_COLUMNS_NEEDED


def load_raw_data(path=RAW_DATA_PATH) -> pd.DataFrame:
    """
    Loads the raw ticket CSV from disk.

    Raises a clear, actionable error if the file is missing, instead
    of letting pandas throw a confusing FileNotFoundError deep in a
    stack trace.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found at {path}.\n"
            f"Download it from Kaggle (see Phase 4 instructions) and "
            f"place it at this exact path before running the pipeline."
        )

    logger.info(f"Loading raw data from {path}")
    df = pd.read_csv(path)
    logger.info(f"Loaded {len(df):,} rows and {len(df.columns)} columns")

    # Keep only the columns this project actually uses.
    missing_cols = [c for c in RAW_COLUMNS_NEEDED if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Expected columns missing from the CSV: {missing_cols}\n"
            f"Available columns are: {list(df.columns)}\n"
            f"Check that you downloaded the correct dataset version."
        )

    df = df[RAW_COLUMNS_NEEDED].copy()
    return df


def inspect_raw_data(df: pd.DataFrame) -> None:
    """
    Prints a quick summary of the raw dataframe: shape, dtypes,
    missing values, and a few sample rows. This is the "look before
    you clean" step every data pipeline should start with.
    """
    print("=" * 60)
    print("RAW DATA INSPECTION")
    print("=" * 60)
    print(f"\nShape: {df.shape[0]:,} rows x {df.shape[1]} columns\n")

    print("Missing values per column:")
    print(df.isnull().sum().to_string())

    print("\nData types:")
    print(df.dtypes.to_string())

    print("\nSample rows:")
    print(df.head(3).to_string())
    print("=" * 60)


if __name__ == "__main__":
    raw_df = load_raw_data()
    inspect_raw_data(raw_df)