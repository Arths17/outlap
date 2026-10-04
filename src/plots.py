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


def _lap_style(session, driver):
    return fastf1.plotting.get_driver_style(driver, style=["color", "linestyle"], session=session)


def qualifying_stack(session, lap_a, lap_b, corners, path, notes=()):
    """speed, throttle, brake, gear and cumulative delta for two laps on one distance axis"""
    from fastf1.utils import delta_time
    _setup()
    tel = {lap["Driver"]: lap.get_car_data().add_distance() for lap in (lap_a, lap_b)}
    delta, ref_tel, _ = delta_time(lap_a, lap_b)
    fig, axes = plt.subplots(5, 1, figsize=(12, 12), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1, 0.8, 1, 1.4]})
    for lap in (lap_a, lap_b):
        drv, t = lap["Driver"], tel[lap["Driver"]]
        style = _lap_style(session, drv)
        label = f"{drv} {lap['LapTime'].total_seconds():.3f}"
        axes[0].plot(t["Distance"], t["Speed"], lw=1.4, label=label, **style)
        axes[1].plot(t["Distance"], t["Throttle"].where(t["Throttle"] <= 100), lw=1.4, **style)
        axes[2].step(t["Distance"], t["Brake"].astype(int), where="post", lw=1.4, **style)
        axes[3].step(t["Distance"], t["nGear"], where="post", lw=1.4, **style)
    axes[4].plot(ref_tel["Distance"], delta, lw=1.4, color="white")
    axes[4].axhline(0, color="grey", lw=0.8)
    for ax, name in zip(axes, ["speed (km/h)", "throttle (%)", "brake (on/off)", "gear",
                               f"{lap_b['Driver']} minus {lap_a['Driver']} (s)"]):
        ax.set_ylabel(name)
        for d in corners["Distance"]:
            ax.axvline(d, color="grey", ls=":", lw=0.8)
    last = -1e9
    level = 0
    for num, d in zip(corners["Number"], corners["Distance"]):
        # stagger labels of neighbouring corners so 10/11 and 16/17 stay readable
        level = (level + 1) % 2 if d - last < 150 else 0
        last = d
        axes[4].text(d, 0.02 + 0.1 * level, str(num), transform=axes[4].get_xaxis_transform(),
                     color="grey", fontsize=8, ha="center", va="bottom")
    axes[2].set_yticks([0, 1], ["off", "on"])
    axes[0].legend(loc="lower right")
    axes[4].set_xlabel("distance along lap (m)")
    axes[4].set_ylim(np.min(delta) - 0.08, np.max(delta) + 0.08)
    for x, y, text, align in notes:
        axes[4].text(x, y, text, fontsize=9, color="white", ha=align)
    _finish(fig, axes[0], f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, qualifying. "
                          f"{lap_a['Driver']} vs {lap_b['Driver']}, fastest laps", path)
    return delta, ref_tel


def track_map(lap, channel, path, label):
    from matplotlib.collections import LineCollection
    _setup()
    pos = lap.get_telemetry()
    points = np.array([pos["X"], pos["Y"]]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    fig = plt.figure(figsize=(12, 7))
    ax = fig.add_axes([0.1, 0.04, 0.6, 0.86])  # explicit layout, equal aspect shrinks the box inside it
    cax = fig.add_axes([0.78, 0.2, 0.02, 0.6])
    lc = LineCollection(segments, cmap="viridis", linewidth=4)
    lc.set_array(pos[channel].to_numpy()[:-1])
    ax.add_collection(lc)
    ax.set_xlim(pos["X"].min() - 300, pos["X"].max() + 300)
    ax.set_ylim(pos["Y"].min() - 300, pos["Y"].max() + 300)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.colorbar(lc, cax=cax, label=label)
    fig.suptitle(f"{config.YEAR} {config.GRAND_PRIX} Grand Prix, qualifying. {lap['Driver']} fastest lap, {label}",
                 x=0.01, ha="left", fontsize=plt.rcParams["axes.titlesize"])
    fig.text(0.01, 0.01, SOURCE, color="grey", fontsize=8)
    fig.savefig(path, dpi=150)
    plt.close(fig)
