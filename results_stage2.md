feature ablation, 610 held-out laps scored
change is the mean error change versus stage 1 mixed, interval is a bootstrap over stints

                         model   mae  change               ci
baseline (compound mean slope) 0.435     NaN             None
                 stage 1 mixed 0.445     NaN             None
                       + speed 0.438  -0.007 -0.019 to +0.005
                     + braking 0.438  -0.010 -0.024 to +0.006
                     + corners 0.447   0.002 -0.002 to +0.006
                  + lift_coast 0.445   0.001 -0.001 to +0.003
                       + gears 0.446   0.002 -0.004 to +0.008
                  + all groups 0.428  -0.016 -0.039 to +0.006

top_speed vs SpeedST over 1095 laps: correlation 0.58, mean gap 11.4 km/h
