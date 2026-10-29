"""
model.py
--------
Training and evaluation for the churn prediction models.

Usage:
    from src.model import split_data, train_baseline, train_advanced, evaluate

    X_train, X_test, y_train, y_test = split_data(X, y)
    baseline = train_baseline(X_train, y_train)
    evaluate(baseline, X_test, y_test)
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler


def split_data(X, y, test_size: float = 0.2, random_state: int = 42):
    """Stratified train/test split, so both sets keep the same churn rate."""
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def train_baseline(X_train, y_train) -> Pipeline:
    """
    Interpretable baseline: logistic regression on standardized features.
    The scaler is fitted on the training data only, inside the pipeline.
    """
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced"),
    )
    model.fit(X_train, y_train)
    return model


def train_advanced(X_train, y_train) -> RandomForestClassifier:
    """Stronger model: Random Forest, with class imbalance handling."""
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> None:
    """
    Print the key metrics. On an imbalanced churn problem, recall (catching
    actual churners) matters more than raw accuracy.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, y_pred, target_names=["Retained", "Churn"]))
    print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.3f}")
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))
