import matplotlib.pyplot as plt
import numpy as np
import fastf1.plotting

import config

COMPOUND_COLORS = {"SOFT": "#e8002d", "MEDIUM": "#ffd12e", "HARD": "#f0f0ec",
                   "INTERMEDIATE": "#39b54a", "WET": "#0067ad"}
SOURCE = "Data: FastF1, live timing"


def _setup():
    fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme="fastf1")


def _finish(fig, ax, title, path):
    ax.set_title(title, loc="left")
    fig.text(0.01, 0.01, SOURCE, color="grey", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def degradation_scatter(green_laps, curves, path):
    _setup()
    fig, ax = plt.subplots(figsize=(12, 7))
    for compound, g in green_laps.groupby("Compound"):
        color = COMPOUND_COLORS[compound]
        ax.scatter(g["stint_age"], g["fuel_corrected_laptime"], s=15, alpha=0.5, color=color, label=compound.lower())
        ax.plot(curves[compound][:, 0], curves[compound][:, 1], color=color, lw=1.6)
    ax.set_xlabel("tire age (laps in stint)")
    ax.set_ylabel("fuel-corrected lap time (s)")
    ax.legend(loc="upper left")
    _finish(fig, ax, f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, race. Fuel-corrected lap time vs tire age", path)


def stint_view(green_laps, path):
    _setup()
    fig, ax = plt.subplots(figsize=(12, 7))
    for (driver, stint), g in green_laps.groupby(["Driver", "Stint"]):
        ax.plot(g["LapNumber"], g["fuel_corrected_laptime"], lw=1.2, alpha=0.7,
                color=COMPOUND_COLORS[g["Compound"].iloc[0]])
    ax.set_xlabel("race lap")
    ax.set_ylabel("fuel-corrected lap time (s)")
    for compound in ("MEDIUM", "HARD"):
        ax.plot([], [], color=COMPOUND_COLORS[compound], label=compound.lower())
    ax.legend(loc="upper right")
    _finish(fig, ax, f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, race. Green-flag stints, one line per driver stint", path)


def error_comparison(summary, path):
    _setup()
    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(summary))
    ax.bar(x - 0.2, summary["base_err"], width=0.4, color="#9a9a9a", label="baseline (compound mean slope)")
    ax.bar(x + 0.2, summary["mixed_err"], width=0.4, color="#2a9d8f", label="mixed model")
    ax.set_xticks(x, [i.lower() for i in summary.index])
    ax.set_ylabel("held-out mean absolute error (s per lap)")
    ax.set_ylim(0, summary[["base_err", "mixed_err"]].to_numpy().max() * 1.25)
    ax.legend(loc="upper right")
    _finish(fig, ax, f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, race. Held-out stint error, baseline vs mixed model", path)
