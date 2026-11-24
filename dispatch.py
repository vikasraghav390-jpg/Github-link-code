"""Simple hourly battery dispatch simulation and net-load alert metrics."""
import numpy as np
import pandas as pd

def simulate_dispatch(df: pd.DataFrame, capacity_kwh=200.0, max_power_kw=50.0,
                      efficiency=0.95, min_soc=0.10, initial_soc=0.50):
    soc = initial_soc * capacity_kwh
    rows = []
    for row in df.itertuples():
        pv = max(float(row.pv_kw), 0.0)
        load = max(float(row.load_kw), 0.0)
        net = load - pv
        charge = discharge = 0.0
        if net < 0:
            available_surplus = -net
            room_kw = max(0.0, (capacity_kwh - soc) / efficiency)
            charge = min(available_surplus, max_power_kw, room_kw)
            soc += charge * efficiency
        elif net > 0:
            available_energy_kw = max(0.0, (soc - min_soc * capacity_kwh) * efficiency)
            discharge = min(net, max_power_kw, available_energy_kw)
            soc -= discharge / efficiency
        soc = float(np.clip(soc, min_soc * capacity_kwh, capacity_kwh))
        grid_import = max(net - discharge, 0.0)
        grid_export = max(-net - charge, 0.0)
        rows.append({
            "timestamp": row.timestamp, "soc_pct": 100 * soc / capacity_kwh,
            "charge_kw": charge, "discharge_kw": discharge,
            "grid_import_kw": grid_import, "grid_export_kw": grid_export,
        })
    return pd.DataFrame(rows)

def alert_scores(actual_net, forecast_net, threshold_kw=40.0):
    actual_alert = np.asarray(actual_net) > threshold_kw
    predicted_alert = np.asarray(forecast_net) > threshold_kw
    tp = int(np.sum(actual_alert & predicted_alert))
    fp = int(np.sum(~actual_alert & predicted_alert))
    fn = int(np.sum(actual_alert & ~predicted_alert))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall}
