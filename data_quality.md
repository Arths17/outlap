# data quality

2026 British Grand Prix, race. Every dropped lap and why.

## laps remaining after each step

| step | dropped | remaining |
|---|---|---|
| all laps | 0 | 1113 |
| lap 1, standing start skews the time | 22 | 1091 |
| in or out lap | 102 | 989 |
| non-green track status | 165 | 824 |
| deleted lap | 0 | 824 |
| slower than 107% of fastest lap | 61 | 763 |
| missing laptime or compound | 0 | 763 |
| stint under 5 clean laps | 8 | 755 |
| compound with under 5 clean stints | 10 | 745 |

## dropped laps per driver and reason

```
drop_reason  compound with under 5 clean stints  in or out lap  lap 1, standing start skews the time  non-green track status  slower than 107% of fastest lap  stint under 5 clean laps
Driver                                                                                                                                                                                 
ALB                                          10             10                                     1                       2                                3                         3
ALO                                           0              4                                     1                       8                               23                         0
ANT                                           0              6                                     1                      10                                0                         4
BEA                                           0              4                                     1                       9                                1                         0
BOR                                           0              4                                     1                       9                                0                         0
BOT                                           0              4                                     1                       9                                7                         0
COL                                           0              4                                     1                       8                                0                         0
GAS                                           0              4                                     1                       9                                0                         0
HAD                                           0              6                                     1                       7                                0                         0
HAM                                           0              4                                     1                       8                                0                         0
HUL                                           0              4                                     1                       3                                0                         1
LAW                                           0              4                                     1                       8                                0                         0
LEC                                           0              4                                     1                       7                                0                         0
LIN                                           0              4                                     1                       9                                0                         0
NOR                                           0              6                                     1                       6                                0                         0
OCO                                           0              4                                     1                       8                                0                         0
PER                                           0              4                                     1                       8                                2                         0
PIA                                           0              6                                     1                       7                                0                         0
RUS                                           0              4                                     1                      10                                0                         0
SAI                                           0              4                                     1                       8                                0                         0
STR                                           0              4                                     1                       9                               25                         0
VER                                           0              4                                     1                       3                                0                         0
```

## stints excluded for being too short

- ALB stint 4: 10 clean laps
- ALB stint 5: 2 clean laps
- ALB stint 6: 1 clean laps
- ANT stint 2: 2 clean laps
- ANT stint 4: 2 clean laps
- HUL stint 3: 1 clean laps
