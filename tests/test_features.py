import numpy as np
import pandas as pd

from src.features import brake_zones, lift_and_coast, lap_features, mask_throttle


def make_trace(throttle, brake, step_m=10.0):
    n = len(throttle)
    return pd.DataFrame(dict(
        Distance=np.arange(n) * step_m,
        Speed=np.full(n, 200.0),
        Throttle=pd.Series(throttle, dtype=float),
        Brake=np.asarray(brake, dtype=bool),
        nGear=np.full(n, 5),
        Time=pd.to_timedelta(np.arange(n) * 0.1, unit="s")))


def test_two_brake_zones_are_found_with_their_distances():
    brake = [0] * 5 + [1] * 4 + [0] * 6 + [1] * 3 + [0] * 5
    zones = brake_zones(make_trace([100] * len(brake), brake))
    assert zones == [(50.0, 80.0), (150.0, 170.0)]


def test_lift_and_coast_only_counts_stretches_that_end_in_braking():
    # 5 samples at 60 percent then brake: lift and coast. later 5 samples at 60 then back to full: corner exit, not counted
    throttle = [100] * 3 + [60] * 5 + [0] * 3 + [100] * 3 + [60] * 5 + [100] * 3
    brake = [0] * 8 + [1] * 3 + [0] * 11
    stretches = lift_and_coast(make_trace(throttle, brake))
    assert stretches == [(30.0, 70.0)]


def test_short_lift_below_the_distance_threshold_is_ignored():
    throttle = [100] * 3 + [60, 60] + [0] * 3 + [100] * 3
    brake = [0] * 5 + [1] * 3 + [0] * 3
    assert lift_and_coast(make_trace(throttle, brake)) == []  # 10 m between samples, one step is only 10 m


def test_throttle_error_value_is_masked_not_counted_as_full_throttle():
    assert mask_throttle(pd.Series([100.0, 104.0, 50.0])).isna().tolist() == [False, True, False]
    corners = pd.DataFrame(dict(Number=[1], Distance=[50.0]))
    trace = make_trace([100, 100, 104, 104, 0, 0, 100, 100], [0] * 8)
    # time weighted, the first sample has no elapsed time: 0.3 s full throttle of 0.5 s valid.
    # counting the 104 samples as full throttle would give 0.5 / 0.7
    assert abs(lap_features(trace, corners)["full_throttle_frac"] - 0.6) < 1e-9
