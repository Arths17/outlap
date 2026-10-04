import fastf1
import config


def load_race():
    fastf1.Cache.enable_cache(config.CACHE_DIR)
    session = fastf1.get_session(config.YEAR, config.GRAND_PRIX, "R")
    session.load(laps=True, telemetry=True, weather=True, messages=False)
    laps = session.laps.reset_index(drop=True)
    # per-lap weather so track temperature can be a model feature
    laps["TrackTemp"] = laps.get_weather_data().reset_index(drop=True)["TrackTemp"]
    needed = ["LapTime", "LapNumber", "Driver", "Team", "Stint", "Compound",
              "TyreLife", "TrackStatus", "PitInTime", "PitOutTime", "Deleted"]
    missing = [c for c in needed if c not in laps.columns]
    if missing:
        raise ValueError(f"laps table is missing {missing}")
    return session, laps
