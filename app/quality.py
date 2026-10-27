"""Data quality checks built on pandas."""
import pandas as pd


def _clean(value):
    """Convert numpy/NaN values into JSON-safe Python values."""
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def find_outliers(series: pd.Series) -> int:
    """Count outliers in a numeric column using the 1.5 * IQR rule."""
    s = series.dropna()
    if len(s) < 4:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    return int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())


def analyze(df: pd.DataFrame) -> dict:
    """Profile a DataFrame and return a quality report with an overall 0-100 score."""
    rows, cols = df.shape
    if rows == 0 or cols == 0:
        raise ValueError("Dataset is empty")

    total_cells = rows * cols
    missing = df.isna().sum()
    duplicate_rows = int(df.duplicated().sum())

    numeric_cols = df.select_dtypes(include="number").columns
    column_reports, outlier_total, numeric_cells = {}, 0, 0
    for col in df.columns:
        info = {
            "dtype": str(df[col].dtype),
            "missing": int(missing[col]),
            "missing_pct": round(100 * missing[col] / rows, 2),
            "unique": int(df[col].nunique(dropna=True)),
        }
        if col in numeric_cols:
            outliers = find_outliers(df[col])
            outlier_total += outliers
            numeric_cells += int(df[col].notna().sum())
            info.update(
                outliers=outliers,
                min=_clean(df[col].min()),
                max=_clean(df[col].max()),
                mean=_clean(round(df[col].mean(), 4)) if df[col].notna().any() else None,
            )
        column_reports[col] = info

    completeness = 1 - missing.sum() / total_cells
    uniqueness = 1 - duplicate_rows / rows
    validity = 1 - (outlier_total / numeric_cells) if numeric_cells else 1.0
    score = round(100 * (0.5 * completeness + 0.3 * uniqueness + 0.2 * validity), 2)

    issues = []
    for col, info in column_reports.items():
        if info["missing_pct"] > 20:
            issues.append(f"Column '{col}' has {info['missing_pct']}% missing values")
        if info.get("outliers"):
            issues.append(f"Column '{col}' has {info['outliers']} outlier(s)")
    if duplicate_rows:
        issues.append(f"{duplicate_rows} duplicate row(s) found")

    return {
        "rows": rows,
        "columns": cols,
        "missing_cells": int(missing.sum()),
        "duplicate_rows": duplicate_rows,
        "outlier_values": outlier_total,
        "scores": {
            "completeness": round(100 * completeness, 2),
            "uniqueness": round(100 * uniqueness, 2),
            "validity": round(100 * validity, 2),
            "overall": score,
        },
        "issues": issues,
        "column_details": column_reports,
    }
