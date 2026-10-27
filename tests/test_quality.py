import pandas as pd
import pytest
from app.quality import analyze, find_outliers


def test_clean_dataset_scores_100():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": ["x", "y", "z", "w", "v"]})
    report = analyze(df)
    assert report["scores"]["overall"] == 100.0
    assert report["issues"] == []


def test_detects_missing_and_duplicates():
    df = pd.DataFrame({"a": [1, 1, None, 4], "b": ["x", "x", "y", "z"]})
    report = analyze(df)
    assert report["missing_cells"] == 1
    assert report["duplicate_rows"] == 1
    assert report["scores"]["overall"] < 100


def test_outlier_detection():
    assert find_outliers(pd.Series([10, 11, 12, 11, 10, 500])) == 1
    assert find_outliers(pd.Series([1, 2])) == 0


def test_empty_dataframe_raises():
    with pytest.raises(ValueError):
        analyze(pd.DataFrame())
