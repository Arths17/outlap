import pandas as pd
import config


def add_stint_age(laps):
    # tyrelife includes laps on used sets, so count laps since the stint began
    laps = laps.copy()
    laps["stint_age"] = laps.groupby(["Driver", "Stint"]).cumcount() + 1
    return laps


def fuel_corrected(laps, total_laps, fuel_effect=None, fuel_start=None):
    fuel_effect = config.FUEL_EFFECT_S_PER_KG if fuel_effect is None else fuel_effect
    fuel_start = config.FUEL_START_KG if fuel_start is None else fuel_start
    burned_kg = fuel_start * (laps["LapNumber"] - 1) / total_laps  # linear burn
    return laps["LapTime"].dt.total_seconds() + fuel_effect * burned_kg


def clean_laps(laps, total_laps):
    """returns green laps, every dropped lap with its reason, and a (step, dropped, remaining) log"""
    laps = add_stint_age(laps)
    dropped = []
    log = [("all laps", 0, len(laps))]
    fastest = laps["LapTime"].min()
    masks = {
        "lap 1, standing start skews the time": lambda d: d["LapNumber"] == 1,
        "in or out lap": lambda d: d["PitInTime"].notna() | d["PitOutTime"].notna(),
        "non-green track status": lambda d: d["TrackStatus"] != "1",
        "deleted lap": lambda d: d["Deleted"].notna() & (d["Deleted"] != False),
        f"slower than {config.QUICKLAP_THRESHOLD:.0%} of fastest lap":
            lambda d: d["LapTime"] > fastest * config.QUICKLAP_THRESHOLD,
        "missing laptime or compound": lambda d: d["LapTime"].isna() | d["Compound"].isna(),
    }
    remaining = laps
    for reason, mask in masks.items():
        hit = mask(remaining)
        gone = remaining[hit].assign(drop_reason=reason)
        dropped.append(gone)
        remaining = remaining[~hit]
        log.append((reason, len(gone), len(remaining)))

    # stints too short to model
    n_clean = remaining.groupby(["Driver", "Stint"])["LapNumber"].transform("count")
    short = remaining[n_clean < config.MIN_STINT_LAPS].assign(
        drop_reason=f"stint under {config.MIN_STINT_LAPS} clean laps")
    dropped.append(short)
    remaining = remaining[n_clean >= config.MIN_STINT_LAPS].copy()
    log.append((f"stint under {config.MIN_STINT_LAPS} clean laps", len(short), len(remaining)))

    # a compound with a handful of stints gives no usable slope or interval
    stints_per_compound = remaining.groupby("Compound")["Stint"].transform(
        lambda col: remaining.loc[col.index].groupby("Driver")["Stint"].nunique().sum())
    rare = remaining[stints_per_compound < config.MIN_STINTS_PER_COMPOUND].assign(
        drop_reason=f"compound with under {config.MIN_STINTS_PER_COMPOUND} clean stints")
    dropped.append(rare)
    remaining = remaining[stints_per_compound >= config.MIN_STINTS_PER_COMPOUND].copy()
    log.append((f"compound with under {config.MIN_STINTS_PER_COMPOUND} clean stints", len(rare), len(remaining)))

    remaining["fuel_corrected_laptime"] = fuel_corrected(remaining, total_laps)
    return remaining, pd.concat(dropped), log


def write_data_quality(path, log, dropped):
    lines = ["# data quality", "",
             f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, race. Every dropped lap and why.", "",
             "## laps remaining after each step", "",
             "| step | dropped | remaining |", "|---|---|---|"]
    lines += [f"| {s} | {d} | {r} |" for s, d, r in log]
    lines += ["", "## dropped laps per driver and reason", ""]
    table = dropped.groupby(["Driver", "drop_reason"]).size().unstack(fill_value=0)
    lines += ["```", table.to_string(), "```"]
    lines += ["", "## stints excluded for being too short", ""]
    short = dropped[dropped["drop_reason"].str.startswith("stint under")]
    for (drv, stint), g in pd.concat([short, dropped[dropped["drop_reason"].str.startswith("compound")]]).groupby(["Driver", "Stint"]):
        lines.append(f"- {drv} stint {int(stint)}: {len(g)} clean laps")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
