"""Create a reproducible synthetic 90-day community microgrid dataset."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic_microgrid_hourly.csv"

def generate_dataset(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    index = pd.date_range("2026-08-01", periods=90 * 24, freq="h")
    hour = index.hour.to_numpy()
    dow = index.dayofweek.to_numpy()
    day_index = np.arange(len(index)) // 24

    # Slowly varying daily cloud factor plus hourly variation.
    daily_idx = np.arange(90)
    daily_cloud = np.clip(
        0.72 + 0.18 * np.sin(2 * np.pi * daily_idx / 13)
        + rng.normal(0, 0.10, 90), 0.25, 1.0
    )
    cloud = np.clip(daily_cloud[day_index] + rng.normal(0, 0.07, len(index)), 0.15, 1.0)

    daylight = np.maximum(0, np.sin(np.pi * (hour - 6) / 12))
    temp = 29 + 5 * np.sin(2 * np.pi * (hour - 8) / 24) + rng.normal(0, 1.5, len(index))
    irradiance = 900 * daylight * cloud
    pv_kw = 120 * daylight * cloud * 0.82
    pv_kw *= np.maximum(0.70, 1 - 0.004 * np.maximum(temp - 25, 0))
    pv_kw += rng.normal(0, 1.0, len(index))
    pv_kw = np.clip(pv_kw, 0, None)

    morning_peak = 13 * np.exp(-0.5 * ((hour - 8) / 1.8) ** 2)
    midday = 7 * np.exp(-0.5 * ((hour - 13) / 3.0) ** 2)
    evening_peak = 25 * np.exp(-0.5 * ((hour - 20) / 2.2) ** 2)
    cooling = 1.8 * np.maximum(temp - 28, 0)
    weekend_factor = np.where(dow >= 5, 1.10, 1.0)
    load_kw = (28 + morning_peak + midday + evening_peak + cooling) * weekend_factor
    load_kw += rng.normal(0, 2.0, len(index))
    load_kw = np.clip(load_kw, 8, None)

    # Noisy forecast proxies, not a live weather service.
    irr_forecast = np.clip(irradiance * (1 + rng.normal(0, 0.12, len(index))), 0, None)
    temp_forecast = temp + rng.normal(0, 1.0, len(index))

    return pd.DataFrame({
        "timestamp": index,
        "pv_kw": pv_kw,
        "load_kw": load_kw,
        "irradiance": irradiance,
        "temperature_c": temp,
        "irr_forecast": irr_forecast,
        "temp_forecast": temp_forecast,
    })

def main():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    df.to_csv(DATA_PATH, index=False)
    print(f"Saved {len(df)} hourly rows to {DATA_PATH}")

if __name__ == "__main__":
    main()
