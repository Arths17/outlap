import numpy as np
import pandas as pd

import config

# lap-level features grouped so the ablation can add them one group at a time
FEATURE_GROUPS = {
    "speed": ["top_speed", "full_throttle_frac"],
    "braking": ["n_brake_zones", "brake_time_s", "mean_brake_onset_m"],
    "corners": ["mean_apex_speed", "mean_throttle_pickup_m"],
    "lift_coast": ["lift_coast_m"],
    "gears": ["shift_count", "mean_apex_gear"],
}
ALL_FEATURES = [f for cols in FEATURE_GROUPS.values() for f in cols]


def mask_throttle(throttle):
    # 104 means error or no data
    return throttle.where(throttle <= 100)


def runs(flag):
    """first and last index of each consecutive run of True"""
    padded = np.concatenate(([0], np.asarray(flag, dtype=np.int8), [0]))
    edges = np.diff(padded)
    return np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1


def brake_zones(trace):
    starts, ends = runs(trace["Brake"].to_numpy())
    dist = trace["Distance"].to_numpy()
    return [(dist[s], dist[e]) for s, e in zip(starts, ends)]


def lift_and_coast(trace):
    # off full throttle with no brake, then straight into a braking zone
    throttle = mask_throttle(trace["Throttle"]).to_numpy()
    brake = trace["Brake"].to_numpy()
    dist = trace["Distance"].to_numpy()
    coasting = (throttle < config.FULL_THROTTLE_PCT) & ~brake
    stretches = []
    for s, e in zip(*runs(coasting)):
        braking_next = e + 1 < len(brake) and brake[e + 1]
        if braking_next and dist[e] - dist[s] > config.LIFT_COAST_MIN_M:
            stretches.append((dist[s], dist[e]))
    return stretches


def corner_table(trace, corners):
    """apex speed, gear, throttle pickup and brake onset for each corner on one lap"""
    dist = trace["Distance"].to_numpy()
    speed = trace["Speed"].to_numpy()
    gear = trace["nGear"].to_numpy()
    throttle = mask_throttle(trace["Throttle"]).to_numpy()
    zones = brake_zones(trace)
    rows = []
    for corner in corners.itertuples():
        near = np.flatnonzero(np.abs(dist - corner.Distance) <= config.APEX_WINDOW_M)
        row = dict(corner=corner.Number, apex_speed=np.nan, apex_gear=np.nan,
                   throttle_pickup_m=np.nan, brake_onset_m=np.nan)
        if len(near):
            apex = near[np.argmin(speed[near])]
            row["apex_speed"], row["apex_gear"] = speed[apex], gear[apex]
            later = np.flatnonzero((np.arange(len(dist)) >= apex) & (throttle > 50)
                                   & (dist - dist[apex] <= config.PICKUP_SEARCH_M))
            if len(later):
                row["throttle_pickup_m"] = dist[later[0]] - dist[apex]
        # the zone has to end near the apex, otherwise a lift-only corner borrows the previous corner's braking
        before = [s for s, e in zones if corner.Distance - config.BRAKE_ONSET_SEARCH_M <= s <= corner.Distance
                  and corner.Distance <= e + config.APEX_WINDOW_M]
        if before:
            row["brake_onset_m"] = corner.Distance - before[-1]
        rows.append(row)
    return pd.DataFrame(rows)


def lap_features(trace, corners):
    throttle = mask_throttle(trace["Throttle"])
    dt = trace["Time"].dt.total_seconds().diff().fillna(0).to_numpy()
    valid = throttle.notna().to_numpy()
    full = (throttle >= config.FULL_THROTTLE_PCT).to_numpy()
    table = corner_table(trace, corners)
    lift = lift_and_coast(trace)
    return dict(
        top_speed=trace["Speed"].max(),
        full_throttle_frac=dt[full & valid].sum() / dt[valid].sum(),
        n_brake_zones=len(brake_zones(trace)),
        brake_time_s=dt[trace["Brake"].to_numpy()].sum(),
        mean_brake_onset_m=table["brake_onset_m"].mean(),
        mean_apex_speed=table["apex_speed"].mean(),
        mean_throttle_pickup_m=table["throttle_pickup_m"].mean(),
        lift_coast_m=sum(e - s for s, e in lift),
        shift_count=int((trace["nGear"].diff().fillna(0) != 0).sum()),
        mean_apex_gear=table["apex_gear"].mean(),
    )


def extract_lap_features(laps, corners):
    rows = []
    for _, lap in laps.iterlaps():
        # distance is integrated one lap at a time, error grows with length
        trace = lap.get_car_data().add_distance()
        if len(trace) < 50:
            continue
        rows.append(dict(Driver=lap["Driver"], LapNumber=lap["LapNumber"], **lap_features(trace, corners)))
    return pd.DataFrame(rows)


def previous_lap_features(features):
    # features of lap n-1 only, so nothing computed from the lap being predicted
    prev = features.copy()
    prev["LapNumber"] = prev["LapNumber"] + 1
    return prev.rename(columns={c: f"prev_{c}" for c in ALL_FEATURES})
