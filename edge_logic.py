"""Small reusable edge-side validation and signal-processing helpers."""
from collections import deque
import statistics

REQUIRED_FIELDS = {"pv_v", "pv_i", "lux", "temperature_c"}

def validate_payload(payload):
    if not isinstance(payload, dict) or not REQUIRED_FIELDS.issubset(payload):
        return False
    try:
        pv_v = float(payload["pv_v"])
        pv_i = float(payload["pv_i"])
        lux = float(payload["lux"])
        temp = float(payload["temperature_c"])
    except (TypeError, ValueError):
        return False
    return 0 < pv_v < 24 and 0 <= pv_i < 3.2 and lux >= 0 and -20 < temp < 80

def moving_average(values):
    values = list(values)
    if not values:
        raise ValueError("values cannot be empty")
    return sum(values) / len(values)

def is_stuck_sensor(values, window=30):
    values = list(values)[-window:]
    return len(values) == window and len(set(values)) == 1

def estimate_cell_soc(cell_voltage):
    """Linear illustrative estimate between 3.0 V (0%) and 4.2 V (100%)."""
    return round(max(0.0, min(100.0, (float(cell_voltage) - 3.0) / 1.2 * 100.0)), 2)
