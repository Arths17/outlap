# outlap

I wanted to see how much time a tire loses per lap once fuel burn is removed. I used the 2026 British Grand Prix because it was dry and 17 of 22 drivers ran three stints.

## data and cleaning

Everything comes from FastF1 (live timing), loaded through a local cache. The race has 1,113 laps. I drop lap 1, in and out laps, any lap with a non-green track status code, deleted laps, laps slower than 107 percent of the fastest lap, and stints with fewer than 5 clean laps. That leaves 755 laps. The soft compound then has a single stint of 10 laps, which is too little for a slope or an interval, so I drop it too and model mediums and hards only. 745 laps remain. `data_quality.md` lists every dropped lap with its reason, per driver.

The race had a lot of safety car and yellow running. 165 laps went for track status alone, so most stints are shorter than a normal strategy would give.

Lap times are fuel-corrected as lap time plus 0.03 s per kg times the fuel already burned. I assume a 70 kg start load and a linear burn over 52 laps. The 70 kg figure comes from secondary sources on the 2026 rules (planetf1, f1chronicle), and I did not check it against the FIA document. The 0.03 s per kg comes from analyses of the heavier 2025 cars and may be off for these cars. That is why the fuel effect is a parameter in `config.py` and the results are repeated at 0.02 and 0.04 below. Tire age is my own count of laps since the stint began, because FastF1's TyreLife includes laps from earlier sessions on used sets.

## baseline

For each driver-stint I fit a straight line of fuel-corrected lap time against tire age. The mean slope per compound, with a 95 percent bootstrap interval that resamples whole stints:

- medium: about 0.040 s per lap, interval 0.024 to 0.056, from 24 stints
- hard: about 0.061 s per lap, interval 0.036 to 0.091, from 21 stints

The two intervals overlap, so I would not say hards degrade faster. Hard stints also come later in the race, when the track has changed and the field is more spread out, and I do not model either.

Changing the fuel effect moves the slopes directly. At 0.02 s per kg the medium slope is 0.026 and the hard slope is 0.047. At 0.04 it is 0.053 and 0.074. Every 0.01 s per kg shifts both slopes by about 0.014 s per lap, so the fuel assumption moves the result by more than half the gap between the two compounds.

## improved model

I fit a mixed-effects model with compound, compound-specific tire age and track temperature as fixed effects and a random intercept per stint. I chose it because laps inside a stint are not independent and there are only 45 stints. Both models are scored on held-out stints with 5-fold grouped cross-validation, so no stint appears in training and test. For each held-out stint the first 3 laps set its level and the remaining laps are predicted. That gives 678 scored laps.

Mean absolute error in seconds per lap, baseline against mixed model:

- medium: 0.411 against 0.415
- hard: 0.602 against 0.634
- all: 0.493 against 0.509

The mixed model did not beat the baseline. Track temperature barely moved during the race (37.5 to 43.8 degrees C), so it has little to add. I keep the baseline as the headline number.

## what I would not trust

Traffic and DRS trains are not modeled, which likely inflates the scatter for midfield cars. The scatter plot shows fuel-corrected times rising by about 1 s over the first 12 laps of a stint for both compounds, which is steeper than the linear slopes suggest. I did not test why. Bunching after safety car restarts is my guess. The hard LOWESS curve above 25 laps of age rests on a handful of laps and I would not read it. The error of about 0.5 s per lap is larger than the degradation signal of 0.04 to 0.06 s per lap, so the per-lap predictions say little about tire wear. One race also cannot tell me whether any of this holds at other circuits.

## figures

`figures/degradation_scatter.png`, `figures/stint_view.png` and `figures/error_comparison.png`.

## reproduce

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m src.run
.venv/bin/python -m pytest
```

`src.run` downloads the race on first use, writes `data_quality.md`, `results.md` and the figures. Every number above is in `results.md`.
