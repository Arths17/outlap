# features

All features are per driver per lap from FastF1 car telemetry. Distance is integrated one lap at a time. The car data arrives at roughly 4 samples per second, which is about 17 to 20 m between samples at 300 km/h, so every distance below is good to about one sample.

- **top_speed**: highest speed on the lap, in km/h. An engineer cares because it shows straight-line deployment and drag. It is the maximum over the lap, not a fixed point on the main straight, and it correlates only 0.58 with the SpeedST speed trap value over 1,095 laps, with a mean gap of 11.4 km/h.
- **full_throttle_frac**: share of lap time at 99 percent throttle or more, with the 104 error value masked. It shows how much of the lap the driver can use the power. It is time weighted, so slow laps with traffic score lower without any driver reason.
- **n_brake_zones**: number of separate runs of Brake on. It shows how many corners needed the brakes. A single stab of one sample counts as a zone, so a lift-and-tap can add one.
- **brake_time_s**: seconds with Brake on. It shows how long the car spends braking. Brake is a boolean in the public data, so it cannot show brake pressure or how hard the stop was.
- **mean_brake_onset_m**: mean metres from brake onset to the corner, over corners that have a braking zone ending near the apex. Later onset means a higher entry speed. Corners 10 and 11, and 16 and 17, are under 90 m apart and share a zone, so their onsets are not independent.
- **mean_apex_speed**: mean over corners of the minimum speed within 75 m of the corner position from FastF1 circuit info. It shows how much speed is carried through the corners. For the same close pairs the windows overlap.
- **mean_throttle_pickup_m**: mean metres from the apex to the first sample above 50 percent throttle, searched up to 500 m. It shows how early the driver gets back on the power. Flat-out corners give 0 and pull the mean down.
- **lift_coast_m**: metres of stretches over 20 m with throttle below 99 percent and no brake, ending directly in a braking zone. It shows energy saving or fuel saving before a stop. With about 17 m between samples, a 20 m threshold is one or two samples, and partial throttle between two close corners is counted too.
- **shift_count**: number of gear changes. It shows how busy the lap was and flags missed or extra shifts. A single driver error can add two or three.
- **mean_apex_gear**: mean gear at the apexes. It shows gearing choice per corner. It is an average of integers over 18 corners, so it moves in steps of about 0.06.

In the race model these are used as the previous lap's values (`prev_` columns), so nothing is computed from the lap being predicted.
