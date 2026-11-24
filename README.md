# Community Microgrid Energy Forecasting

A reproducible software demonstration for community solar PV and electricity-load forecasting, battery dispatch simulation, and peak net-load alerts.

## What is included

- Reproducible 90-day synthetic hourly dataset (2,160 records; seed 42)
- Chronological day-ahead forecasting for PV generation and community load
- Persistence, Ridge Regression, Random Forest, and Gradient Boosting comparisons
- Streamlit dashboard with actual-versus-forecast plots, metrics, and dispatch simulation
- Basic telemetry validation, moving-average and stuck-sensor utilities
- Unit tests
- ESP32 / MQTT reference firmware templates and a Node-RED flow starter

> **Important scope note:** The dashboard runs in DEMO mode using synthetic data. It is not connected to physical ESP32 sensors, a live MQTT broker, a weather API, or a real community microgrid. Results from this demo must not be presented as field measurements. Hardware integration and bench-test results must be added only after those tests are actually performed.

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open the extracted folder in VS Code.
4. Open Terminal and run:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The dashboard opens in your browser. On first run, it creates the synthetic dataset, trains the models and saves outputs under `data/` and `models/`.

### Run tests

```bash
pytest -q
```

### Regenerate data and train models manually

```bash
python -m forecast.generate_data
python -m forecast.train
```

## GitHub upload

1. Sign in at https://github.com and create a **Public** repository named `community-microgrid-energy-forecasting`.
2. Extract this ZIP on your computer.
3. Open the extracted project folder in VS Code.
4. Open Terminal in that folder and run:

```bash
git init
git add .
git commit -m "Initial community microgrid forecasting project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/community-microgrid-energy-forecasting.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username. Do not paste a made-up repository URL into your submission; use the URL of the repository you actually created.

## Deploy the live dashboard (Streamlit Community Cloud)

1. Push this project to a public GitHub repository.
2. Sign in at https://share.streamlit.io/ using the account connected to GitHub.
3. Select **Create app**, choose your repository, branch `main`, and main file path `app/streamlit_app.py`.
4. Deploy. Wait for the build to finish.
5. Open the generated app URL and test it in a private/incognito browser window.
6. Submit that real URL alongside the GitHub repository URL.

The live app is a hosted synthetic-data demonstration. It is not live sensor telemetry.

## Project layout

```text
community-microgrid-energy-forecasting/
├── app/
│   └── streamlit_app.py
├── forecast/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── features.py
│   ├── train.py
│   └── dispatch.py
├── microgrid/
│   ├── __init__.py
│   └── edge_logic.py
├── firmware/
│   ├── node_a/
│   │   ├── main.py
│   │   └── config.example.py
│   └── README.md
├── nodered/
│   └── flows.json
├── tests/
│   ├── test_edge_logic.py
│   └── test_forecast.py
├── data/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── docs/
│   └── SCOPE_AND_TESTING.md
├── .gitignore
├── requirements.txt
└── README.md
```

## Data and model notes

- Synthetic community size assumption: 120 kWp rooftop PV.
- Dataset: 90 days × 24 hours, starting 1 August 2026.
- PV generation follows a daylight curve, cloud variation and a temperature derate.
- Load includes morning, midday and evening patterns, weekend uplift, cooling demand and noise.
- Weather forecast inputs are simulated with noise.
- Target-derived features use lags of at least 24 hours to avoid day-ahead leakage.
- Model evaluation uses a chronological split: first 72 days for training and last 18 days for testing.

## Security

- Never commit passwords, Wi-Fi credentials, MQTT credentials, Telegram tokens or chat IDs.
- Keep real device configuration in a local `config.py` excluded by `.gitignore`.
- Use TLS and individual broker credentials for real deployments.
- The included firmware and Node-RED files are reference starters, not a verified hardware deployment.

## Submission checklist

- [ ] Push source code to your own GitHub repository.
- [ ] Confirm the repository is accessible to the evaluator.
- [ ] Deploy the Streamlit dashboard and test its URL.
- [ ] Add a short screen-recording demo link if required.
- [ ] Add actual hardware test records only after performing the tests.
- [ ] Add mentor review and final version tag if required by your course.
