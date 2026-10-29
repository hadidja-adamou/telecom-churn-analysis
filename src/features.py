"""
features.py
-----------
Feature engineering for the churn model.

Usage:
    from src.features import build_features

    df_features = build_features(df_clean)
"""

import pandas as pd

PROTECTION_COLS = ["onlinesecurity", "onlinebackup", "deviceprotection", "techsupport"]

# Add-on services that carry a "No internet service" category
SERVICE_COLS = ["onlinesecurity", "onlinebackup", "deviceprotection",
                "techsupport", "streamingtv", "streamingmovies"]

# Columns the model must never see: an identifier, plus helper columns created
# during the EDA (churn_bin is a copy of the target, tenure_band comes from tenure)
DROP_COLS = ["customerid", "churn_bin", "tenure_band"]


def build_features(df: pd.DataFrame, target_col: str = "churn") -> pd.DataFrame:
    """
    Turn the cleaned dataframe into a numeric table for modeling:
    - target as 0/1
    - three features derived from the EDA hypotheses (H2 and H4)
    - "No internet service" merged into "No" for the add-on services
    - identifier and EDA-only columns dropped
    - one-hot encoding for categorical columns
    """
    df = df.copy()

    # Target
    if not pd.api.types.is_numeric_dtype(df[target_col]):
        df[target_col] = df[target_col].map({"Yes": 1, "No": 0})

    # H2: new customers are the most at risk (same cut as the first EDA tenure band, 0-11)
    df["is_new_customer"] = (df["tenure"] < 12).astype(int)

    # H4: number of protection services subscribed
    df["n_protection"] = (df[PROTECTION_COLS] == "Yes").sum(axis=1)

    # H4: internet customers with neither online security nor tech support
    df["no_security_no_support"] = (
        (df["onlinesecurity"] == "No") & (df["techsupport"] == "No")
    ).astype(int)

    # Merge "No internet service" into "No". This must come after the features
    # above: no_security_no_support relies on telling the two apart. The
    # internetservice column already identifies customers without internet.
    df[SERVICE_COLS] = df[SERVICE_COLS].replace("No internet service", "No")

    # Drop columns the model must not see
    df = df.drop(columns=DROP_COLS, errors="ignore")

    # One-hot: no artificial order between categories, readable SHAP plots later
    df = pd.get_dummies(df, drop_first=True, dtype=int)

    return df
