from pathlib import Path
import sys
import json
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from forecast.generate_data import generate_dataset, DATA_PATH
from forecast.train import train_all
from forecast.dispatch import simulate_dispatch

st.set_page_config(page_title="Community Microgrid Forecasting", page_icon="⚡", layout="wide")
st.title("⚡ Community Microgrid Energy Forecasting")
st.caption("Synthetic-data demonstration • Day-ahead PV and load forecasts • Battery dispatch simulation")

@st.cache_data
def load_demo_data():
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    df = generate_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    return df

@st.cache_data
def load_results():
    result_path = ROOT / "data" / "model_metrics.json"
    if result_path.exists():
        try:
            return json.loads(result_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return train_all(save=True)

with st.spinner("Preparing the synthetic dataset and forecasting models..."):
    data = load_demo_data()
    results = load_results()

st.warning("DEMO MODE: all values are generated synthetic data, not live sensor readings or field measurements.")

latest = data.iloc[-1]
c1, c2, c3, c4 = st.columns(4)
c1.metric("PV generation (latest)", f"{latest.pv_kw:.1f} kW")
c2.metric("Community load (latest)", f"{latest.load_kw:.1f} kW")
c3.metric("Net load (latest)", f"{latest.load_kw-latest.pv_kw:.1f} kW")
c4.metric("Dataset duration", "90 days")

st.subheader("Synthetic telemetry history")
history_days = st.slider("History window (days)", min_value=1, max_value=30, value=7)
history = data.tail(history_days * 24).set_index("timestamp")
st.line_chart(history[["pv_kw", "load_kw"]], y_label="Power (kW)")

st.subheader("Day-ahead model comparison")
target_choice = st.selectbox("Forecast target", ["pv_kw", "load_kw"], format_func=lambda x: "PV generation" if x == "pv_kw" else "Community load")
metric_rows = []
for model_name, metric in results["models"][target_choice].items():
    metric_rows.append({"Model": model_name, "MAE (kW)": metric["mae_kw"], "RMSE (kW)": metric["rmse_kw"], "nMAE (%)": metric["nmae_pct"]})
metrics_df = pd.DataFrame(metric_rows).sort_values("MAE (kW)")
st.dataframe(metrics_df, use_container_width=True, hide_index=True)

pred = results["predictions"][target_choice]
forecast_df = pd.DataFrame({
    "timestamp": pd.to_datetime(pred["timestamps"]),
    "Actual": pred["actual"],
    "Ridge forecast": pred["Ridge"],
    "Persistence baseline": pred["Persistence"],
}).set_index("timestamp")
st.line_chart(forecast_df, y_label="Power (kW)")

st.subheader("Battery dispatch simulation")
test = data.tail(len(results["predictions"]["pv_kw"]["actual"])).copy()
dispatch = simulate_dispatch(test)
d1, d2, d3 = st.columns(3)
d1.metric("Simulated battery capacity", "200 kWh")
d2.metric("Maximum charge/discharge", "50 kW")
d3.metric("Starting state of charge", "50%")
st.line_chart(dispatch.set_index("timestamp")[["soc_pct"]], y_label="State of charge (%)")
st.line_chart(dispatch.set_index("timestamp")[["grid_import_kw", "grid_export_kw"]], y_label="Grid power (kW)")

alert = results["alert_metrics"]
st.subheader("Peak net-load alert evaluation")
a1, a2, a3, a4 = st.columns(4)
a1.metric("Precision", f"{alert['precision']*100:.1f}%")
a2.metric("Recall", f"{alert['recall']*100:.1f}%")
a3.metric("True positives", alert["tp"])
a4.metric("False positives", alert["fp"])
st.caption("Alert rule: forecast net load (load minus PV) exceeds 40 kW. Metrics are computed on the synthetic test window.")

with st.expander("Project scope and limitations"):
    st.markdown("""
    - Synthetic dataset: 90 days × 24 hourly samples, fixed seed 42.
    - Forecast weather inputs are simulated noisy proxies; no live weather API is connected.
    - No physical ESP32, inverter, mains meter or MQTT broker is connected by this hosted demo.
    - Battery dispatch is a simplified rule-based simulation; it does not model tariffs, degradation or inverter constraints.
    - Hardware integration tests must be completed and documented separately before making hardware-performance claims.
    """)
