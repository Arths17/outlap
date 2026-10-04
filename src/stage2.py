import warnings
import pandas as pd

from src import model, plots
from src.clean import clean_laps
from src.features import FEATURE_GROUPS, extract_lap_features, previous_lap_features
from src.load import load_race, load_quali


def ablation_table(green_laps):
    prev_groups = {g: [f"prev_{c}" for c in cols] for g, cols in FEATURE_GROUPS.items()}
    every = [c for cols in prev_groups.values() for c in cols]
    # same laps for every model, otherwise the comparison is not like for like
    laps = green_laps.dropna(subset=every)
    sets = {"stage 1 mixed": []}
    sets.update({f"+ {g}": cols for g, cols in prev_groups.items()})
    sets["+ all groups"] = every
    errors = model.heldout_errors(laps, {k.replace(" ", "_") + "_err": v for k, v in sets.items()})
    rows = [dict(model="baseline (compound mean slope)", mae=errors["base_err"].mean(), change=None, ci=None)]
    ref = "stage_1_mixed_err"
    for name in sets:
        col = name.replace(" ", "_") + "_err"
        diff = model.paired_difference_ci(errors, col, ref) if col != ref else None
        rows.append(dict(model=name, mae=errors[col].mean(),
                         change=None if diff is None else diff[0],
                         ci=None if diff is None else f"{diff[1]:+.3f} to {diff[2]:+.3f}"))
    return pd.DataFrame(rows), len(errors)


# placed by hand from the delta trace: distance in m, delta in s
QUALI_NOTES = [(1050, 0.10, "LEC gains 0.17 s, 800 to 1000 m", "left"),
               (3200, 0.16, "ANT gains 0.16 s, T14 to T15", "left"),
               (5420, -0.06, "LEC gains 0.22 s, 5200 m to T17", "right")]


def qualifying_figures(quali, corners):
    fast = quali.laps.pick_quicklaps().sort_values("LapTime").drop_duplicates("Driver").head(2)
    lap_a, lap_b = [row for _, row in fast.iterlaps()]
    plots.qualifying_stack(quali, lap_a, lap_b, corners, "figures/qualifying_stack.png", QUALI_NOTES)
    plots.track_map(lap_a, "Speed", "figures/track_speed.png", "speed (km/h)")
    plots.track_map(lap_a, "nGear", "figures/track_gear.png", "gear")


def main():
    warnings.filterwarnings("ignore")
    quali = load_quali()
    corners = quali.get_circuit_info().corners
    session, laps = load_race()
    total_laps = int(laps["LapNumber"].max())
    race_features = extract_lap_features(laps, corners)
    green_laps, _, _ = clean_laps(laps, total_laps)
    green_laps = green_laps.merge(previous_lap_features(race_features), on=["Driver", "LapNumber"], how="left")
    table, n_laps = ablation_table(green_laps)
    both = race_features.merge(laps[["Driver", "LapNumber", "SpeedST"]], on=["Driver", "LapNumber"])
    both = both[both["top_speed"] > 250]  # drops pit-lane and slow laps where no straight was driven flat out
    st_corr = both["top_speed"].corr(both["SpeedST"])
    st_gap = (both["top_speed"] - both["SpeedST"]).mean()
    pd.options.display.float_format = "{:.3f}".format
    qualifying_figures(quali, corners)
    with open("results_stage2.md", "w") as f:
        f.write(f"feature ablation, {n_laps} held-out laps scored\n")
        f.write("change is the mean error change versus stage 1 mixed, interval is a bootstrap over stints\n\n")
        f.write(table.to_string(index=False) + "\n")
        f.write(f"\ntop_speed vs SpeedST over {len(both)} laps: correlation {st_corr:.2f}, "
                f"mean gap {st_gap:.1f} km/h\n")
    print(open("results_stage2.md").read())
    return table, n_laps


if __name__ == "__main__":
    main()
