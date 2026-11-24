from forecast.generate_data import generate_dataset
from forecast.features import make_features
from forecast.dispatch import simulate_dispatch, alert_scores

def test_dataset_shape_and_completeness():
    df = generate_dataset()
    assert len(df) == 2160
    assert not df.isna().any().any()

def test_features_do_not_use_short_target_lags():
    df = generate_dataset()
    X = make_features(df, "pv_kw")
    assert "pv_kw_lag24" in X.columns
    assert "pv_kw_lag1" not in X.columns

def test_pv_is_nonnegative():
    df = generate_dataset()
    assert (df["pv_kw"] >= 0).all()

def test_dispatch_soc_bounds():
    df = generate_dataset().tail(100)
    result = simulate_dispatch(df)
    assert result["soc_pct"].between(10, 100).all()

def test_alert_metrics():
    result = alert_scores([45, 20, 50], [42, 45, 55], threshold_kw=40)
    assert result["tp"] == 2
    assert result["fp"] == 1
