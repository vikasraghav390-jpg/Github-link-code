"""Train and compare persistence, Ridge, Random Forest and Gradient Boosting."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from forecast.generate_data import generate_dataset, DATA_PATH
from forecast.features import make_features
from forecast.dispatch import alert_scores

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"
RESULTS_PATH = ROOT / "data" / "model_metrics.json"

def _metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = mean_squared_error(actual, predicted) ** 0.5
    nmae = mae / max(float(np.mean(actual)), 1e-9) * 100
    return {"mae_kw": float(mae), "rmse_kw": float(rmse), "nmae_pct": float(nmae)}

def train_all(df=None, save=True):
    if df is None:
        if DATA_PATH.exists():
            df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
        else:
            df = generate_dataset()
    df = df.sort_values("timestamp").reset_index(drop=True)
    # Keep the last 18 days as test data; training ends before that period.
    split_time = pd.to_datetime(df["timestamp"].max()) - pd.Timedelta(days=18)
    output = {"models": {}, "predictions": {}, "split_time": str(split_time)}
    fitted = {}

    for target in ("pv_kw", "load_kw"):
        X = make_features(df, target)
        y = df.loc[X.index, target]
        train_mask = pd.to_datetime(df.loc[X.index, "timestamp"]) < split_time
        X_train, X_test = X.loc[train_mask], X.loc[~train_mask]
        y_train, y_test = y.loc[train_mask], y.loc[~train_mask]

        candidates = {
            "Ridge": Ridge(alpha=1.0),
            "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42, min_samples_leaf=2, n_jobs=-1),
            "Gradient Boosting": GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, random_state=42),
        }
        target_predictions = {}
        persistence = df.loc[X_test.index, target].shift(24)
        # For each target, a simple same-hour-yesterday baseline.
        persistence = df[target].shift(24).loc[X_test.index].to_numpy()
        target_predictions["Persistence"] = np.clip(persistence, 0, None)

        for name, model in candidates.items():
            model.fit(X_train, y_train)
            pred = np.clip(model.predict(X_test), 0, None)
            target_predictions[name] = pred
            fitted[f"{target}_{name.lower().replace(' ', '_')}"] = model

        output["models"][target] = {
            name: _metrics(y_test, pred) for name, pred in target_predictions.items()
        }
        output["predictions"][target] = {
            "timestamps": pd.to_datetime(df.loc[X_test.index, "timestamp"]).astype(str).tolist(),
            "actual": y_test.astype(float).tolist(),
            **{name: np.asarray(pred, dtype=float).tolist() for name, pred in target_predictions.items()}
        }

    pv = output["predictions"]["pv_kw"]
    load = output["predictions"]["load_kw"]
    forecast_net = np.asarray(load["Ridge"]) - np.asarray(pv["Ridge"])
    actual_net = np.asarray(load["actual"]) - np.asarray(pv["actual"])
    output["alert_metrics"] = alert_scores(actual_net, forecast_net)

    if save:
        MODEL_DIR.mkdir(exist_ok=True)
        for name, model in fitted.items():
            joblib.dump(model, MODEL_DIR / f"{name}.joblib")
        RESULTS_PATH.parent.mkdir(exist_ok=True)
        RESULTS_PATH.write_text(json.dumps(output, indent=2))
    return output

def main():
    if not DATA_PATH.exists():
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate_dataset().to_csv(DATA_PATH, index=False)
    result = train_all()
    print(json.dumps(result["models"], indent=2))
    print("Alert metrics:", result["alert_metrics"])

if __name__ == "__main__":
    main()
