"""
data_loading.py
----------------
Load and clean the Telco Customer Churn dataset.

Usage:
    from src.data_loading import load_raw_data, clean_data

    df_raw = load_raw_data("data/raw/telco_churn.csv")
    df_clean = clean_data(df_raw)
"""

import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw CSV as downloaded from Kaggle."""
    df = pd.read_csv(path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Telco Churn dataset:
    - Normalize column names to snake_case
    - Convert TotalCharges to numeric (it's blank for brand-new customers
      with zero tenure)
    - Drop any duplicate rows
    """
    df = df.copy()

    # Normalize column names
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.lower()
    )

    # TotalCharges comes in as an empty string for customers with tenure = 0
    if "totalcharges" in df.columns:
        df["totalcharges"] = pd.to_numeric(df["totalcharges"], errors="coerce")
        df["totalcharges"] = df["totalcharges"].fillna(0)

    df = df.drop_duplicates()

    return df


if __name__ == "__main__":
    raw = load_raw_data("data/raw/telco_churn.csv")
    clean = clean_data(raw)
    clean.to_csv("data/processed/telco_clean.csv", index=False)
    print(f"Cleaned data: {clean.shape[0]} rows, {clean.shape[1]} columns")
