"""Leakage-aware feature creation for 24-hour-ahead forecasting."""
import numpy as np
import pandas as pd

def add_calendar_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts = pd.to_datetime(out["timestamp"])
    out["hour"] = ts.dt.hour
    out["dow"] = ts.dt.dayofweek
    out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24)
    out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24)
    out["weekend"] = (out["dow"] >= 5).astype(int)
    return out

def make_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    if target not in {"pv_kw", "load_kw"}:
        raise ValueError("target must be 'pv_kw' or 'load_kw'")
    data = add_calendar_columns(df)
    X = pd.DataFrame(index=data.index)
    X["hour_sin"] = data["hour_sin"]
    X["hour_cos"] = data["hour_cos"]
    X["dow"] = data["dow"]
    X["weekend"] = data["weekend"]
    for lag in (24, 25, 48, 168):
        X[f"{target}_lag{lag}"] = data[target].shift(lag)
    X["roll24_mean"] = data[target].shift(24).rolling(24).mean()
    X["irr_fc"] = data["irr_forecast"]
    X["temp_fc"] = data["temp_forecast"]
    return X.dropna()
