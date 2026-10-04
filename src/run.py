import warnings
import pandas as pd
from src.load import load_race
from src.clean import clean_laps, write_data_quality
from src import model, plots


def main():
    warnings.filterwarnings("ignore")
    session, laps = load_race()
    total_laps = int(laps["LapNumber"].max())
    green_laps, dropped, log = clean_laps(laps, total_laps)
    write_data_quality("data_quality.md", log, dropped)

    slopes = model.stint_slopes(green_laps)
    slope_ci = model.bootstrap_mean_slope(slopes)
    errors = model.summarise_errors(model.heldout_errors(green_laps))
    sensitivity = model.fuel_sensitivity(green_laps, total_laps)

    plots.degradation_scatter(green_laps, model.pooled_lowess(green_laps), "figures/degradation_scatter.png")
    plots.stint_view(green_laps, "figures/stint_view.png")
    plots.error_comparison(errors, "figures/error_comparison.png")

    pd.options.display.float_format = "{:.3f}".format
    with open("results.md", "w") as f:
        f.write("laps per step\n" + "\n".join(f"{s}: dropped {d}, remaining {r}" for s, d, r in log))
        f.write("\n\nbaseline slope per compound (s per lap, bootstrap over stints)\n" + slope_ci.to_string())
        f.write("\n\nheld-out stint error (s per lap)\n" + errors.to_string())
        f.write("\n\nfuel sensitivity\n" + sensitivity.to_string(index=False) + "\n")
    print(open("results.md").read())


if __name__ == "__main__":
    main()
