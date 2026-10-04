import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.model_selection import GroupKFold
from statsmodels.nonparametric.smoothers_lowess import lowess

import config
from src.clean import fuel_corrected

CALIBRATION_LAPS = 3  # first laps of a held-out stint used to set its level


def stint_slopes(green_laps):
    # one ols line per driver-stint, slope is seconds lost per lap of tyre age
    rows = []
    for (driver, stint, compound), g in green_laps.groupby(["Driver", "Stint", "Compound"]):
        slope, intercept = np.polyfit(g["stint_age"], g["fuel_corrected_laptime"], 1)
        rows.append(dict(Driver=driver, Stint=int(stint), Compound=compound,
                         n_laps=len(g), slope=slope, intercept=intercept))
    return pd.DataFrame(rows)


def bootstrap_mean_slope(slopes, n_boot=5000, seed=0):
    # resample whole stints, laps inside a stint are not independent
    rng = np.random.default_rng(seed)
    out = {}
    for compound, g in slopes.groupby("Compound"):
        s = g["slope"].to_numpy()
        boots = rng.choice(s, size=(n_boot, len(s))).mean(axis=1)
        out[compound] = dict(n_stints=len(s), mean_slope=s.mean(),
                             ci_low=np.percentile(boots, 2.5), ci_high=np.percentile(boots, 97.5))
    return pd.DataFrame(out).T


def pooled_lowess(green_laps, frac=0.5):
    curves = {}
    for compound, g in green_laps.groupby("Compound"):
        curves[compound] = lowess(g["fuel_corrected_laptime"], g["stint_age"], frac=frac)
    return curves


def _stint_id(laps):
    return laps["Driver"] + "_" + laps["Stint"].astype(int).astype(str)


def _recentre(pred, held, calibration_laps=CALIBRATION_LAPS):
    # shift predictions so they match the stint's first clean laps, the level differs per stint
    # (counted over clean laps: a stint can lose its first laps to the pit lane or a safety car)
    order = held.sort_values("LapNumber").groupby("stint").cumcount().reindex(held.index)
    early = order < calibration_laps
    offset = (held.loc[early, "fuel_corrected_laptime"] - pred[early]).groupby(held.loc[early, "stint"]).mean()
    return pred + held["stint"].map(offset).to_numpy(), ~early


def heldout_errors(green_laps, feature_sets, n_splits=5):
    """baseline plus one mixed model per entry of feature_sets, all on the same stint folds"""
    laps = green_laps.assign(stint=_stint_id(green_laps)).reset_index(drop=True)
    rows = []
    for train_idx, test_idx in GroupKFold(n_splits=n_splits).split(laps, groups=laps["stint"]):
        train, test = laps.iloc[train_idx], laps.iloc[test_idx].copy()

        # baseline: mean ols slope per compound, applied from the stint's early level
        train_slopes = stint_slopes(train.assign(Stint=train["stint"].factorize()[0]))
        mean_slope = train_slopes.groupby("Compound")["slope"].mean()
        base_pred = test["Compound"].map(mean_slope).to_numpy() * test["stint_age"].to_numpy()
        base_pred, later = _recentre(pd.Series(base_pred, index=test.index), test)

        out = pd.DataFrame(dict(
            stint=test["stint"], Compound=test["Compound"],
            base_err=(base_pred - test["fuel_corrected_laptime"]).abs()))
        for name, extra in feature_sets.items():
            terms = "".join(f" + standardize({c})" for c in extra)
            fit = smf.mixedlm(f"fuel_corrected_laptime ~ C(Compound) + stint_age:C(Compound) + TrackTemp{terms}",
                              train, groups=train["stint"]).fit(reml=False)
            pred = pd.Series(fit.predict(test).to_numpy(), index=test.index)
            pred, _ = _recentre(pred, test)
            out[name] = (pred - test["fuel_corrected_laptime"]).abs()
        rows.append(out[later])
    return pd.concat(rows)


def paired_difference_ci(errors, column, reference="mixed_err", n_boot=5000, seed=0):
    """mean error change versus the reference model, bootstrapped over stints"""
    per_stint = (errors[column] - errors[reference]).groupby(errors["stint"]).mean().to_numpy()
    rng = np.random.default_rng(seed)
    boots = rng.choice(per_stint, size=(n_boot, len(per_stint))).mean(axis=1)
    return per_stint.mean(), np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def summarise_errors(errors):
    cols = [c for c in errors.columns if c.endswith("_err")]
    by_compound = errors.groupby("Compound")[cols].mean()
    by_compound.loc["all"] = errors[cols].mean()
    return by_compound


def fuel_sensitivity(green_laps, total_laps):
    rows = []
    for effect in config.FUEL_EFFECT_SENSITIVITY:
        laps = green_laps.assign(fuel_corrected_laptime=fuel_corrected(green_laps, total_laps, effect))
        ci = bootstrap_mean_slope(stint_slopes(laps))
        for compound, r in ci.iterrows():
            rows.append(dict(fuel_effect=effect, Compound=compound, mean_slope=r["mean_slope"],
                             ci_low=r["ci_low"], ci_high=r["ci_high"]))
    return pd.DataFrame(rows)
