from microgrid.edge_logic import validate_payload, moving_average, is_stuck_sensor, estimate_cell_soc

def test_valid_payload():
    assert validate_payload({"pv_v": 12, "pv_i": 1.2, "lux": 500, "temperature_c": 30})

def test_reject_out_of_range_voltage():
    assert not validate_payload({"pv_v": 48, "pv_i": 1.2, "lux": 500, "temperature_c": 30})

def test_reject_missing_field():
    assert not validate_payload({"pv_v": 12, "pv_i": 1.2, "lux": 500})

def test_moving_average():
    assert moving_average(range(1, 11)) == 5.5

def test_stuck_sensor_detection():
    assert is_stuck_sensor([2.0] * 30)

def test_normal_sensor_not_stuck():
    assert not is_stuck_sensor([float(i) for i in range(30)])

def test_soc_midpoint():
    assert abs(estimate_cell_soc(3.6) - 50.0) < 1e-9
