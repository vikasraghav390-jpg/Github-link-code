# Scope, evaluation and testing notes

## Software demonstration

This repository implements a synthetic 90-day hourly dataset, day-ahead forecasting feature generation, model comparison, a simplified battery dispatch simulation, a Streamlit dashboard and unit tests.

The report's design compares persistence, Ridge Regression, Random Forest (200 trees) and Gradient Boosting (300 estimators, depth 3, learning rate 0.05), using a chronological first-72-days / last-18-days split. This implementation follows that broad design and saves its own results when run; use the freshly generated metrics rather than copying report numbers as if they were produced by this run.

## Hardware work still required

- Calibrate INA219 voltage/current measurements against a multimeter.
- Calibrate battery voltage divider against a reference meter.
- Calibrate BH1750 lux as an irradiance proxy.
- Complete and test both ESP32 nodes.
- Run one-hour telemetry soak, Wi-Fi-drop, power-cycle, sensor-disconnect, low-battery, over-temperature, broker-outage and end-to-end latency tests.
- Record measured results, dates, equipment and test conditions.

No hardware test outcomes are asserted by this repository.

## Software test command

```bash
pytest -q
```
