import numpy as np
import pandas as pd
import config
from src.clean import clean_laps, fuel_corrected


def make_laps(n_laps=30, drivers=("AAA", "BBB", "CCC", "DDD", "EEE")):
    rows = []
    for d in drivers:
        for lap in range(1, n_laps + 1):
            rows.append(dict(Driver=d, LapNumber=lap, Stint=1, Compound="MEDIUM", TrackStatus="1",
                             LapTime=pd.Timedelta(seconds=90.0), PitInTime=pd.NaT, PitOutTime=pd.NaT,
                             Deleted=None))
    return pd.DataFrame(rows)


def test_lap_one_and_pit_laps_are_dropped():
    laps = make_laps()
    laps.loc[(laps.Driver == "AAA") & (laps.LapNumber == 10), "PitInTime"] = pd.Timedelta(minutes=20)
    laps.loc[(laps.Driver == "AAA") & (laps.LapNumber == 11), "PitOutTime"] = pd.Timedelta(minutes=21)
    green, dropped, _ = clean_laps(laps, 30)
    assert green["LapNumber"].min() > 1
    aaa = green[green.Driver == "AAA"]["LapNumber"].tolist()
    assert 10 not in aaa and 11 not in aaa


def test_safety_car_and_slow_laps_are_dropped():
    laps = make_laps()
    laps.loc[(laps.Driver == "BBB") & (laps.LapNumber == 5), "TrackStatus"] = "4"
    laps.loc[(laps.Driver == "CCC") & (laps.LapNumber == 6), "LapTime"] = pd.Timedelta(seconds=110.0)
    green, _, _ = clean_laps(laps, 30)
    assert 5 not in green[green.Driver == "BBB"]["LapNumber"].tolist()
    assert 6 not in green[green.Driver == "CCC"]["LapNumber"].tolist()


def test_fuel_correction_removes_a_known_fuel_trend():
    # synthetic race where the only trend is fuel burn: 0.03 s/kg, so lap times fall linearly
    total_laps = 50
    lap_numbers = np.arange(1, total_laps + 1)
    burned = config.FUEL_START_KG * (lap_numbers - 1) / total_laps
    laps = pd.DataFrame(dict(LapNumber=lap_numbers,
                             LapTime=pd.to_timedelta(95.0 - 0.03 * burned, unit="s")))
    corrected = fuel_corrected(laps, total_laps, fuel_effect=0.03)
    assert np.ptp(corrected) < 1e-6
