laps per step
all laps: dropped 0, remaining 1113
lap 1, standing start skews the time: dropped 22, remaining 1091
in or out lap: dropped 102, remaining 989
non-green track status: dropped 165, remaining 824
deleted lap: dropped 0, remaining 824
slower than 107% of fastest lap: dropped 61, remaining 763
missing laptime or compound: dropped 0, remaining 763
stint under 5 clean laps: dropped 8, remaining 755
compound with under 5 clean stints: dropped 10, remaining 745

baseline slope per compound (s per lap, bootstrap over stints)
        n_stints  mean_slope  ci_low  ci_high
HARD      21.000       0.061   0.036    0.091
MEDIUM    24.000       0.040   0.024    0.056

held-out stint error (s per lap)
          base_err  mixed_err
Compound                     
HARD         0.602      0.634
MEDIUM       0.411      0.415
all          0.493      0.509

fuel sensitivity
 fuel_effect Compound  mean_slope  ci_low  ci_high
       0.020     HARD       0.047   0.022    0.077
       0.020   MEDIUM       0.026   0.011    0.043
       0.030     HARD       0.061   0.036    0.091
       0.030   MEDIUM       0.040   0.024    0.056
       0.040     HARD       0.074   0.049    0.104
       0.040   MEDIUM       0.053   0.038    0.070
